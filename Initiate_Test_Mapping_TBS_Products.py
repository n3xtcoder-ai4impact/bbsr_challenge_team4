import pandas as pd

# load TBaustoff dataset
tbaustoff_df = pd.read_csv('data/tBaustoff/tBaustoff_with_OBD_mapping.csv', low_memory=False)

# TBS unique UUID (assumed as mapped to OBDs) = 728 unique UUIDs in TBaustoff
TBS_with_UUIDs_df = tbaustoff_df[tbaustoff_df['oekobaudatProcessUuid'].notna()]
TBS_unique_UUID=set(TBS_with_UUIDs_df['oekobaudatProcessUuid'].unique())


# Load all three OBD files (adjust paths as needed)
obd_2020_df = pd.read_csv('data/OBD/OBD_2020_II.csv',
                            sep=';', encoding='ISO-8859-1', low_memory=False)
obd_2023_df = pd.read_csv('data/OBD/OBD_2023_I.csv',
                            sep=';', encoding='ISO-8859-1', low_memory=False)
obd_2024_df = pd.read_csv('data/OBD/OBD_2024_I.csv',
                            sep=';', encoding='ISO-8859-1', low_memory=False)

# Add column with DB version
obd_2020_df['OBD_Version'] = 'OBD_2020_II'
obd_2023_df['OBD_Version'] = 'OBD_2023_I'
obd_2024_df['OBD_Version'] = 'OBD_2024_I'

# Combine all OBD datasets into one DataFrame
OBD_all_years_df = pd.concat([obd_2020_df, obd_2023_df, obd_2024_df], ignore_index=True)

# only keep unique row by UUIDs
OBD_all_years_df_LessFeatures=OBD_all_years_df[['UUID', 'Name (de)', 'Name (en)', 'Kategorie (original)', 'Kategorie (en)', 'Typ', 'OBD_Version','Referenzjahr', 'Gueltig bis','UUID des Vorgängers',
                                        'Bezugsgroesse', 'Bezugseinheit', 'Referenzfluss-UUID','Referenzfluss-Name', 'Flaechengewicht (kg/m2)',
                                        'Rohdichte (kg/m3)']]
# remove duplicates
OBD_all_years_df_LessFeatures_2=OBD_all_years_df_LessFeatures.drop_duplicates()

# merge OBD into TBS
combined_TBS_OBD = TBS_with_UUIDs_df.merge(OBD_all_years_df_LessFeatures_2, left_on=['oekobaudatProcessUuid','oekobaudatDatastockName'], right_on=['UUID','OBD_Version'], how='left')

# find the UUIDs in TBaustoff that are not mapped to any of the 3 OBD Databases = 30 UUIDs not found in any of these 3 OBD databases
emptyUUID=combined_TBS_OBD[combined_TBS_OBD['UUID'].isna()]

# remove empty UUIDs from combined dataframe TBS OBD
combined_TBS_OBD_2=combined_TBS_OBD[combined_TBS_OBD['UUID'].notna()] # 698 unique UUIDS = 728 unique UUIDs in TBaustoff - 30 UUIDs not found in any of these 3 OBD databases



# create reference datasets : 
#   Mapped dataframe between TBS with OBDs, dataset of the reality (the aim to achieve for our matching method) = 
#                       current mapped TBS products with UUIDs from the 3 OBD databases.
#   UNMAPPED dataframe between TBS with OBDs, dataset to use for our matching method =
#                       umapped version with no duplicates (only 1 row by product) based on current mapped TBS products with UUIDs from the 3 OBD databases.
TBS_columns=list(tbaustoff_df.columns) # find TBS columns
ref_mapped_TBS_df = combined_TBS_OBD_3[TBS_columns] # keep TBS columns only
ref_mapped_TBS_df.to_csv("Reference_results_mapped_TBS_products_with_OBD_genericUUIDs.csv", index=False) # Save reference table of mapped TBS

ref_unmapped_TBS_df= ref_mapped_TBS_df.copy()
columns_to_empty = ['oekobaudatProcessUuid','oekobaudatDatastockUuid','oekobaudatDatastockName']
for col in columns_to_empty:
    ref_unmapped_TBS_df[col] = ''
ref_unmapped_TBS_df_2=ref_unmapped_TBS_df.drop_duplicates() # remove duplicates and now only 260 unique products in TBS to map with 1 (or more UUIDs) from OBS databases
ref_unmapped_TBS_df_2.to_csv("Reference_results_UNmapped_TBS_products_with_OBD_genericUUIDs.csv", index=False) # Save reference table of unmapped TBS