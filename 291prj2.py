def search_movie(sid, cid):
    movies = search_by_key_words() 
    print("Movies by the given search: ")
    index = 0
    indexEd = 0
    i = "n"
    indexToCheck = -1
    while(i!="c"):
        if i=="n":
            for movie in movies:
                print(str(index+1) + ". " + str(movie))
        i = input("In order to view detailed information about movie enter its number.\nIf you want to see next movies in the search, enter 'n'. \nIf you want to serach another movie press s. \nif you want to return to homepage enter 'q': ")
        if i=="s":
            movies = search_by_key_words() 
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
        seeDetailedInfo(movies[indexEd])
    return

def search_by_key_words():
    keywords = input("Enter keywords for searching movie: ")
    keywords_list = keywords.split()
    title_basics.createIndex({"primaryTitle":"text","startYear":"text"})   
    output_movies = title_basics.find({"$text": {"$search": keywords_list}})
    return output_movies

def seeDetailedInfo(movie):
    inpMovie = ''
    print("\n\nDetailed information for " + movie)
    movie_title = movie["primaryTitle"]
    tconst = movie["tconst"]
    output_rating = title_ratings.find({"$tconst": {"$eq": tconst}})
    print("The rating is: " + str(output_rating["averageRating"]))
    print("The number of votes is: " + str(output_rating["numVotes"]))
    roles = title_principals.find({"$tconst": {"$eq": tconst}})
    for person in roles:
        nconst = person["nconst"]
        characters = person["characters"]
        actor = name_basics.find({"$nconst": {"$eq": nconst}})
        actor_name = actor["primaryName"]
        print(actor_name + " played " + characters)
    return 

def searchForGenres():
    genre = input("What genre you want to search for: ")
    minVotes = input("What is the minimum number of votes: ")
    stages = [{"$lookup": {
              "$From": title_ratings,
              "$LocalField": "$tconst",
              "$foreignField": "$tconst",
              "$as": "$tconst"}},
              {"$in": {genre, "$genre"}},
              {'$match': {{ "$toInt": '$integer' }: {'$gt':minVotes}}},
              {'$sort': {'averageRating': -1}}]
    result = title_basics.aggregate(stages)
    for r in result:
        print(r)
    return

def searchForCast():
    name = input("What is cast/crew member name: ")
    stages = [{"$primaryName": {"$eq": name}},
              {"$lookup": {
               "$From": title_principals,
               "$LocalField": "$nconst",
               "$foreignField": "nconst",
               "$as": "$nconst"}},
              {"$lookup": {
              "$From": title_basics,
              "$LocalField": "$tconst",
              "$foreignField": "$tconst",
              "$as": "$tconst"}},
              {"$group": {
                      nconst: "$category",
                      items: {"$push": "$item"}
                  }}              
              ]  



        
    
            
        