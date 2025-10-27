import csv

def DefaultDeserializer(row: list[str], cols: list[str]) -> object:
    """ The default csv deserializer for the DeserializeCSV function. Maps the value for the corresponding column onto a new object. """
    obj = {}
    for i, col in enumerate(cols):
        obj[col] = row[i]
    return obj

def DeserializeCSV(path: str, deserializer=None) -> list[object]:
    """ Reads a given csv file and uses the given deserializer function to map values into keys for a new object """
    if not path.endswith(".csv"): raise Exception("Must be a CSV file (.csv)")
    data: list[object] = []
    with open(file=path, encoding="mac_roman", newline='') as csvFile:
        reader = csv.reader(csvFile, quotechar = '|')
        cols = next(reader) # Grab column names on the first line of the CSV file
        for row in reader:
            data.append((deserializer if deserializer is not None else DefaultDeserializer)(row, cols))
    return data