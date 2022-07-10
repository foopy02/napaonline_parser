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

BASE_URL = "https://www.napaonline.com"

def main():
    options = Options()
    driver = uc.Chrome(driver_executable_path="C://Users//Адиль//Desktop//parser_job//chromedriver", options=options)

    # Adding pause to not get the WebDriverException
    time.sleep(2)
    driver.get(BASE_URL)
    try:
        myElem = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, 'add-vehicle')))
    except TimeoutException:
        print("Loading took too much time!")
    #Finding button that add vehicle
    while True:
        try:
            add_new_vehicle_btn = driver.find_element_by_id("add-vehicle")
            add_new_vehicle_btn.click()
            break
        except:
            print("Can't find add-vehicle button")
            continue
        

    time.sleep(3)

    select_auto(year=2015, make="Ford", model="1_28_14_2015", driver=driver)


    for i in get_all_main_products_links(driver.page_source):
        driver.get(f'{BASE_URL}/{i}')

        try:
            myElem = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'geo-category-container')))
        except TimeoutException:
            print("Loading took too much time!")
       

        categories = get_all_categories_links(driver.page_source)
        for category in categories:

            driver.get(f'{BASE_URL}/{category}')
            sub_categories = get_all_categories_links(driver.page_source)

            for subcategory in sub_categories:

                driver.get(f'{BASE_URL}/{subcategory}')
                
                try:
                    myElem = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'geo-parttype-list')))
                except:
                    print("Loading of subcategory took too much time!")

                concrete_categories = get_concrete_categories_links(driver.page_source)
                
                for concrete_category in concrete_categories:
                    driver.get(f'{BASE_URL}/{concrete_category}')
                    time.sleep(12)
                    parse_all_items_of_category(driver.page_source, driver)
            print("GOT PAGE")

    
def select_auto(year, make, model, driver):
    find_and_press_selection(element_id="vehicleYear-selector",data_value=year, driver=driver)
    time.sleep(1)
    find_and_press_selection(element_id="vehicleMake-selector",data_value=make, driver=driver)
    time.sleep(1)
    find_and_press_selection(element_id="vehicleModel-selector",data_value=model, driver=driver)
    time.sleep(1)
    submit_btn = driver.find_element_by_class_name("geo-add-cancel-vehiclediv").find_element_by_tag_name("button")
    submit_btn.click()

def find_and_press_selection(element_id, data_value, driver):
    select_of = driver.find_element_by_id(element_id).find_element_by_tag_name("div")
    select_of.click()
    selection_of_concrete = driver.find_element_by_xpath(f"//*[@data-value='{data_value}']")
    selection_of_concrete.click()

if __name__ == "__main__":
    main()