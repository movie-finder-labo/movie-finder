from backend.moviefinder.csv import DeserializeCSV
import os
from time import time

def TestSerializeDirectory(path: str):
    absPath = os.getcwd() + path
    print(f"Serialising csv file at directory {absPath}:")
    clock = time()
    try:
        data = DeserializeCSV(path)
    except Exception:
        print("Deserialization failed.")
    clock = time() - clock # Don't waste time counting the object with len first
    print(f"[{len(data)}] Time elapsed for file at path {absPath}: {clock} seconds.{data[0]}\n")

if __name__ == "__main__":
    try:
        print(f"Current working directory: {os.getcwd()}.\nBeginning deserialization...")
        TestSerializeDirectory("ml-32m/tags.csv")
        TestSerializeDirectory("ml-32m/links.csv")
        TestSerializeDirectory("ml-32m/movies.csv")
        TestSerializeDirectory("ml-32m/ratings.csv")
    except KeyboardInterrupt: # CTRL + C
        print("Keyboard interrupt.")
    finally:
        print("Finished!")