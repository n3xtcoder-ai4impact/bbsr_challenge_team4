"""This is used to re-create the list of best matches after an update of the Ökobaudat data set was made."""

from pathlib import Path
import numpy as np
import pandas as pd
from loguru import logger
from sentence_transformers import SentenceTransformer, util


WEIGHT_NAME_SIMILARITY = 0.5
WEIGHT_CATEGORY_SIMILARITY = 0.2
WEIGHT_YEAR_BUCKET_MATCH = 0.1
WEIGHT_UNIT_MATCH = 0.2


class MaterialMapper:
    def __init__(self):
        self.model_dir = 'app/data/semantic_matching/model'
        self.model_name = 'all-MiniLM-L6-v2'
        #self.model = SentenceTransformer(model_name_or_path=f'{self.model_dir}/{self.model_name}', local_files_only=True)

        self.specific = pd.DataFrame()
        self.generic = pd.DataFrame()

        self.generic_name_embeddings = []
        self.generic_cat_embeddings = []
        self.specific_name_embeddings = []
        self.specific_cat_embeddings = []


    def download_model(self, model_name:str):
        """Downloads the named model from huggingface and saves it in self.model_dir"""
        model = SentenceTransformer(model_name_or_path=model_name)
        _ = model.save_pretrained(f'{self.model_dir}/{self.model_name}')


    def embed_single(self, text):
        return self.model.encode(text, convert_to_tensor=True)


    def create_embeddings(self):
        self.generic_name_embeddings = self.embed_single(
            self.generic["Name (en)"].fillna("").tolist()
        )
        self.generic_cat_embeddings = self.embed_single(
            self.generic["Kategorie (en)"].fillna("").tolist()
        )
        self.specific_name_embeddings = self.model.encode(
            self.specific["Name (en)"].fillna("").tolist(), convert_to_tensor=True
        )
        self.specific_cat_embeddings = self.model.encode(
            self.specific["Kategorie (en)"].fillna("").tolist(), convert_to_tensor=True
        )


    def year_bucket_match(self, year1: int, year2: int) -> int:
        if pd.isna(year1) or pd.isna(year2):
            return 0
        return 1 if abs(int(year1) - int(year2)) <= 2 else 0


    def unit_match(self, unit1: str, unit2: str) -> int:
        return 1 if unit1.strip().lower() == unit2.strip().lower() else 0


    def calculate_row_scores(
        self,
        row: pd.Series,
        idx: int,
        name_similarities: np.ndarray,
        cat_similarities: np.ndarray,
        specific_ref_year: int,
        specific_unit: str,
    ) -> pd.Series:
        """
        Calculate the scores for the specific material and the generic materials
        """
        name_score = name_similarities[idx]
        cat_score = cat_similarities[idx]
        year_score = self.year_bucket_match(specific_ref_year, row["Referenzjahr"])
        unit_score = self.unit_match(specific_unit, row["Bezugseinheit"])

        final_score = (
            WEIGHT_NAME_SIMILARITY * name_score
            + WEIGHT_CATEGORY_SIMILARITY * cat_score
            + WEIGHT_YEAR_BUCKET_MATCH * year_score
            + WEIGHT_UNIT_MATCH * unit_score
        )

        return pd.Series(
            {
                "Generic_UUID": row["UUID"],
                "Generic_Name": row["Name (en)"],
                "Name_Similarity": round(name_score, 3),
                "Category_Similarity": round(cat_score, 3),
                "Year_Match": year_score,
                "Unit_Match": unit_score,
                "Final_Score": round(final_score, 3),
            }
        )

    def calculate_scores(self, specific_uuid: str) -> pd.DataFrame:
        """
        Calculate scores for a specific material and return top 3 matches
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
            util.cos_sim(spec_name_emb, self.generic_name_embeddings)
            .cpu()
            .numpy()
            .flatten()
        )
        cat_similarities = (
            util.cos_sim(spec_cat_emb, self.generic_cat_embeddings)
            .cpu()
            .numpy()
            .flatten()
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
                specific_unit,
            ),
            axis=1,
        )

        top_results = results_df.nlargest(3, "Final_Score")

        return top_results

    def process_material(self, row: pd.Series) -> pd.DataFrame:
        """
        Calculate the score for a specific material and return top 3 matches in a DataFrame
        """
        print(f"Processing specific material: {row['Name (en)']}")
        res = self.calculate_scores(specific_uuid=row["UUID"])
        if res is not None:
            # Create a DataFrame for each match with the specific material
            matches = res.assign(
                Specific_UUID=row["UUID"], Specific_Name=row["Name (en)"]
            )[
                [
                    "Specific_UUID",
                    "Generic_UUID",
                    "Specific_Name",
                    "Generic_Name",
                    "Final_Score",
                ]
            ]
            return matches
        return pd.DataFrame()  # Return empty DataFrame if no matches

    def map_materials(self) -> pd.DataFrame:
        """
        Go through all specific materials and give matches for them
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
            ignore_index=True,
        )

        specific_generic_mapping.to_csv(
            "data/result/specific_generic_mapping.csv", index=False
        )


    def preprocess_data(self,obd: pd.DataFrame, processed_data_path: str) -> None:
        """
        Preprocess the data from raw_data_path and save the processed data to processed_data_path
        This function assumes the OBD datasets are in the raw_data_path/OBD folder
        """
        # Get all CSV files in the raw data OBD folder

        #obd_files = list(raw_data_path.joinpath("OBD").glob("*.csv"))
        logger.info(f'Len OBD: {len(obd)}')
        dfs = []
        for file in [obd]:
            # Read CSV with proper encoding and separator
            #df = pd.read_csv(file, sep=";", encoding="ISO-8859-1", low_memory=False)
            df = obd
            logger.info(f'Len DF: {len(df)}')
            # Convert numeric columns that use comma as decimal separator
            for col in df.select_dtypes(include=["object"]).columns:
                try:
                    df[col] = pd.to_numeric(df[col].str.replace(",", "."))
                except:
                    pass

            # Handle Referenzjahr and Gueltig bis columns specially
            df["Referenzjahr"] = (
                pd.to_numeric(df["Referenzjahr"], errors="coerce")
                .fillna(df["Referenzjahr"])
                .astype("Int64")
            )
            df["Gueltig bis"] = (
                pd.to_numeric(df["Gueltig bis"], errors="coerce")
                .fillna(df["Gueltig bis"])
                .astype("Int64")
            )

            dfs.append(df)
            # Drop columns that are all NaN
            df = df.drop(columns=df.columns[df.isna().all()])

            # Split into specific and generic datasets
            specific = df[df["Typ"] == "specific dataset"].copy()
            generic = df[df["Typ"] == "generic dataset"].copy()

            # Add dataset identifier based on filename
            dataset_name = file.stem
            generic["data_set"] = dataset_name

            # Drop duplicates
            specific = specific.drop_duplicates(subset=["UUID"])
            generic = generic.drop_duplicates(subset=["UUID"])

            # Fill missing text fields
            text_cols = ["UUID", "Name (en)", "Kategorie (en)", "Bezugseinheit"]
            specific[text_cols] = specific[text_cols].fillna(value="", downcast="infer")
            generic[text_cols] = generic[text_cols].fillna(value="", downcast="infer")

            dfs.append({"specific": specific, "generic": generic})

        # Combine all specific and generic datasets
        all_specific = pd.concat(
            [df.get("specific") for df in dfs if isinstance(df, dict)], ignore_index=True
        )
        all_generic = pd.concat(
            [df.get("generic") for df in dfs if isinstance(df, dict)], ignore_index=True
        )
        all_generic = all_generic.drop_duplicates(subset=["UUID"])
        all_specific = all_specific.drop_duplicates(subset=["UUID"])

        # Save processed data
        all_specific.to_csv(f'{processed_data_path} + "specific.csv"', index=False)
        all_generic.to_csv(f'{processed_data_path} + "generic.csv"', index=False)
