import json
from os import path
class Product:
    def __init__(self, category, name, part_number, url, image_url, price):
        self.category = category
        self.name = name
        self.part_number = part_number
        self.url = url
        self.image_url = image_url
        self.price = price
    
    def save(self):
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
