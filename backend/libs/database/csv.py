import os
import re
from os.path import isfile, join, dirname, abspath

BASE_DIR = dirname(dirname(dirname(abspath(__file__))))
DATA_DIR = join(BASE_DIR, "data")

dataFileExtension = ".csv"
MovieData = {}
""" Loaded formatted set of movie data based off of CSVData. Uses movieId as key """
CSVData = {}
""" Loaded raw CSV data indexed by file name (movies, ratings, tags, etc.) """

def formatCSVData(data: dict):
    cache = {}
    def Lookup(key: str, id):
        d = data.get(key, [])
        c = cache.get(key, {})
        value = c.get(id)
        if value is None:
            try:
                i = c.get("_idx", 0)
                x = d[i]
                xId = x.get("movieId") if x else None

                if xId == id:
                    c[xId] = x
                    return x
                elif xId is not None:
                    c[xId] = x
            except IndexError:
                pass
            finally:
                c["_idx"] = c.get("_idx", 0) + 1
                cache[key] = c
        return value

    def formatMovie(movie: dict):
        match = re.search(r"(.+?)\s\((\d{4})\)$", movie.get("title", ""))
        title = match.group(1).strip() if match else movie.get("title", "N/A")
        year = match.group(2) if match else "N/A"
        movie_id = movie.get("movieId")
        ratingLookup = Lookup("ratings", movie_id)
        moodLookup = Lookup("tags", movie_id)
        return {
            "id": movie_id,
            "title": title,
            "year": year,
            "genres": movie.get("genres", "").split("|"),
            "poster": "https://via.placeholder.com/300x450/252b3d/8a8f98?text=Movie",
            "rating": ratingLookup.get("rating") if ratingLookup else "N/A",
            "mood": moodLookup.get("tag") if moodLookup else "N/A",
            "ageSuitability": "N/A"
        }
    formatted = {}
    for movie in data.get("movies", []):
        formatted[movie["movieId"]] = formatMovie(movie)
    return formatted

def InitializeMovieData(path: str | None = None) -> dict:
    global MovieData, CSVData
    if MovieData:
        return MovieData
    try:
        for fp in GetDataFiles(path):
            data = DeserializeCSV(fp)
            key = os.path.basename(fp).replace(dataFileExtension, "")
            if key != "movies":
                data.reverse()
            CSVData[key] = data
        MovieData = formatCSVData(CSVData)
    except Exception as e:
        print(f"CSV file initialization failed: {e}")
        MovieData = {}
    return MovieData

def IsCSV(path: str) -> bool:
    return path.lower().endswith(dataFileExtension)

def GetDataFiles(path: str | None = None) -> list[str]:
    path = path or DATA_DIR
    files = []
    for p in os.listdir(path):
        fp = join(path, p)
        if isfile(fp) and IsCSV(fp):
            files.append(fp)
    return files

def DefaultDeserializer(row: str, cols: list[str]) -> dict:
    values = re.split(r",(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)", row)
    obj = {}
    for i, col in enumerate(cols):
        obj[col] = values[i].replace('"', "") if i < len(values) else ""
    return obj

def DeserializeCSV(path: str, deserializer=None) -> list[dict]:
    if not IsCSV(path):
        raise Exception("Must be a CSV file (.csv)")
    data = []
    with open(path, encoding="utf-8", newline="") as csvFile:
        cols = csvFile.readline().strip().split(",")
        for row in csvFile:
            parser = deserializer if deserializer else DefaultDeserializer
            data.append(parser(row.strip(), cols))
    return data
