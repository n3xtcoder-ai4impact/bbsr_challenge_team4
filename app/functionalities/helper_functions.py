import csv
import json
import os
from pathlib import Path

from loguru import logger

from app.model.RouterModels import DatasetVersion


def read_json_file(file_path: str) -> dict:
    """Reads a JSON file and returns its content as a dictionary."""
    with open(file_path, "r", encoding="utf-8") as json_file:
        return json.load(json_file)


def write_csv_from_response(response, output_path: str):
    """Writes a csv file given an API text response"""
    lines = response.text.splitlines()
    with open(output_path, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        for line in lines:
            row = line.split(";")
            writer.writerow(row)


def save_dataset_version(filepath: str, dataset=DatasetVersion):
    """Writes a variable of Type DatasetVersion as a dict into a json file.
    Used for saving the current dataset version to app/data/OBD"""
    json_data = dataset.__dict__
    Path(filepath).write_text(
        json.dumps(json_data, indent=2, ensure_ascii=False), encoding="utf-8"
    )
