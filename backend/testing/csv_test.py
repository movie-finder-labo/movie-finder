# Import parent directory so we can access libs package
import sys
from pathlib import Path

libdir = Path(__file__).resolve().parent.parent
sys.path.append(str(libdir))

from libs.database.csv import DeserializeCSV, GetDataFiles
from os import getcwd
from time import time

def TestDeserializePath(path: str):
    absPath = getcwd() + path
    print(f"Serialising csv file at directory {absPath}:")
    clock = time()
    data = DeserializeCSV(path)
    clock = time() - clock # Don't waste time counting the object with len first
    print(f"[{len(data)}] Time elapsed for file at path {absPath}: {clock} seconds.\n")
    print(data[0])
    print(data[-1])
    print(data[10])
    
def TestDeserializeDirectory():
    for fp in GetDataFiles():
        TestDeserializePath(fp)

if __name__ == "__main__":
    try:
        print(f"Current working directory: {getcwd()}.\nBeginning deserialization...")
        TestDeserializeDirectory()
    except KeyboardInterrupt: # CTRL + C
        print("Keyboard interrupt.")
    finally:
        print("Finished!")