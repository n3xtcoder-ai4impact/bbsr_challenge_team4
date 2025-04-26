import pandas as pd
from material_mapping.similarity import name_sim, cat_sim, year_bucket_match, unit_match
from material_mapping.embed import embed_single
import typer
from pathlib import Path

def calculate_scores(specific_uuid, specific, generic, generic_name_embeddings, generic_cat_embeddings) -> pd.DataFrame:
    
    specific_material = specific[specific['UUID'] == specific_uuid]
    if specific_material.empty:
        print(f"No specific material found with UUID: {specific_uuid}")
        return
    
    spec_name_emb = embed_single(specific_material.iloc[0]["Name (en)"])
    spec_cat_emb = embed_single(specific_material.iloc[0]["Kategorie (en)"])

    results = []
    for i, (_, gen_row) in enumerate(generic.iterrows()):
        name_score = name_sim(spec_name_emb, generic_name_embeddings[i])
        cat_score = cat_sim(spec_cat_emb, generic_cat_embeddings[i])
        year_score = year_bucket_match(specific_material.iloc[0]["Referenzjahr"], gen_row["Referenzjahr"])
        unit_score = unit_match(specific_material.iloc[0]["Bezugseinheit"], gen_row["Bezugseinheit"])

        final_score = 0.5 * name_score + 0.2 * cat_score + 0.1 * year_score + 0.2 * unit_score

        results.append({
            "Generic_UUID": gen_row["UUID"],
            "Generic_Name": gen_row["Name (en)"],
            "Name_Similarity": round(name_score, 3),
            "Category_Similarity": round(cat_score, 3),
            "Year_Match": year_score,
            "Unit_Match": unit_score,
            "Final_Score": round(final_score, 3)
        })

    results_df = pd.DataFrame(results)
    return results_df

if __name__ == "__main__":
    specific = pd.read_csv("data/processed/specific_data.csv")
    generic = pd.read_csv("data/processed/generic_data.csv")
    generic_name_embeddings = embed_single(generic["Name (en)"].fillna("").tolist())
    generic_cat_embeddings = embed_single(generic["Kategorie (en)"].fillna("").tolist())
    uuid = typer.prompt("Please enter the UUID")
    result_df = calculate_scores(uuid, specific, generic, generic_name_embeddings, generic_cat_embeddings)
    if result_df is not None:
        top_results = result_df.nlargest(3, "Final_Score")
        print(top_results)
    
