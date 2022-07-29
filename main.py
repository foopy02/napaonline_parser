from bs4 import BeautifulSoup
import requests
from requests.models import Response
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import undetected_chromedriver as uc
from fake_useragent import UserAgent
from selenium.webdriver import ActionChains
from functions import *
import sqlite3
import pprint
import os
import sys
from selenium.webdriver import DesiredCapabilities
BASE_URL = "https://www.napaonline.com"


def create_db():
    conn = sqlite3.connect('cars.db')
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS cars(
       id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
       year TEXT,
       make TEXT,
       model TEXT);
    """)
    conn.commit()
    conn = sqlite3.connect('items.db')
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS items(
           id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
           year TEXT NOT NULL,
           make TEXT NOT NULL,
           model TEXT NOT NULL,
           category TEXT NOT NULL,
           name TEXT NOT NULL,
           number TEXT NOT NULL,
           url TEXT NOT NULL,
           image_url TEXT NOT NULL,
           price TEXT NOT NULL,
           main_category TEXT NOT NULL,
           category_0 TEXT NOT NULL,
           category_1 TEXT NOT NULL,
           category_2 TEXT NOT NULL,
           page INTEGER NOT NULL);
        """)
    conn.commit()


def main():
    create_db_flag = True

    if create_db_flag == True:
        create_db()
    conn_cars = sqlite3.connect('cars.db')
    cur_cars = conn_cars.cursor()
    try:
        year=sys.argv[0] 
        make=sys.argv[1]
        model=sys.argv[2]
    except:
        year, make, model = "2015", "Ford", "1_28_14_2015"
    options = Options()
    # make chrome log requests
    capabilities = DesiredCapabilities.CHROME

    # capabilities["loggingPrefs"] = {"performance": "ALL"}  # chromedriver < ~75
    capabilities["goog:loggingPrefs"] = {"performance": "ALL"}  # chromedriver 75+
    driver = uc.Chrome(driver_executable_path=f"{os.path.dirname(__file__)}/chromedriver", options=options,desired_capabilities=capabilities)
    #TEST

    # driver.get("https://www.napaonline.com/en/search/oil-and-chemicals/additives/automotive-additives/cooling-system-additive/201805113")
    # time.sleep(10)
    # logs_raw = driver.get_log("performance")
    # logs = [json.loads(lr["message"])["message"] for lr in logs_raw]

    # def log_filter(log_):
    #     return (
    #         # is an actual response
    #         log_["method"] == "Network.responseReceived"
    #         # and json
    #         and "json" in log_["params"]["response"]["mimeType"]
    #     )

    # for log in filter(log_filter, logs):
    #     request_id = log["params"]["requestId"]
    #     resp_url = log["params"]["response"]["url"]
    #     print(type(resp_url))

    #     if "https://www.napaonline.com/api/search/core/?site=us"  in resp_url:
    #         r = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
    #         try:
    #             response_real = json.loads(r['body'])
    #             pprint.pprint(response_real)
    #         except Exception as e:
    #             print(e)

    # Adding pause to not get the WebDriverException
    time.sleep(2)
    while True:
        try:
            get_main_url(driver=driver)
            if cur_cars.execute('SELECT id FROM cars WHERE year = ? and make = ? and model = ?', (year, make, model)).fetchone() is None:
                try:
                    select_auto(year=sys.argv[0], make=sys.argv[1], model=sys.argv[2], driver=driver)
                except:
                    select_auto(year=year, make=make, model=model, driver=driver)
            break
        except Exception as e:
            print("Error with getting base url", e)
            time.sleep(3)
            continue


    conn_items = sqlite3.connect('items.db')
    cur_items = conn_items.cursor()
    last_item = cur_items.execute(
        'SELECT * FROM items WHERE year = ? and make = ? and model = ? ORDER BY id DESC LIMIT 1',
        (year, make, model)).fetchone()
    
    main_categories = get_all_main_products_links(driver.page_source) #Например Replacement Parts

    print(f"Main categories {main_categories}")
    if last_item is not None:
        try:
            main_categories = main_categories[main_categories.index(last_item[-5]):]
        except Exception as e:
            print(f"Проблема с main category. Начинаем тогда все с {main_categories[0]}" + e)

    for i in main_categories:
        driver.get(f'{BASE_URL}/{i}')

        try:
            myElem = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'geo-category-container')))
        except TimeoutException:
            print("Loading took too much time!")
       

        categories = get_all_categories_links(driver.page_source) #Например Air Brakes
        print(f"Categories {categories}")

        if categories is None:
            refresh_until_appears(categories, driver)

        if last_item is not None:
            try:
                categories = categories[categories.index(last_item[-4]):]
            except Exception as e:
                print(f"Проблема с category. Начинаем тогда все с {categories[0]}" + e)

        for category in categories:

            driver.get(f'{BASE_URL}/{category}')
            sub_categories = get_all_categories_links(driver.page_source)

            if sub_categories is None:
                refresh_until_appears(sub_categories, driver)

            print(f"Sub_categories {sub_categories}")

            if last_item is not None:
                try:
                    sub_categories = sub_categories[sub_categories.index(last_item[-3]):]
                except Exception as e:
                    print(f"Проблема с subcategory. Начинаем тогда все с {sub_categories[0]}" + e)
            for subcategory in sub_categories:

                driver.get(f'{BASE_URL}/{subcategory}')
                
                try:
                    myElem = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'geo-parttype-list')))
                except:
                    print("Loading of subcategory took too much time!")

                concrete_categories = get_concrete_categories_links(driver.page_source)
                print(f"concrete_categories {concrete_categories}")
                while concrete_categories is None:
                    driver.refresh()
                    time.sleep(5)
                    concrete_categories = get_concrete_categories_links(driver.page_source)

                if last_item is not None:
                    try:
                        concrete_categories = concrete_categories[concrete_categories.index(last_item[-2]):]
                    except Exception as e:
                        print(f"Проблема с concrete_categories. Начинаем тогда все с {concrete_categories[0]}" + e)
                for concrete_category in concrete_categories:
                    driver.get(f'{BASE_URL}/{concrete_category}')
                    info = {
                        'year': year,
                        'make': make,
                        'model': model,
                        'main_category': i,
                        'category_0': category,
                        'category_1': subcategory,
                        'category_2': concrete_category,
                    }
                    parse_all_items_of_category(driver, last_item, info)
            print("GOT PAGE")

