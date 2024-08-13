from bs4 import BeautifulSoup
import requests
import logging

logger = logging.getLogger()

all_list = []

def menu_extract(link):
    response = requests.get(link)
    html = response.text
    bs = BeautifulSoup(html, 'html.parser')
    # extract a list of category
    menu_list = bs.select("div h3 a")
    #print(menu_list)

    for menu in menu_list:
        all_list.append(menu['href'])
    return all_list
# print on when a build done successfully
logger.info("Starting to crawl...")
