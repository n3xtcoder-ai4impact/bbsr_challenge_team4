import json

def read_json_file(self, file_path: str) -> dict:
    """Reads a JSON file and returns its content as a dictionary."""
    with open(file_path, 'r', encoding='utf-8') as json_file:
        return json.load(json_file)