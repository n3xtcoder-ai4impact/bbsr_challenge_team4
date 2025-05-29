from pathlib import Path

import pandas as pd


def preprocess_data(raw_data_path: Path, processed_data_path: Path) -> None:
    """
    Preprocess the data from raw_data_path and save the processed data to processed_data_path
    This function assumes the TBS dataset are in the raw_data_path/TBS folder
    """
    generic_df =  pd.read_csv(processed_data_path / "generic.csv", encoding="ISO-8859-1", low_memory=False)
    tbs_file_path = raw_data_path / "TBS" / "tBaustoff_with_OBD_mapping.csv"
    tbs = pd.read_csv(tbs_file_path, encoding="utf-8", low_memory=False)

    TBS_unique_UUID_set=set(tbs['oekobaudatProcessUuid'].unique())
    unmapped_generic = generic_df[~generic_df['UUID'].isin(TBS_unique_UUID_set)]

    # Save processed data
    unmapped_generic.to_csv(processed_data_path / "unmapped_generic.csv", encoding="ISO-8859-1", index=False)

if __name__ == "__main__":
    # path to be adjusted
    RAW_DATA_ROOT = Path("C:/Users/Nutzer/Documents/my_data/raw") # Example path
    PROCESSED_DATA_ROOT = Path("C:/Users/Nutzer/Documents/my_data/processed") # Example path

    # calling the preprocess function
    preprocess_data(RAW_DATA_ROOT, PROCESSED_DATA_ROOT)
    print(f"Data preprocessing complete. Processed files saved to: {PROCESSED_DATA_ROOT}")
