from parsing.menu_parsing import menu_extract
from parsing.product_parsing import *

import logging

all_category = menu_extract("https://www.glamira.com/sitemap/")
#print(all_category)
for cate in all_category:
    #product_info = get_infor(cate)
    get_product(cate)