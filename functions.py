from bs4 import BeautifulSoup
import time
import json
from os import path
from models.Product import Product
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By




BASE_URL = "https://www.napaonline.com"
PROGRESS_LIST_PATH = "progress.json"
delay_time_in_s = 3

def get_all_main_products_links(content):
    soup = BeautifulSoup(content, "html.parser")
    for i in range(10):
        try:
            menu_items = soup.find("div",{"class":"geo-mega-menu-wrapper"}).find_all("a",{"class":"geo-mega-menu-item"})
            return [i.get("href") for i in menu_items if "/en/c/" in i.get("href")]
        except:
            time.sleep(delay_time_in_s)


def get_all_categories_links(content):
    soup = BeautifulSoup(content, "html.parser")
    for i in range(10):
        try:
            all_category_pod_link = soup.find("geo-category-container").find_all("a",{"class":"geo-category-pod-link"})
            return [i.get("href") for i in all_category_pod_link]
        except:
            time.sleep(delay_time_in_s)

def get_concrete_categories_links(content):
    soup = BeautifulSoup(content, "html.parser")
    for i in range(10):
        try:
            all_category_pod_link = soup.find("geo-partype-list").find_all("a",{"class":"geo-parttype-list-links"})
            return [i.get("href") for i in all_category_pod_link]
        except:
            time.sleep(delay_time_in_s)


def parse_all_items_of_category(driver, last_item, info):
    time.sleep(delay_time_in_s)
    check_engine = None
    while True:
        try:
            soup = BeautifulSoup(driver.page_source, "html.parser")
            pages_number = round(int(soup.find("geo-pagination-links").get("item-count")) / 24)
            if pages_number == 0:
                pages_number = 1
            break
        except Exception as e:
            print("Can't get pages number", e)
            pages_number = 1
            time.sleep(delay_time_in_s)
            continue
    if last_item is not None:
        stopped_page = last_item[-1] + 1
        last_item = None
    else:
        stopped_page = 1
    while True:
        try:
            soup = BeautifulSoup(driver.page_source,"html.parser")
            url = soup.find("meta", property="og:url").get("content").split("?")[0]
            _get_part_price(soup)
            print("Page is ready!")
            break # it will break from the loop once the specific element will be present. 
        except Exception as e:
            check_engine = soup.find("a",{"class":"know-blog-btn"})
            if  check_engine is not None:
                time.sleep(2)
                driver.refresh()
            print(e, "In parse all items")
            time.sleep(delay_time_in_s)

    # val = _parse_individual_page(driver.page_source)
    if pages_number > 1:
        for page in range(stopped_page, pages_number + 1):
            driver.get(f"{url}?page={page}")
            no_res = None
            check_engine = None
            apache_not_found = None
            for i in range(10):
                try:
                    soup = BeautifulSoup(driver.page_source,"html.parser")
                    _get_part_price(soup)
                    print("Page is ready!")
                    break # it will break from the loop once the specific element will be present. 
                except Exception as e:
                    print(e, "IN PARSING")
                    time.sleep(delay_time_in_s)
                    apache_not_found = soup.find("h1")
                    if apache_not_found is not None and apache_not_found.text == "HTTP Status 404 ??? Not Found":
                        apache_not_found = apache_not_found

                        
                    no_res = soup.find("geo-no-result-page")
                    check_engine = soup.find("a",{"class":"know-blog-btn"})
                    if no_res is not None or check_engine is not None or apache_not_found is not None:
                        break

            if no_res is None and check_engine is None and apache_not_found is None:
                info['page'] = page
                _parse_individual_page(driver, info)
                print(f"PAGE {page} DONE!")
            else:
                try:
                    driver.refresh()
                    time.sleep(delay_time_in_s)
                    info['page'] = page
                    _parse_individual_page(driver, info)
                    print(f"PAGE {page} DONE!")
                except Exception as e:
                    print(f"?????????????? ???????????? ???? ???????????????? {page} - ", e)
                    continue
        

def _parse_individual_page(driver, info):
    category = None
    first_soup = BeautifulSoup(driver.page_source, "html.parser")
    for i in range(10):
        try:
            first_soup = BeautifulSoup(driver.page_source, "html.parser")
            category = _get_category_path(first_soup)
            break
        except Exception as e:
            print(e)
            pass
    print(f"Parsing {category}")
    for item in  _get_all_elements_on_page(driver):
        if item is not None:
            soup  = BeautifulSoup(str(item), "html.parser")
            price = None
            
            name = _get_part_name(soup)
            number = _get_part_number(soup)
            url = _get_part_url(soup)
            image_url = _get_part_image_url(soup)
            
            for i in range(10):
                try:
                    price = _get_part_price(soup)
                    break
                except Exception as e:
                    print(e)
                    time.sleep(delay_time_in_s)
                    pass
            if price is None:
                print("?????? ???????? ???? ?????????? ???? ????????????????, ???????????????????????? ????????????????")
                driver.refresh()
                time.sleep(3)
                _parse_individual_page(driver, info)
            product = Product(
                year = info['year'],
                make = info['make'],
                model = info['model'],
                category = category,
                name = name,
                part_number = number,
                url = url,
                image_url = image_url,
                price = price,
                main_category = info['main_category'],
                category_0 = info['category_0'],
                category_1 = info['category_1'],
                category_2 = info['category_2'],
                page = info['page']
            )
            product.save()

def _get_all_elements_on_page(driver):
    time.sleep(2)
    for i in range(10):
        try:
            soup = BeautifulSoup(driver.page_source, "html.parser")
            return soup.find("geo-search-results",{"class":"hydrated"}).find_all("geo-product-list-item")
        except:
            print("Error on get_all_elements_on_page ")
            time.sleep(delay_time_in_s)
    return []

def _get_category_path(soup=BeautifulSoup):
    return "/".join([i.text for i in soup.find("geo-breadcrumb-links",{"class":"hydrated"}).find_all("span")]) 


def _get_part_name(soup=BeautifulSoup):
    return soup.find("div",{"class":"geo-pod-title geo-productpod-top"}).text


def _get_part_number(soup=BeautifulSoup):
    return soup.find("div", {"class":"geo-pod-normal-text product-review"}).get('data-bv-product-id')


def _get_part_url(soup=BeautifulSoup):
    return BASE_URL + soup.find("div",{"class":"geo-pod-title geo-productpod-top"}).find("a").get("href")


def _get_part_image_url(soup=BeautifulSoup):
    url = soup.find("img").get("src")
    if "data:image" in url:
        return "NO IMAGE FOUND"
    else:
        return url


def _get_part_price(soup=BeautifulSoup):
    if soup.find("div", {"class": "geo-no-priceavailable"}) is not None:
        return "Not available"
    return soup.find("div",{"class":"geo-pod-price-cost"}).text.replace('$','').replace("/ Each", "")



def save_parsed_categories(category):
    if path.isfile(PROGRESS_LIST_PATH):
        db = json.load(open(PROGRESS_LIST_PATH, encoding="utf8"))
        db.append(category)
        with open(PROGRESS_LIST_PATH, "w") as f:
            json.dump(db, f, indent=2)
    else:
        with open(PROGRESS_LIST_PATH, "w") as f:
            json.dump([], f, indent=2)
        
        db = json.load(open(PROGRESS_LIST_PATH, encoding="utf8"))
        db.append(category)
        with open(PROGRESS_LIST_PATH, "w") as f:
            json.dump(db, f, indent=2)
