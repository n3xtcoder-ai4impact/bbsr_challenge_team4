import pandas as pd
from pathlib import Path
from loguru import logger


class DataLoader:
    def __init__(self):
        self.obd = self._load_obd_directory('app/data/OBD')
        self.tbaustoff = pd.read_csv('app/data/tBaustoff/tBaustoff_with_OBD_mapping.csv', encoding='utf-8',
                                     low_memory=False)
        logger.info(f'Loaded tBaustoff.csv')
        self.specific_generic_mapping = pd.read_csv('app/data/semantic_matching/specific_generic_mapping.csv',
                                                    low_memory=False)
        logger.info(f'Loaded specific_generic_mapping.csv')


    def _load_obd_directory(self, directory: str) -> pd.DataFrame:
        """
        Loads all CSV files from the given directory and combines them into one DataFrame.
        Adds a 'source_file' column with the original filename.
        """
        path = Path(directory)
        all_dfs = []

        for csv_file in path.glob('*.csv'):
            if not 'obd' in csv_file.name.lower():
                continue
            try:
                df = pd.read_csv(csv_file, delimiter=';', encoding='latin-1', low_memory=False)
                df['source_file'] = csv_file.name
                logger.info(f'Loaded {csv_file.name}')
                all_dfs.append(df)
            except Exception as e:
                logger.critical(f'Could not load all files. Error:{e}')
                continue

        if all_dfs:
            return pd.concat(all_dfs, ignore_index=True)
        else:
            return pd.DataFrame()