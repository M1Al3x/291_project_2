import json
from pymongo import MongoClient

def loadall():
    client = MongoClient('mongodb://localhost:27017')
    
    # Create or open a database on the server.
    db = client["291db"]
    
    name_basics_delete = False
    title_basics_delete = False
    title_principals_delete = False
    title_ratings_delete = False
    
    collist = db.list_collection_names()
    # if the collection exists then delete them
    if "name_basics" in collist:
        print("The name_basics collection exists.")
        name_basics_delete = True
    if "title_basics" in collist:
        print("The title_basics collection exists.") 
        title_basics_delete = True
    if "title_principals" in collist:
        print("The title_principals collection exists.") 
        title_principals_delete = True
    if "title_ratings" in collist:
        print("The title_ratings collection exists.")  
        title_ratings_delete = True
    
    # all the collections create or open them
    name_basics = db["name_basics"]
    title_basics = db["title_basics"]
    title_principals = db["title_principals"]
    title_ratings = db["title_ratings"]    
    
    # delete all previous entries in the movies_collection  
    # if the collection exists then delete them
    if name_basics_delete:
        print("The name_basics collection exists so the prevoius data will be deleted")
        name_basics.delete_many({})
    if title_basics_delete:
        print("The title_basics collection exists so the prevoius data will be deleted") 
        title_basics.delete_many({})
    if title_principals_delete:
        print("The title_principals collection exists so the prevoius data will be deleted") 
        title_principals.delete_many({})
    if title_ratings_delete:
        print("The title_ratings collection exists so the prevoius data will be deleted")  
        title_ratings.delete_many({})
        
    # load all the files  
    file_name1 = 'name.basics.json'
    loadone(file_name1, name_basics)
    
    file_name2 = 'title.basics.json'
    loadone(file_name2, title_basics)
    
    file_name3 = 'title.principals.json'
    loadone(file_name3, title_principals)
    
    file_name4 = 'title.ratings.json'
    loadone(file_name4, title_ratings)    

    print("all the data has been succesfully inserted!!")

def loadone(file_name, collection):
    array = []
    with open(file_name) as f:
        temp_string = ''
        data = f.read()
        index = 0
        is_comma = False
        for char in data:
            if char == '}':
                is_comma = True
                # to skip a turn
                temp_string = temp_string + '}'
                collection.insert_one(json.loads(temp_string))
                temp_string = ''   
            else:
                temp_string = temp_string + char                
                
def main():
    loadall()
main()

