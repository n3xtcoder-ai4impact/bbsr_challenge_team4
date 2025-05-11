import json
import os
import csv
from pathlib import Path
from app.model.RouterModels import DatasetVersion
from loguru import logger


def read_json_file(file_path: str) -> dict:
    """Reads a JSON file and returns its content as a dictionary."""
    with open(file_path, 'r', encoding='utf-8') as json_file:
        return json.load(json_file)


def overwrite_smaller_file(new_file: str, old_file: str):
    """Checks if a csv file already exists. If it does, the number of rows in the existing and
    the new file are compared. The old file gets replaced if it is shorter."""

    overwritten = False

    with open(old_file, 'r', encoding='latin-1') as f:
        existing_file_lines = sum(1 for _ in f)

    with open(new_file, 'r', encoding='latin-1') as f:
        new_file_lines = sum(1 for _ in f)

    if new_file_lines > existing_file_lines:
        os.replace(new_file, old_file)
        logger.info(f'Overwriting existing file "{old_file}" because it was shorter than the downloaded file.')
        overwritten = True
    else:
        logger.info(
            f'Keeping existing file "{old_file}" because it is longer than or equal to the downloaded file.')
        if os.path.exists(old_file):
            os.remove(new_file)

    return overwritten


def write_csv_from_response(response, output_path: str):
    """Writes a csv file given an API text response"""
    lines = response.text.splitlines()
    with open(output_path, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        for line in lines:
            row = line.split(';')
            writer.writerow(row)

def save_dataset_version(filepath: str, dataset=DatasetVersion):
    """Writes a variable of Type DatasetVersion as a dict into a json file.
    Used for saving the current dataset version to app/data/OBD"""
    json_data = dataset.__dict__
    Path(filepath).write_text(json.dumps(json_data, indent=2, ensure_ascii=False), encoding='utf-8')