import pandas as pd
from scoring_logic import name_sim, cat_sim, year_bucket_match, unit_match
import typer
from pathlib import Path
import torch
from sentence_transformers import SentenceTransformer
import numpy as np
from sentence_transformers import util

model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_single(text):
    return model.encode(text, convert_to_tensor=True)

WEIGHT_NAME_SIMILARITY = 0.5
WEIGHT_CATEGORY_SIMILARITY = 0.2
WEIGHT_YEAR_BUCKET_MATCH = 0.1
WEIGHT_UNIT_MATCH = 0.2

class MaterialMapper:
    def __init__(self, 
                 specific: pd.DataFrame, 
                 generic: pd.DataFrame):
        self.specific = specific
        self.generic = generic
        self.generic_name_embeddings = embed_single(generic["Name (en)"].fillna("").tolist())
        self.generic_cat_embeddings = embed_single(generic["Kategorie (en)"].fillna("").tolist())
        self.specific_name_embeddings = model.encode(
            specific["Name (en)"].fillna("").tolist(), convert_to_tensor=True
        )
        self.specific_cat_embeddings = model.encode(
            specific["Kategorie (en)"].fillna("").tolist(), convert_to_tensor=True
        )
    
    def calculate_row_scores(self, 
                             row: pd.Series, 
                             idx: int, 
                             name_similarities: np.ndarray, 
                             cat_similarities: np.ndarray, 
                             specific_ref_year: int, 
                             specific_unit: str) -> pd.Series:
            name_score = name_similarities[idx]
            cat_score = cat_similarities[idx]
            year_score = year_bucket_match(specific_ref_year, row["Referenzjahr"])
            unit_score = unit_match(specific_unit, row["Bezugseinheit"])
            
            final_score = (
                WEIGHT_NAME_SIMILARITY * name_score + 
                WEIGHT_CATEGORY_SIMILARITY * cat_score + 
                WEIGHT_YEAR_BUCKET_MATCH * year_score + 
                WEIGHT_UNIT_MATCH * unit_score
            )
            
            return pd.Series({
                "Generic_UUID": row["UUID"],
                "Generic_Name": row["Name (en)"],
                "Name_Similarity": round(name_score, 3),
                "Category_Similarity": round(cat_score, 3), 
                "Year_Match": year_score,
                "Unit_Match": unit_score,
                "Final_Score": round(final_score, 3)
            })

    def calculate_scores(self, 
                         specific_uuid: str) -> pd.DataFrame:
        """
        Calculate the scores for the specific material and the generic materials
        """
        specific_index = self.specific[self.specific["UUID"] == specific_uuid].index
        if specific_index.empty:
            print(f"No specific material found with UUID: {specific_uuid}")
            return

        # Retrieve the precomputed embeddings for the specific material
        spec_name_emb = self.specific_name_embeddings[specific_index[0]]
        spec_cat_emb = self.specific_cat_embeddings[specific_index[0]]

        # Compute similarity in one shot
        name_similarities = (
            util.cos_sim(spec_name_emb, self.generic_name_embeddings).cpu().numpy().flatten()
        )
        cat_similarities = (
            util.cos_sim(spec_cat_emb, self.generic_cat_embeddings).cpu().numpy().flatten()
        )

        specific_ref_year = self.specific.iloc[specific_index[0]]["Referenzjahr"]
        specific_unit = self.specific.iloc[specific_index[0]]["Bezugseinheit"]
        
        results_df = self.generic.apply(
            lambda row: self.calculate_row_scores(
                row,
                self.generic.index.get_loc(row.name),
                name_similarities,
                cat_similarities,
                specific_ref_year,
                specific_unit
            ),
            axis=1
        )
        
        top_results = results_df.nlargest(3, "Final_Score")
        
        return top_results
    
    def process_material(self, row: pd.Series) -> pd.DataFrame:
            print(f"Processing specific material: {row['Name (en)']}")
            res = self.calculate_scores(specific_uuid=row['UUID'])
            if res is not None:
                # Create a DataFrame for each match with the specific material
                matches = res.assign(
                    Specific_UUID=row['UUID'],
                    Specific_Name=row['Name (en)']
                )[['Specific_UUID', 'Generic_UUID', 'Specific_Name', 'Generic_Name', 'Final_Score']]
                return matches
            return pd.DataFrame()  # Return empty DataFrame if no matches

    def map_materials(self) -> pd.DataFrame:
        """
        Map the specific materials to the generic materials
        """
        specific_generic_mapping = pd.DataFrame()
        specific_generic_mapping = pd.DataFrame(
            columns=[
                "Specific_UUID",
                "Generic_UUID",
                "Specific_Name",
                "Generic_Name",
                "Final_Score",
            ]
        )
        # Apply the processing function to all specific materials and combine results
        specific_generic_mapping = pd.concat(
            self.specific.apply(self.process_material, axis=1).tolist(),
            ignore_index=True
        )

        specific_generic_mapping.to_csv(
            "data/result/specific_generic_mapping.csv", index=False
        )


if __name__ == "__main__":
    specific = pd.read_csv("data/processed/specific.csv")
    generic = pd.read_csv("data/processed/generic.csv")

    mapper = MaterialMapper(specific, generic)
    mapper.map_materials()
