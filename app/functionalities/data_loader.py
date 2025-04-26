import pandas as pd
from loguru import logger

try:
    tbaustoff = pd.read_csv('app/data/tBaustoff/tBaustoff_with_OBD_mapping.csv', encoding='utf-8', low_memory=False)

    OBD_2020 = pd.read_csv('app/data/OBD/OBD_2020_II.csv', delimiter=';', encoding='latin-1', low_memory=False)
    OBD_2023 = pd.read_csv('app/data/OBD/OBD_2023_I.csv', delimiter=';', encoding='latin-1', low_memory=False)
    OBD_2024 = pd.read_csv('app/data/OBD/OBD_2024_I.csv', delimiter=';', encoding='latin-1', low_memory=False)
except FileNotFoundError as e:
    logger.critical(f'Could not load a file. Error: {e.strerror} {e.filename}')
except Exception as e:
    logger.critical(f'Could not load all files. Error:{e}')
