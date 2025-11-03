from backend.database.csv import DeserializeCSV, GetDataFiles
from os import getcwd
from time import time

def TestDeserializePath(path: str):
    absPath = getcwd() + path
    print(f"Serialising csv file at directory {absPath}:")
    clock = time()
    try:
        data = DeserializeCSV(path)
        clock = time() - clock # Don't waste time counting the object with len first
        print(f"[{len(data)}] Time elapsed for file at path {absPath}: {clock} seconds.\n")
    except Exception as e:
        print(f"Deserialization failed: {e}.")
    
def TestDeserializeDirectory(path: str):
    for fp in GetDataFiles():
        TestDeserializePath(fp)

if __name__ == "__main__":
    try:
        print(f"Current working directory: {getcwd()}.\nBeginning deserialization...")
        TestDeserializeDirectory("../data")
    except KeyboardInterrupt: # CTRL + C
        print("Keyboard interrupt.")
    finally:
        print("Finished!")