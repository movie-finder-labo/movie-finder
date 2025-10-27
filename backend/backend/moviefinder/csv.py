import csv
import json

def DefaultSerializer(l: list[str]) -> object:
    """ The default csv deserializer for the DeserializeCSV function """
    return ",".join(l)

def DeserializeCSV(path: str, deserializer: callable[[list[str]], object] | None) -> list[object]:
    """ Reads a given csv file and uses the given deserializer function to map values into keys for a new object """
    if not path.endswith(".csv"): raise Exception("Must be a CSV file (.csv)")
    l = []
    with open(file=path, encoding="mac_roman", newline='') as csvFile:
        reader = csv.reader(csvFile, quotechar = '|')
        for row in reader:
            l.append(deserializer(row) if deserializer is not None else DefaultSerializer)
    return l