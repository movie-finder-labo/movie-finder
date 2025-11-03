import csv
from os import listdir
from os.path import isfile
import re

# Relative datafile path to ../movie-finder/backend/
dataFilePath = "data/"
dataFileExtension = ".csv"
MovieData = {}
CSVData = {}

def formatCSVData(data: dict):
    """ Formats raw CVS data across all the links, movies, ratings and tags datafiles and formats them into one dict.
    Sample movies
    {
        id: 1,
        title: "Inception",
        year: 2010,
        genres: ["Sci-Fi", "Action", "Thriller"],
        poster: "https://via.placeholder.com/300x450/252b3d/8a8f98?text=Inception",
        rating: 8.8,
        mood: "thoughtful",
        ageSuitability: 13
    },
    {
        id: 2,
        title: "The Shawshank Redemption",
        year: 1994,
        genres: ["Drama"],
        poster: "https://via.placeholder.com/300x450/252b3d/8a8f98?text=Shawshank",
        rating: 9.3,
        mood: "emotional",
        ageSuitability: 16
    },
    {
        id: 3,
        title: "The Dark Knight",
        year: 2008,
        genres: ["Action", "Crime", "Drama"],
        poster: "https://via.placeholder.com/300x450/252b3d/8a8f98?text=Dark+Knight",
        rating: 9.0,
        mood: "exciting",
        ageSuitability: 13
    }
    """
    cache = {} # Dgaf about space complexity. Assume at least one or more related rows per movieId in the other files.
    def Lookup(key: str, id):
        d = data[key]
        c = cache.get(key, {})
        value = c.get(id, None)
        if not value:
            # Keep track of the index inside the loop. We will not read N entries for every iteration, each entry only gets read once. Anything that doesn't match gets cached and looked up later.
            try:  
                i = c.get("_idx", 0)
                x = d[i]
                xId = x and x["movieId"] or None
                
                if x and xId == id:
                    if (xId == "193567"): print(x)
                    return x
                elif x is not None:
                    c[xId] = x
            except IndexError: # Do nothing if i is out of bounds. We are trying to explicitly avoid calling the len function for checking index bounds, as iterating over d defeats the purpose
                pass
            finally:
                c["_idx"] = i + 1
                cache[key] = c
                
        return value
    
    def formatMovie(movie: dict):
        match = re.search(r"(.+?)\s\((\d{4})\)$", movie["title"])
        title = match and match.group(1).strip() or movie["title"]
        year = match and match.group(2) or "N/A"
        id = movie["movieId"]
        ratingLookup = Lookup("ratings", id)
        moodLookup = Lookup("tags", id)
        fm = {
            "id": id,
            "title": title,
            "year": year,
            "genres": movie["genres"].split("|"),
            "poster": "https://via.placeholder.com/300x450/252b3d/8a8f98?text=Dark+Knight", # TODO: One of the two: imdbId,tmdbId. Maybe we can fetch the URL at some point
            "rating": ratingLookup and ratingLookup["rating"] or "N/A",
            "mood": moodLookup and moodLookup["tag"] or "N/A",
            "ageSuitability": "N/A" # ??
        }
        if (id =="193567"):print(fm)
        return fm
    
    fms = {}
    for movie in data["movies"]:
        fms[movie["movieId"]] = formatMovie(movie)
    return fms

def InitializeMovieData() -> dict:
    """ Finds and loads all .cvs files located in ../movie-finder/data/* and initialises movie data objects and stores them in the global variable 'MovieData'. Repeated calls to this function just returns the already loaded cache."""
    global MovieData
    global CSVData
    
    # Don't load twice
    try:
        data = list(MovieData.values())
        data[0]
        return MovieData
    except IndexError:
        try:
            for fp in GetDataFiles(): # e.g data/movies.csv, data/ratings.csv
                data = DeserializeCSV(fp)
                if fp != dataFilePath + "movies": data.reverse() # All the files are ordered by movieId, we need to reverse to setup performance boost for the formatCSVData function. The movie file doesn't matter.
                CSVData[fp.removeprefix(dataFilePath).removesuffix(dataFileExtension)] = data
            MovieData = formatCSVData(CSVData)
        except Exception as e:
            print(f"CVS file initialization failed: {e}")
            MovieData = {} # Roll back any changes
        finally:
            return MovieData

def IsCSV(path: str) -> bool:
    """ Checks if the file extension of a file matches with .csv """
    return path.endswith(dataFileExtension)

def GetDataFiles() -> list[str]:
    """ Finds the relative path to the ../movie-finder/backend folder of all the .csv data files in ../movie-finder/backend/data """
    fps = []
    for p in listdir(dataFilePath):
        fp = dataFilePath + p
        if isfile(fp) and IsCSV(fp):
            fps.append(fp)
    return fps

def DefaultDeserializer(row: list[str], cols: list[str]) -> dict:
    """ The default csv deserializer for the DeserializeCSV function. Maps the value for the corresponding column onto a new object. """
    obj = {}
    for i, col in enumerate(cols):
        obj[col] = row[i]
    return obj

def DeserializeCSV(path: str, deserializer=None) -> list[dict]:
    """ Reads a given csv file and uses the given deserializer function to map values into keys for a new object """
    if not IsCSV(path): raise Exception("Must be a CSV file (.csv)")
    data: list[dict] = []
    with open(file=path, encoding="mac_roman", newline='') as csvFile:
        reader = csv.reader(csvFile, quotechar ='|')
        cols = next(reader) # Grab column names on the first line of the CSV file
        for row in reader:
            data.append((deserializer if deserializer is not None else DefaultDeserializer)(row, cols))
    return data