import pandas as pd
from pathlib import Path

def preprocess_data(raw_data_path: Path, processed_data_path: Path) -> None:
    """
    Preprocess the data from raw_data_path and save the processed data to processed_data_path
    This function assumes the OBD datasets are in the raw_data_path/OBD folder
    """
    # Get all CSV files in the raw data OBD folder
    obd_files = list(raw_data_path.joinpath('OBD').glob('*.csv'))
    
    dfs = []
    for file in obd_files:
        # Read CSV with proper encoding and separator
        df = pd.read_csv(file, sep=';', encoding='ISO-8859-1', low_memory=False)
        
        # Convert numeric columns that use comma as decimal separator
        for col in df.select_dtypes(include=['object']).columns:
            try:
                df[col] = pd.to_numeric(df[col].str.replace(',', '.'))
            except:
                pass
                
        # Handle Referenzjahr and Gueltig bis columns specially
        df['Referenzjahr'] = pd.to_numeric(df['Referenzjahr'], errors='coerce').fillna(df['Referenzjahr']).astype('Int64')
        df['Gueltig bis'] = pd.to_numeric(df['Gueltig bis'], errors='coerce').fillna(df['Gueltig bis']).astype('Int64')
        
        dfs.append(df)
        # Drop columns that are all NaN
        df = df.drop(columns=df.columns[df.isna().all()])
        
        # Split into specific and generic datasets
        specific = df[df['Typ'] == 'specific dataset'].copy()
        generic = df[df['Typ'] == 'generic dataset'].copy()
        
        # Add dataset identifier based on filename
        dataset_name = file.stem
        generic['data_set'] = dataset_name
        
        # Drop duplicates
        specific = specific.drop_duplicates(subset=['UUID'])
        generic = generic.drop_duplicates(subset=['UUID'])
        
        # Fill missing text fields
        text_cols = ['UUID', 'Name (en)', 'Kategorie (en)', 'Bezugseinheit']
        specific[text_cols] = specific[text_cols].fillna(value='', downcast='infer')
        generic[text_cols] = generic[text_cols].fillna(value='', downcast='infer')
        
        dfs.append({'specific': specific, 'generic': generic})

    # Combine all specific and generic datasets
    all_specific = pd.concat([df.get('specific') for df in dfs if isinstance(df, dict)], ignore_index=True)
    all_generic = pd.concat([df.get('generic') for df in dfs if isinstance(df, dict)], ignore_index=True)
    all_generic = all_generic.drop_duplicates(subset=["UUID"])
    all_specific = all_specific.drop_duplicates(subset=["UUID"])
    
    # Save processed data
    all_specific.to_csv(processed_data_path / 'specific.csv', index=False)
    all_generic.to_csv(processed_data_path / 'generic.csv', index=False)

