from backend.moviefinder.csv import DeserializeCSV
import os
import time

if __name__ == "__main__":
    print(f"Current directory: {os.getcwd()}.")
    print("Serialising tags:")
    DeserializeCSV("ml-32m/tags.csv")