from pathlib import Path

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_single(text):
    return model.encode(text, convert_to_tensor=True)


WEIGHT_NAME_SIMILARITY = 0.6
WEIGHT_CATEGORY_SIMILARITY = 0.4

class MaterialMapper:
    def __init__(self, unmapped_generic: pd.DataFrame, tbs: pd.DataFrame):
        self.unmapped_generic = unmapped_generic
        self.tbs = tbs
        self.tbs_name_embeddings = embed_single(
            tbs["productName"].fillna("").tolist()
        )
        print(f"Shape of tbs_name_embeddings: {self.tbs_name_embeddings.shape}")
        self.tbs_cat_embeddings = embed_single(
            tbs["eolCategoryName"].fillna("").tolist()
        )
        self.unmapped_generic_name_embeddings = model.encode(
            unmapped_generic["Name (de)"].fillna("").tolist(), convert_to_tensor=True
        )
        print(f"Shape of unmapped_generic_name_embeddings: {self.unmapped_generic_name_embeddings.shape}")
        self.unmapped_generic_cat_embeddings = model.encode(
            unmapped_generic["Kategorie (original)"].fillna("").tolist(), convert_to_tensor=True
        )

    def calculate_row_scores(
        self,
        row: pd.Series,
        idx: int,
        name_similarities: np.ndarray,
        cat_similarities: np.ndarray,

    ) -> pd.Series:
        """
        Calculate the scores for the unmapped_generic material and the tbs materials
        """
        name_score = name_similarities[idx]
        cat_score = cat_similarities[idx]
        
        final_score = (
            WEIGHT_NAME_SIMILARITY * name_score
            + WEIGHT_CATEGORY_SIMILARITY * cat_score
        )

        return pd.Series(
            {
                'unmapped_generic_UUID': row['UUID'],
                'unmapped_generic_name': row['Name (de)'],
                'tbs_product_UUID': self.tbs.loc[idx, 'oekobaudatProcessUuid'],
                'tbs_product_name': self.tbs.loc[idx, 'productName'],
                "Name_Similarity": round(name_score, 3),
                'unmapped_generic_category': row['Kategorie (original)'],
                'tbs_category_name': self.tbs.loc[idx, 'eolCategoryName'],
                "Category_Similarity": round(cat_score, 3),
                'tbs_EOL_Scenario_Unbuilt_Real': self.tbs.loc[idx, 'eolScenarioUnbuiltReal'],
                'tbs_EOL_Scenario_Unbuilt_Potential': self.tbs.loc[idx, 'eolScenarioUnbuiltPotential'],
                'tbs_EOL_Scenario_Technology_Factor': self.tbs.loc[idx, 'technologyFactor'],
                "Final_Score": round(final_score, 3),
            }
        )

    def calculate_scores(self, unmapped_generic_uuid: str) -> pd.DataFrame:
        """
        Calculate scores for a unmapped_generic material and return top 3 matches
        """
        unmapped_generic_index = self.unmapped_generic[self.unmapped_generic["UUID"] == unmapped_generic_uuid].index
        if unmapped_generic_index.empty:
            print(f"No unmapped_generic material found with UUID: {unmapped_generic_uuid}")
            return None

        # Retrieve the precomputed embeddings for the unmapped_generic material
        unmapped_generic_name_emb = self.unmapped_generic_name_embeddings[unmapped_generic_index[0]]
        unmapped_generic_cat_emb = self.unmapped_generic_cat_embeddings[unmapped_generic_index[0]]

        # Compute similarity in one shot
        name_similarities = (
            util.cos_sim(unmapped_generic_name_emb, self.tbs_name_embeddings)
            .cpu()
            .numpy()
            .flatten()
        )
        cat_similarities = (
            util.cos_sim(unmapped_generic_cat_emb, self.tbs_cat_embeddings)
            .cpu()
            .numpy()
            .flatten()
        )

        all_scores = []
        for tbs_idx in range(len(self.tbs)):
            score_series = self.calculate_row_scores(
                row=self.unmapped_generic.loc[unmapped_generic_index[0]], # Pass the full row
                idx=tbs_idx, # Pass the current TBS index
                name_similarities=name_similarities, # Pass the full similarity arrays
                cat_similarities=cat_similarities
            )
            all_scores.append(score_series)
        
        final_scores_df = pd.DataFrame(all_scores)
        # sort and return top 3
        top_matches = final_scores_df.sort_values(by='Final_Score', ascending=False).head(3)
        return top_matches


    def map_materials(self):
        """
        mapping of all unmapped_generic materials to TBS materials
        """
        all_results = []
        for index, row in self.unmapped_generic.iterrows():
            print(f"Processing UUID: {row['UUID']}")
            result = self.calculate_scores(row['UUID'])
            if result is not None:
                all_results.append(result)
        
        # Concatenate all results into a single DataFrame
        final_results_df = pd.concat(all_results, ignore_index=True)


        # Save results to CSV
        RESULTS_DATA_ROOT = Path("C:/Users/Nutzer/Documents/my_data/results") # Example path
        final_results_df.to_csv(RESULTS_DATA_ROOT / "unmapped_generic_tbs_mapping.csv", encoding="utf-8", index=False)


if __name__ == "__main__":
    PROCESSED_DATA_ROOT = Path("C:/Users/Nutzer/Documents/my_data/processed") # Example path
    RAW_DATA_ROOT = Path("C:/Users/Nutzer/Documents/my_data/raw")
    unmapped_generic = pd.read_csv(PROCESSED_DATA_ROOT / "unmapped_generic.csv", encoding="ISO-8859-1")
    # unmapped_generic_all = pd.read_csv(PROCESSED_DATA_ROOT / "unmapped_generic.csv", encoding="ISO-8859-1")
    # unmapped_generic = unmapped_generic_all.head(30)
    # tbs = pd.read_csv(RAW_DATA_ROOT / "TBS" / "tBaustoff_with_OBD_mapping.csv", encoding='utf-8')
    tbs_full = pd.read_csv(RAW_DATA_ROOT / "TBS" / "tBaustoff_with_OBD_mapping.csv", encoding='utf-8')
    tbs = tbs_full.drop_duplicates(subset=["productName"]).reset_index(drop=True)

    mapper = MaterialMapper(unmapped_generic, tbs)
    mapper.map_materials()