import json
import pymongo
import re
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
    return name_basics, title_basics, title_principals, title_ratings, db

def search_movie(title_basics, title_ratings, name_basics, title_principals):
    movies = search_by_key_words(title_basics) 
    print("Movies by the given search: ")
    index = 0
    indexEd = 0
    i = "n"
    indexToCheck = -1
    while(i!="c"):
        if i=="n":
            movies = list(movies)
            for movie in movies:
                print(str(index+1), movie)
                index = index+ 1
               
        i = input("In order to view detailed information about movie enter its number.\nIf you want to search another movie press s. \nif you want to return to homepage enter 'q': ")
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
    print('\n')
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
        strKeys = strKeys + "i\"" + keyword + "\""   

    # title_basics.create_index([("startYear", 'text')])
    stages = {"$text": {"$search": strKeys}}
    output_movies = title_basics.find(stages)
    return output_movies

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

def searchForGenres(db, title_basics, title_ratings):
    genre = input("What genre you want to search for: ")
    minVotes = int(input("What is the minimum number of votes: "))
    title_ratings.drop_indexes()
    # movies = list(title_basics.find({'genres':{"$in": [genre]}})) 
    
    stages = [{'$unwind': '$genres'},
              {"$match": {"genres": re.compile(genre, re.IGNORECASE)}}]
              
    results = list(title_basics.aggregate(stages))
    tconst_list = []
    print_dic = {}
    for result in results:
        tconst_list.append(result['tconst'])
        print_dic[result['tconst']] = result['primaryTitle']
    
    stages2 = [{'$match':{'tconst':{"$in": tconst_list}}},
               {'$set': {'numVotes': {'$toInt':'$numVotes'}}},
               {'$match':{'numVotes':{'$gte': minVotes}}}, 
               {'$sort': {'averageRating': -1}}]
    movies = list(title_ratings.aggregate(stages2)) 
    
    print('title, rating')
    for movie in movies:
        print(print_dic[movie['tconst']], movie['averageRating'],movie['numVotes'])
    
    print('done!\n')
    return

def searchForCast(name_basics, title_principals, title_basics):
    name = input("What is cast/crew member name: ")
    stages = [{"$match": {"primaryName": re.compile(name, re.IGNORECASE)}}]  
    results = list(name_basics.aggregate(stages))
    for result in results:
        print('The cast memeber name: '+result['primaryName'])
        print('The cast member id:    '+ result['nconst'])
        print('Professions: ', result['primaryProfession'])
        
        # search for all the places where he played a role 
        nconst = result["nconst"]
        stages1 = {"nconst": nconst}
        principals = list(title_principals.find(stages1))
        
        print('Title, job and chracters played are as following:')
        for principal in principals:
            tconst = principal["tconst"]
            stages2 = [{"$match": {"tconst": re.compile(tconst, re.IGNORECASE)}}]
            movie = list(title_basics.aggregate(stages2))
            if principal["job"] == '\N' and principal["characters"] == '\N':
                print(movie[0]["primaryTitle"])
            elif principal["job"] == '\N':
                print(movie[0]["primaryTitle"] + " as character " + principal["characters"])
            elif principal["characters"] == '\N':
                print(movie[0]["primaryTitle"] + ": job of " + principal["job"])
            else:
                print(movie[0]["primaryTitle"] + ": job of " + principal["job"] + " as character " + principal["characters"])
            
        print("\n")
    return
            
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
        if max(ordering) > 10:
            ordering =  '10'
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
    continue_program = True
    while continue_program:
        print('Welcome to the program! to quit enter "q" to continue enter one of the choices')
        print('1.search for titles')
        print('2.search for genres')
        print('3.search for cast/crew members')
        print('4.add a movie')
        print('5.add a cast/crew member')
        
        # connect to the db
        name_basics, title_basics, title_principals, title_ratings, db = connect()
        choice = input('\n\nplease enter your choice: ').lower()
        if choice == 'q':
            continue_program = False
        elif choice == '1':
            search_movie(title_basics, title_ratings, name_basics, title_principals)
        elif choice == '2':
            searchForGenres(db, title_basics, title_ratings)
        elif choice == '3':
            searchForCast(name_basics, title_principals, title_basics)
        elif choice == '4':
            add_movie(title_basics)
        elif choice == '5':
            add_cast_member(name_basics, title_basics, title_principals)
        else:
            print('\nplease enter a valid choice!!!!')
        
        
    
    print('Thank you for using the program will close now')
main()