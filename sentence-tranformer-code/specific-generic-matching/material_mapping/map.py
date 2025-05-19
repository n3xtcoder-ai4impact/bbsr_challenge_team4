import pandas as pd
from scoring_logic import name_sim, cat_sim, year_bucket_match, unit_match
import typer
from pathlib import Path
import torch
from sentence_transformers import SentenceTransformer
from sentence_transformers import util

model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_single(text):
    return model.encode(text, convert_to_tensor=True)


def calculate_scores(
    specific_uuid: str, 
    specific: pd.DataFrame, 
    generic: pd.DataFrame, 
    generic_name_embeddings: torch.Tensor, 
    generic_cat_embeddings: torch.Tensor,
    specific_name_embeddings: torch.Tensor, 
    specific_cat_embeddings: torch.Tensor
) -> pd.DataFrame:
    """
    Calculate the scores for the specific material and the generic materials
    """
    specific_index = specific[specific["UUID"] == specific_uuid].index
    if specific_index.empty:
        print(f"No specific material found with UUID: {specific_uuid}")
        return

    # Retrieve the precomputed embeddings for the specific material
    spec_name_emb = specific_name_embeddings[specific_index[0]]
    spec_cat_emb = specific_cat_embeddings[specific_index[0]]

    # Compute similarity in one shot
    name_similarities = (
        util.cos_sim(spec_name_emb, generic_name_embeddings).cpu().numpy().flatten()
    )
    cat_similarities = (
        util.cos_sim(spec_cat_emb, generic_cat_embeddings).cpu().numpy().flatten()
    )

    results = []
    for i, (_, gen_row) in enumerate(generic.iterrows()):
        name_score = name_similarities[i]
        cat_score = cat_similarities[i]
        year_score = year_bucket_match(
            specific.iloc[specific_index[0]]["Referenzjahr"], gen_row["Referenzjahr"]
        )
        unit_score = unit_match(
            specific.iloc[specific_index[0]]["Bezugseinheit"], gen_row["Bezugseinheit"]
        )

        final_score = (
            0.5 * name_score + 0.2 * cat_score + 0.1 * year_score + 0.2 * unit_score
        )

        results.append(
            {
                "Generic_UUID": gen_row["UUID"],
                "Generic_Name": gen_row["Name (en)"],
                "Name_Similarity": round(name_score, 3),
                "Category_Similarity": round(cat_score, 3),
                "Year_Match": year_score,
                "Unit_Match": unit_score,
                "Final_Score": round(final_score, 3),
            }
        )

    results_df = pd.DataFrame(results)
    top_results = results_df.nlargest(3, "Final_Score")

    return top_results


def map_materials(
    specific: pd.DataFrame,
    generic: pd.DataFrame,
    generic_name_embeddings: torch.Tensor,
    generic_cat_embeddings: torch.Tensor,
    specific_name_embeddings: torch.Tensor,
    specific_cat_embeddings: torch.Tensor
) -> pd.DataFrame:
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
    for row in specific.iterrows():
        print(f"Processing specific material: {row[1]['Name (en)']}")
        specific_uuid = row[1]["UUID"]
        res = calculate_scores(
            specific_uuid=specific_uuid,
            specific=specific,
            generic=generic,
            generic_name_embeddings=generic_name_embeddings,
            generic_cat_embeddings=generic_cat_embeddings,
            specific_name_embeddings=specific_name_embeddings,
            specific_cat_embeddings=specific_cat_embeddings,
        )
        if res is not None:
            for _, r in res.iterrows():
                specific_generic_mapping = pd.concat(
                    [
                        specific_generic_mapping,
                        pd.DataFrame(
                            [
                                {
                                    "Specific_UUID": specific_uuid,
                                    "Generic_UUID": r["Generic_UUID"],
                                    "Specific_Name": row[1]["Name (en)"],
                                    "Generic_Name": r["Generic_Name"],
                                    "Final_Score": r["Final_Score"],
                                }
                            ]
                        ),
                    ],
                    ignore_index=True,
                )

    specific_generic_mapping.to_csv(
        "data/result/specific_generic_mapping.csv", index=False
    )


if __name__ == "__main__":
    specific = pd.read_csv("data/processed/specific.csv")
    generic = pd.read_csv("data/processed/generic.csv")

    generic_name_embeddings = embed_single(generic["Name (en)"].fillna("").tolist())
    generic_cat_embeddings = embed_single(generic["Kategorie (en)"].fillna("").tolist())
    specific_name_embeddings = model.encode(
        specific["Name (en)"].fillna("").tolist(), convert_to_tensor=True
    )
    specific_cat_embeddings = model.encode(
        specific["Kategorie (en)"].fillna("").tolist(), convert_to_tensor=True
    )

    map_materials(
        specific=specific,
        generic=generic,
        generic_name_embeddings=generic_name_embeddings,
        generic_cat_embeddings=generic_cat_embeddings,
        specific_name_embeddings=specific_name_embeddings,
        specific_cat_embeddings=specific_cat_embeddings,
    )