def refresh_until_appears(categories, driver) :
    while categories is None:
        driver.refresh()
        time.sleep(5)
        categories = get_all_categories_links(driver.page_source)


def select_auto(year, make, model, driver):
    find_and_press_selection(element_id="vehicleYear-selector",data_value=year, driver=driver)
    time.sleep(1)
    find_and_press_selection(element_id="vehicleMake-selector",data_value=make, driver=driver)
    time.sleep(1)
    find_and_press_selection(element_id="vehicleModel-selector",data_value=model, driver=driver)
    time.sleep(1)
    submit_btn = driver.find_element(By.CLASS_NAME, "geo-add-cancel-vehiclediv").find_element(By.TAG_NAME, "button")
    submit_btn.click()

def find_and_press_selection(element_id, data_value, driver):
    driver.execute_script("""
                    document.getElementById('%s').getElementsByClassName('geo-option-name')[0].click()
                    """ % element_id)
    time.sleep(1)
    print(f"Pressed {data_value}")
    driver.execute_script("""
                document.querySelectorAll('[data-value="%s"]')[0].click()
                """ % data_value)

def get_main_url(driver):
    driver.get(BASE_URL)
    try:
        myElem = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'add-vehicle')))
    except TimeoutException:
        print("Loading took too much time!")
    #Finding button that add vehicle
    while True:
        try:
            add_new_vehicle_btn = driver.find_element(By.ID,"add-vehicle")
            add_new_vehicle_btn.click()
            break

        except Exception as e:
            print("Can't find add-vehicle button", e)
            if driver.find_element(By.CLASS_NAME, "cf-highlight-inverse") is not None:
                get_main_url(driver)
            time.sleep(3)
            continue
        

    time.sleep(3)

if __name__ == "__main__":
    main()