import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# load TBS dataset to be mapped
unmapped_df = pd.read_csv('Reference_results_UNmapped_TBS_products_with_OBD_genericUUIDs.csv', low_memory=False) 

# load OBD datasets to be used for the mapping
obd_2020_df = pd.read_csv(r'C:\Users\Nutzer\OneDrive\CodeAcademyBerlin_Projects\N3XTCODER_AI4Impact\Data\OBD\OBD_2020_II.csv',
                            sep=';', encoding='ISO-8859-1', low_memory=False)
obd_2023_df = pd.read_csv(r'C:\Users\Nutzer\OneDrive\CodeAcademyBerlin_Projects\N3XTCODER_AI4Impact\Data\OBD\OBD_2023_I.csv',
                            sep=';', encoding='ISO-8859-1', low_memory=False)
obd_2024_df = pd.read_csv(r'C:\Users\Nutzer\OneDrive\CodeAcademyBerlin_Projects\N3XTCODER_AI4Impact\Data\OBD\OBD_2024_I.csv',
                            sep=';', encoding='ISO-8859-1', low_memory=False)

# Filter for only "generic dataset" entries
generic_2020 = obd_2020_df[obd_2020_df['Typ'] == 'generic dataset']
generic_2023 = obd_2023_df[obd_2023_df['Typ'] == 'generic dataset']
generic_2024 = obd_2024_df[obd_2024_df['Typ'] == 'generic dataset']

# Combine all generic materials into one DataFrame
generic_all_years_df = pd.concat([generic_2020, generic_2023, generic_2024], ignore_index=True)


# Select relevant features
# adjust format/datatype of the relevant features

# Fill nulls
generic_all_years_df['Name (en)'] = generic_all_years_df['Name (en)'].fillna('')
generic_all_years_df['Bezugseinheit'] = generic_all_years_df['Bezugseinheit'].fillna('')
generic_all_years_df['Referenzjahr'] = pd.to_numeric(generic_all_years_df['Referenzjahr'], errors='coerce')

unmapped_df['productName'] = unmapped_df['productName'].fillna('')
unmapped_df['tBaustoffVersion'] = unmapped_df['tBaustoffVersion'].fillna('2024-Q4')  # Simulated fallback
unmapped_df['version_year'] = unmapped_df['tBaustoffVersion'].str.extract(r'(\d{4})').astype(float)

### method to generate vectors/embeddings (the code below should be adjusted based on the method tested) ###
# Vectorize names
name_vectorizer = TfidfVectorizer().fit(
    generic_all_years_df['Name (en)'].tolist() + unmapped_df['productName'].tolist()
)
generic_vectors = name_vectorizer.transform(generic_all_years_df['Name (en)'])

# Loop through each unmapped entry
matches = []

for idx, row in unmapped_df.iterrows():
    specific_name = row['productName']
    year = row['version_year']
    unit = 'kg'  # Simulated; replace if actual value available

    specific_vector = name_vectorizer.transform([specific_name])
    name_similarities = cosine_similarity(specific_vector, generic_vectors).flatten()

    temp_df = generic_all_years_df.copy()
    temp_df['Specific_Name'] = specific_name
    temp_df['Name_Similarity'] = name_similarities
    temp_df['Year_Match'] = temp_df['Referenzjahr'].apply(lambda x: 1 if pd.notna(x) and abs(x - year) <= 2 else 0)
    temp_df['Unit_Match'] = (temp_df['Bezugseinheit'] == unit).astype(int)

    temp_df['Final_Score'] = (
        0.4 * temp_df['Name_Similarity'] +
        0.1 * temp_df['Year_Match'] +
        0.2 * temp_df['Unit_Match']
    )

    top_match = temp_df.sort_values(by='Final_Score', ascending=False).head(1)
    matches.append(top_match)

# Combine results
top_matches_df = pd.concat(matches, ignore_index=True)
# display final results
top_matches_df_2=top_matches_df[['Specific_Name', 'UUID', 'Name (en)', 'Name_Similarity', 'Year_Match', 'Unit_Match', 'Final_Score']]
top_matches_df_2.sort_values(by='Final_Score', ascending=False)

### ###

# calculate overall score for the method
overall_score_mean = top_matches_df_2['Final_Score'].mean()
overall_score_median = top_matches_df_2['Final_Score'].median()
print('Final score mean =',overall_score_mean)
print('Final score median =',overall_score_median)

# compare matching done with reality
Reference_Mapped_df = pd.read_csv('Reference_results_mapped_TBS_products_with_OBD_genericUUIDs.csv', low_memory=False)
combined_Reference_Mapped_df_with_matching = Reference_Mapped_df.merge(top_matches_df_2, left_on=['productName'], right_on=['Specific_Name'], how='left') # map OBD into TBS

# summary of matching assessment
print('TBaustoff products to map',combined_Reference_Mapped_df_with_matching['productName'].nunique())
print('unique UUID assigned',combined_Reference_Mapped_df_with_matching['UUID'].nunique())

# matched UUID Vs Real Mapping
combined_Reference_Mapped_df_with_matching['UUID_matched'] = combined_Reference_Mapped_df_with_matching['UUID']==combined_Reference_Mapped_df_with_matching['oekobaudatProcessUuid']
match_count=combined_Reference_Mapped_df_with_matching[combined_Reference_Mapped_df_with_matching['UUID_matched']==True]
print('matched UUID equal to Reality',len(match_count))
print('Success Matching Rate',len(match_count)/combined_Reference_Mapped_df_with_matching['productName'].nunique())