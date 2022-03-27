import json
import pymongo
from pymongo import MongoClient

def connect():
    # to connect to client and database
    client = MongoClient('mongodb://localhost:27017')
    
    # Create or open a database on the server.
    db = client["291db"]
    
    # all the collections create or open them
    name_basics = db["name_basics"]
    title_basics = db["title_basics"]
    title_principals = db["title_principals"]
    title_ratings = db["title_ratings"]  
    return name_basics, title_basics, title_principals, title_ratings

def search_movie(title_basics, title_ratings, name_basics, title_principals):
    movies = search_by_key_words(title_basics) 
    print("Movies by the given search: ")
    index = 0
    indexEd = 0
    i = "n"
    indexToCheck = -1
    while(i!="c"):
        if i=="n":
            for movie in movies:
                print(str(index+1), movie)
                index = index+ 1
               
        i = input("In order to view detailed information about movie enter its number.\nIf you want to serach another movie press s. \nif you want to return to homepage enter 'q': ")
        if i=="s":
            movies = search_by_key_words(title_basics) 
            print("Movies by the given search: ")
            index = 0
            indexEd = 0
            i = "n"
            indexToCheck = -1
        if i == 'q':
            # end the loop
            print("you will be returned to the homepage!")
            return
        else:
            while indexEd < index:
                if i == str(indexEd+1):
                    indexToCheck = indexEd
                    i = "c"
                    break
                indexEd = indexEd + 1
        
    if i=="c":
        seeDetailedInfo(movies[indexEd], title_ratings, name_basics, title_principals)
    return

def search_by_key_words(title_basics):
    continue_program = True
    
    # while continue_program:
        
    title_basics.drop_indexes()
    keywords = input("Enter keywords for searching movie: ").split(' ')

    # title_basics.create_index({"$primaryTitle": "text"}, {"$startYear":"text"})  
    title_basics.create_index([("primaryTitle", pymongo.TEXT),
                            ("startYear", pymongo.TEXT)])
    strKeys = ''
    for keyword in keywords:
        strKeys = strKeys + "\"" + keyword + "\""   

    # title_basics.create_index([("startYear", 'text')])
    stages = {"$text": {"$search": strKeys}}
    output_movies = title_basics.find(stages)
    return list(output_movies)

def seeDetailedInfo(movie, title_ratings, name_basics, title_principals):
    inpMovie = ''
    print("\n\nDetailed information for ", movie['primaryTitle'])
    movie_title = movie["primaryTitle"]
    tconst = movie["tconst"]
    output_rating = list(title_ratings.find({"tconst": tconst}))
    print("The rating is: " + str(output_rating[0]["averageRating"]))
    print("The number of votes is: " + str(output_rating[0]["numVotes"]))
    roles = list(title_principals.find({"tconst": tconst}))
    for person in roles:
        nconst = person["nconst"]
        characters = person["characters"]
        actor = list(name_basics.find({"nconst": nconst}))
        actor_name = actor[0]["primaryName"]
        print(actor_name + " played " + characters)
    return 

def searchForGenres(title_basics, title_ratings):
    genre = input("What genre you want to search for: ")
    minVotes = input("What is the minimum number of votes: ")
    string = 'genres.'+genre
    
    
    stages = [{"$lookup": {
              "from": 'title_ratings',
              "localField": "tconst",
              "foreignField": "tconst",
              "as": "tconst"}},
              #{'$match':{'genres':{"$in": [genre]}}},
              #{'$match': {'numVotes': {'$gt':minVotes}}}
              #{'$sort': {'averageRating': -1}}]
              ]
    result = list(title_basics.aggregate(stages))
    for r in result:
        print(r)
    return

def searchForCast():
    name = input("What is cast/crew member name: ")
    stages = [{"$primaryName": {"$eq": name}},
              {"$lookup": {
               "$From": title_principals,
               "$LocalField": "$nconst",
               "$foreignField": "$nconst",
               "$as": "$nconst"}},
              {"$lookup": {
              "$From": title_basics,
              "$LocalField": "$tconst",
              "$foreignField": "$tconst",
              "$as": "$tconst"}},
              {"$group": {
                      '$_id': "$category",
                      items: {"$push": "$item"}
                  }}              
              ]  

def add_movie(title_basics):
    
    print("This is the add movie function where you can add a movie\nby providing a unique id, a title, a start year, a running time and a list of genres")
    movie_id = input('Please enter a unique id: ')
    
    # find all the results for the movie_id
    results = list(title_basics.find({"tconst": movie_id}))
    
    if results != []:
        print('this movie id already exists, please enter a unique id')
        print('you will be returned to the home screen')
        return
    
    # the id is unique
    title = input('PLease enter the title: ')
    start_year = input('PLease enter the start year: ')
    running_time  = input('PLease enter the running time: ')
    genres = []
    print('please enter a list of genres for this movie, to end adding enter "q"')
    user_input = ' '
    while user_input.lower() != 'q':
        user_input = input('please enter a genre or "q": ')
        if user_input.lower() != 'q':
            genres.append(user_input)
        if user_input == [] and user_input.lower() == 'q':
            # if the user did not enter anything
            print('you must enter a genre, cannot quit nowwww!!!!')
            user_input = ' '
            
    title_basics.insert_one(
        { 'tconst':movie_id,
         'titleType':'movie',
         'primaryTitle':title,
         'originalTitle':title,
         'isAdult':"\\N",
         'startYear':start_year,
         'endYear':'\\N',
         'runtimeMinutes': running_time,
         'genres':genres})   
    
    print('It has been added succesfully!\nyou will be returned to the homescreen now')
    return

def add_cast_member(name_basics, title_basics, title_principals):
    '''
    The user should be able to add a row to title_principals by providing a cast/crew member id, 
    a title id, and a category. The provided title and person ids should exist in name_basics and 
    title_basics respectively (otherwise, proper messages should be given), the ordering should be 
    set to the largest ordering listed for the title plus one (or 1 if the title is not listed in 
    title_principals) and any other field that is not provided (including job and characters) set to Null.
    '''
    
    cast_id = input('Please enter a cast/crew member id: ')
    # check to see if it is in the name_basics and 
    results = list(name_basics.find({"nconst": cast_id}))
    if results == []:
        print('The cast memeber id does not exist please enter a valid id!!')
        print('you will be returned to the homescreen')
        return
    
    title_id = input('Please enter a movie title id: ')
    results = list(title_basics.find({"tconst": title_id}))
    if results == []:
        print('The movie title id does not exist please enter a valid id!!')
        print('you will be returned to the homescreen')
        return    
    
    category = input('Please enter the category: ')
    orderings = list(title_principals.find({"tconst": title_id}))

    ordering = []
    for order in orderings:
        order['ordering'] = int(order['ordering'])
        ordering.append(order['ordering'])
    
    # order them
    if ordering == []:
        ordering = 1
    else:
        ordering =  str(max(ordering) + 1)
    
    title_principals.insert_one(
        { 'tconst':title_id,
          'ordering':ordering,
          'nconst':cast_id,
          'category':category,
          'job':'\\N',
          'characters': '\\N'})  
    
    print('This added succesfully!')
    return

def main():
    name_basics, title_basics, title_principals, title_ratings = connect()
    #add_movie(title_basics)
    #add_cast_member(name_basics, title_basics, title_principals)
    #search_movie(title_basics, title_ratings, name_basics, title_principals)
    searchForGenres(title_basics, title_ratings)
main()