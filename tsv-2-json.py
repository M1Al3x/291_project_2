import json
from pymongo import MongoClient

def transfromjson(filename):
    arr = []
    input_filename = filename + '.tsv'
    
    with open(input_filename, encoding="utf-8") as inp_file:
        a = inp_file.readline()  
        titles = [t.strip() for t in a.split('\t')]
        for line in inp_file:
            d = {}
            for t, f in zip(titles, line.split('\t')):
                if ',' in f:
                    f = f.strip()
                    f = f.split(',')
                    d[t] = f
                  # Convert each row into dictionary with keys as titles
                else: 
                    d[t] = f.strip()
                     
            # we will use strip to remove '\n'.
            arr.append(d)    
    
    output_filename = filename + '.json'
    with open(output_filename, 'w', encoding='utf-8') as out_file:
        for element in arr:
            json.dump(element, out_file)

def change_file():
    
    input_filename1 = 'name.basics' 
    input_filename2 = 'title.basics'
    input_filename3 = 'title.principals'
    input_filename4 = 'title.ratings'
    file_names = [input_filename1, input_filename2, input_filename3, input_filename4]
    
    for name in file_names:
        transfromjson(name)
        
change_file()
