#from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
#from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import uuid
#from pathlib import Path
import json
import urllib.request
import boto3
from sqlalchemy import create_engine
import os
from urllib.parse import urlparse


class Scraper:

    """ This class contains the blueprints for a webscraper

    This class will access a website and gather information
    on different products listed and will store it in a 
    dictionary. The data from the webscraping session will
    be saved as .json file and will also be stored on aws rds.
    Raw data will be stored in aws s3.

    Attributes:
        url : The website that will be webscraped.
        driver: The driver that will be used for webscraping.
    """

    def __init__(self):
        options = Options()
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox") 
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--ignore-certificate-errors')
        # options.add_argument("--disable-setuid-sandbox")
        # options.add_argument('--window-size=1920,1080')
        options.add_argument("window-size=1920,1080")
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
        options.add_argument(f'user-agent={user_agent}') # bypasses
        options.add_argument('--headless') # doesn't bring up the GUI
        # options.add_argument("--start-maximized")
        # options.add_argument("--disable-infobars")
        # options.add_argument("--disable-extensions")
        # options.add_argument("--disable-gpu")
        
        
        self.url = 'https://www.asos.com/men/sale/cat/?cid=8409&nlid=mw|sale|shop+sale+by+product|sale+view+all'
        self.driver = Chrome(ChromeDriverManager().install(), options=options)
        self.driver.get(self.url)
        #self.driver.maximize_window()
        self.counter = 0
        self.product_ID = 0
        self.link_list = []
        self.clothe_dict = {'Clothe_Name': [], 'Price': [], 'URL': [], 'product_id': [], 'UUID4': [] }
        self.img_dict = {'Image': [], 'product_id': [], 'UUID4': []}
        self.s3_client = boto3.client('s3', aws_access_key_id=str(input("Enter Access Key: ")), aws_secret_access_key=str(input("Enter Secret ID: ")))
        self.DATABASE_TYPE = 'postgresql'
        self.DBAPI = 'psycopg2'
        self.ENDPOINT = 'aicoredb.cjfn9z1woyjk.us-east-1.rds.amazonaws.com' # Change it for your AWS endpoint
        self.USER = 'postgres'
        self.PASSWORD = str(input('Database Password: '))
        self.PORT = 5432
        self.DATABASE = 'postgres'
        self.engine = create_engine(f"{self.DATABASE_TYPE}+{self.DBAPI}://{self.USER}:{self.PASSWORD}@{self.ENDPOINT}:{self.PORT}/{self.DATABASE}")


    def cookies(self):

        """Makes the webscraper accept cookies on the website otherwise 
        if cookies do not appear then it prints 'cookies are not 
        found'."""

        try:
            time.sleep(2)
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')))
            self.driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]').click()
        except TimeoutException:
            #self.driver.get_screenshot_as_file("screenshot.png")
            print("Cookies not found")


    def clothe_container(self):

        """Makes the webscraper find the container with all the products
           and then stores the links for all the products in a list. The
           number of links (item of clothing) are then printed."""

        clothes = self.driver.find_element(By.XPATH, '//*[@id="plp"]/div/div[1]/div[2]/div/div[1]/section')
        clothe_list = clothes.find_elements(By.XPATH, './article')

        for clothe in clothe_list:
            a_tag = clothe.find_element(by = By.TAG_NAME, value = 'a')
            link = a_tag.get_attribute('href')
            self.link_list.append(link)

        print(f'There are {len(self.link_list)} clothes in this page')
        return self.link_list


    def make_dict(self):

        """The webscraper then checks out the links in the list and 
           stores information about these products in a dictionary. The 
           information stored are the names, price, picture, URL, product ID for 
           the clothes. A UUID4 is also generated for each item of clothing.
           Image data is also installed into folders and uploaded to s3."""

        for i in self.link_list:
            self.driver.get(i)
            time.sleep(2)
            

            parse_object = urlparse(i)
            object0 = parse_object.path
            integers_in_list = [int(s) for s in str(object0) if s.isdigit()]
            self.product_ID = ''.join(str(e) for e in integers_in_list)

            newpath = f'raw_data/{self.product_ID}' 

            cur = self.engine.execute(f"SELECT * FROM asos_dataset WHERE product_id='{self.product_ID}'")

            if i not in self.clothe_dict and not cur.fetchone():

                self.clothe_dict['URL'].append(str(i))

                unique = uuid.uuid4()
                self.clothe_dict['UUID4'].append(str(unique))
                

                try: 
                    #WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="product-details-container"]/div[2]/div[1]')))
                    #self.product_ID = self.driver.find_element(By.XPATH, '//*[@id="product-details-container"]/div[2]/div[1]/p').text
                    #unq = self.driver.find_element(By.XPATH, '//*[@id="product-details-container"]/div[2]/div[1]')
                    #self.product_ID = unq.find_element(by = By.TAG_NAME, value = 'p').text
                    # Unique_ID = Unique_I.get_attribute('<p>').text
                    
                    self.clothe_dict['product_id'].append(self.product_ID)
                except NoSuchElementException:
                    self.clothe_dict['product_id'].append('N/A')
                    #self.img_dict['Image'].append('N/A')

                try:
                    #WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="aside-content"]/div[1]/h1')))
                    Clothe_name = self.driver.find_element(By.XPATH, '//*[@id="aside-content"]/div[1]/h1').text
                    self.clothe_dict['Clothe_Name'].append(str(Clothe_name))
                except NoSuchElementException:
                    self.clothe_dict['Clothe_Name'].append('N/A')

                try:
                    #WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/main/div[2]/section[1]/div/div[2]/div[2]/div[1]/div[1]/div[1]/span[2]/span[4]/span[1]')))
                    Price = self.driver.find_element(By.XPATH, '/html/body/div[1]/div/main/div[2]/section[1]/div/div[2]/div[2]/div[1]/div[1]/div[1]/span[2]/span[4]/span[1]').text
                    real_price = Price[4:]
                    self.clothe_dict['Price'].append(str(real_price))
                except NoSuchElementException:
                    self.clothe_dict['Price'].append('N/A')

                try:
                    # find_pic = self.driver.find_element(By.XPATH, '//*[@id="product-gallery"]/div[2]/div[2]/div[2]')
                    # pics = find_pic.find_elements(By.XPATH, './div')
                    find_pic = self.driver.find_element(By.XPATH, '//*[@id="product-gallery"]/div[2]/div[2]')
                    pics = find_pic.find_elements(By.XPATH, './div')
                    for x in pics:
                        img_tag = x.find_element(by = By.TAG_NAME, value = 'img')
                        img = img_tag.get_attribute('src')
                        if not os.path.exists(newpath):
                            os.makedirs(newpath)
                        urllib.request.urlretrieve(img, f'{newpath}/{pics.index(x)}.jpg')
                        upload_img = self.s3_client.upload_file(f'{newpath}/{pics.index(x)}.jpg', 'webscraperprojectbucket', 'clothe_images')
                        self.img_dict['Image'].append(str(img))
                        self.img_dict['product_id'].append(self.product_ID)
                        self.img_dict['UUID4'].append(str(unique))
                except NoSuchElementException:
                    self.img_dict['Image'].append('N/A')
                    self.img_dict['product_id'].append('N/A')

                self.counter +=1

            else:
                pass

        print(self.clothe_dict)
        print(self.img_dict)
        print(f'counter: {self.counter}')
        return self.clothe_dict

    def make_json(self):

        """The information from the dictionaries is then stored in
        dataframes. Product info is stored in a json file. The data is then 
        stored in s3. The dataframes are also uploaded to postgresql. 
        The browser is then closed after completion."""

        df = pd.DataFrame.from_dict(self.clothe_dict, orient = 'index')
        img = pd.DataFrame.from_dict(self.img_dict, orient = 'index')
        df = df.transpose()
        img = img.transpose()
        with open('raw_data/data.json', 'w') as fp:
            json.dump(self.clothe_dict, fp, indent = 4)

        response = self.s3_client.upload_file('raw_data/data.json', 'webscraperprojectbucket', 'webscraperdata')
        df.to_sql('asos_dataset', self.engine , if_exists='append')
        img.to_sql('asos_images', self.engine, if_exists='append')

        self.driver.quit() # Close the browser when you finish


if __name__ == "__main__": #it only runs if this file is run directly rather than on any import 
    bot = Scraper()
    bot.cookies()
    bot.clothe_container()
    bot.make_dict()
    bot.make_json()