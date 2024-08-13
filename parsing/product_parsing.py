import sys

from bs4 import BeautifulSoup
import requests
import urllib
import logging
import time
import os
import mysql.connector
from decimal import Decimal

logger = logging.getLogger()

class product_info:
    def __init__(self, category, prod_name, prod_id,prod_link, prod_imgs,price, prod_desc,path_img, url,total_page,total_prod):
        self.category = category
        self.prod_name = prod_name
        self.prod_id = prod_id
        self.prod_link = prod_link
        self.prod_imgs = prod_imgs
        self.price = price
        self.prod_desc = prod_desc
        self.path_img = path_img
        self.url = url
        self.total_page = total_page
        self.total_prod = total_prod
def get_total_page_product(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    products = soup.select_one('ol.products.list.items.product-items li')
    total_page = int(products.get('data-lastpage'))
    total_product = int(products.get('data-total-items'))
    return total_page, total_product

def get_infor(url):
    response = requests.get(url)
    if response and response.status_code == 200:
        logging.info("Request Success url: %s", url)
        soup = BeautifulSoup(response.content, 'html.parser')
        product_items = soup.find("ol", class_="products list items product-items")
        list_product_name = [element.text.strip() for element in
                             product_items.find_all('h2', class_='product-item-details product-name')]
        list_product_image = [element.get('src') for element in
                              product_items.find_all('img', class_='product-image-photo')]
        list_product_price = [element.text.strip() for element in product_items.find_all('span', class_='price')]
        list_product_link = [element.get('href') for element in product_items.find_all('a', class_='product-link')]
        list_product_desc = [element.text.strip() for element in
                             product_items.find_all('span', class_='short-description')]
        list_product_id = [element.get('data-product-id') for element in
                           product_items.find_all('div', class_='price-box price-final_price')]
        return list(
            zip(list_product_name, list_product_image, list_product_desc, list_product_price, list_product_link,list_product_id)) #merge list product name and list product image
    else:
        logging.warning("Request Failed url:%s", url)
        return [(None, None)]
def get_product(urlCate):
    tuple_data = []
    tuple_data_page = []
    logging.info("---------------------------------------------------")
    logging.info(f"START SCRAP URL: {urlCate} ")
    total_page, total_product = get_total_page_product(urlCate)
    image_path = os.path.join(os.getcwd(), 'data', 'image')
    if total_page and total_product:
        urls = [urlCate + f'?p={i}' if i > 1 else urlCate for i in range(1, total_page + 1)]
        for url in urls:
            data_page = get_infor(url)
            for data in data_page:
                #print(data)
                images_dowload = [(data[1],data[5])]
                #print(images_dowload)
                path_img = crawl_image(image_path,images_dowload)
                product_data = product_info(urlCate,data[0],int(data[5]),data[4],data[1],data[3],data[2],path_img,url,int(total_page),int(total_product))
                tuple_data = tuple([
                    product_data.category,
                    product_data.prod_id,
                    product_data.prod_name,
                    product_data.price,
                    product_data.prod_link,
                    product_data.prod_desc,
                    product_data.prod_imgs,
                    product_data.path_img,
                    product_data.url,
                    product_data.total_page,
                    product_data.total_prod
                ])
                insert_data(tuple_data)
def crawl_image(image_path, prod_img_urls=None):
    if not os.path.exists(image_path):
        os.makedirs(image_path)
    for link,prod_id in prod_img_urls:
        path_img_saved = download_image(prod_id,link,image_path)
    return path_img_saved
def download_image(prod_id, link, product_image_folder):
    save_path = os.path.join(product_image_folder, prod_id+".jpg")
    response = requests.get(link)
    if response and response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
    print(save_path)
    logger.info(f"Downloaded {save_path}")
    return save_path

def insert_data(data):
    try:
        # Kết nối tới MySQL
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="password",
            database="glamira"
        )

        # Kiểm tra kết nối
        if conn.is_connected():
            print("Đã kết nối thành công đến MySQL")

        # Chèn dữ liệu vào bảng
        insert_query = "INSERT INTO product (category,prod_id,prod_name,prod_price,prod_link,prod_desc,prod_imgs,path_img,prod_url,prod_total_page,prod_total_product) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        args = [item for item in data]
        curson = conn.cursor()
        curson.execute(insert_query,args)
        # Lưu thay đổi vào cơ sở dữ liệu
        conn.commit()
        print("Dữ liệu đã được chèn thành công.")
    except Exception as ex:
        print(ex)
        sys.exit(1)
    finally:
        # Đóng con trỏ
        curson.close()
        # Đóng kết nối
        conn.close()
        print("Kết nối đã được đóng.")

