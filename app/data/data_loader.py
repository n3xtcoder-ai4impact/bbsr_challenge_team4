import pandas as pd


#todo catch errors when loading csv files
df_tbaustoff = pd.read_csv('app/data/tBaustoff/tBaustoff_with_OBD_mapping.csv', encoding='utf-8', low_memory=False)

df_OBD_2020 = pd.read_csv('app/data/OBD/OBD_2020_II.csv', delimiter=';', encoding='latin-1', low_memory=False)
df_OBD_2023 = pd.read_csv('app/data/OBD/OBD_2023_I.csv', delimiter=';', encoding='latin-1', low_memory=False)
df_OBD_2024 = pd.read_csv('app/data/OBD/OBD_2024_I.csv', delimiter=';', encoding='latin-1', low_memory=False)