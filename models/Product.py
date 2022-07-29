import json
from os import path
import sqlite3
class Product:
    def __init__(self, year, make, model, category, name, part_number, url, image_url, price, main_category, category_0, category_1, category_2, page):
        self.year = year
        self.make = make
        self.model = model
        self.category = category
        self.name = name
        self.part_number = part_number
        self.url = url
        self.image_url = image_url
        self.price = price
        self.main_category = main_category
        self.category_0 = category_0
        self.category_1 = category_1
        self.category_2 = category_2
        self.page = page
    
    def save(self):
        res_item = [i for i in self.__dict__.values()]
        conn_items = sqlite3.connect('items.db')
        cur_items = conn_items.cursor()
        check_try = cur_items.execute('select id from items where year = ? and make = ? and model = ? and category = ? and name = ? and number = ? and url = ? and image_url = ? and price = ?', res_item[:-5])

        if check_try.fetchone() is None:
            # res_item.extend([categore_0, categore_1, categore_2, n])
            cur_items.execute('''INSERT or ignore INTO items(year, make, model, category, name, number, url, image_url, price, main_category, category_0, category_1, category_2, page) 
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?);''', res_item)
        conn_items.commit()

    def save_last(self):
        PATH = "database.json"
        if path.isfile(PATH):
            db = json.load(open(PATH, encoding="utf8"))
            db.append(self.__dict__)
            with open(PATH, "w") as f:
                json.dump(db, f, indent=2)
        else:
            with open(PATH, "w") as f:
                json.dump([], f, indent=2)
            
            db = json.load(open(PATH, encoding="utf8"))
            db.append(self.__dict__)
            with open(PATH, "w") as f:
                json.dump(db, f, indent=2)

# item = Product(
#     "2015",
#     "Ford",
#     "1_28_14_2015",
#     "categorysome",
#     "2022",
#     "urlsome",
#     "urlsome",
#     "image",
#     "2002",
#     "/en/c/paint-and-body/201056703",
#     "/en/c/paint-and-body/air-compressors-and-accessories/201340332",
#     "/en/c/paint-and-body/air-compressors-and-accessories/air-compressor-accessories/201340349",
#     "/en/search/paint-and-body/air-compressors-and-accessories/air-compressor-accessories/coupler/201805942",
#     1
# )
# item.save()