from pathlib import Path
import pandas as pd
import numpy as np
import typer
from torch.utils.data import Dataset


class MyDataset(Dataset):
    """My custom dataset."""

    def __init__(self, data_path: Path) -> None:
        self.data_path = data_path
        self.data = self._load_data()

    def __len__(self) -> int:
        """Return the length of the dataset."""
        return len(self.data)

    def __getitem__(self, index: int):
        """Return a given sample from the dataset."""
        return self.data.iloc[index]

    def preprocess(self, output_folder: Path) -> None:
        """Preprocess the raw data and save it to the output folder."""
        specific, generic = self._process_data()
        specific.to_csv(output_folder / "specific_data.csv", index=False)
        generic.to_csv(output_folder / "generic_data.csv", index=False)

    def _load_data(self) -> pd.DataFrame:
        """Load the raw data from the file."""
        return pd.read_csv(
            self.data_path,
            sep=";",
            encoding="ISO-8859-1",
            low_memory=False
        )

    def _process_data(self):
        """Process the raw data into specific and generic datasets."""
        data = self.data

        # Convert numeric columns to float automatically
        for col in data.select_dtypes(include=["object"]).columns:
            try:
                data[col] = pd.to_numeric(data[col].str.replace(",", "."))
            except:
                pass

        # Convert to int64 but ignore NaN values
        data["Referenzjahr"] = pd.to_numeric(data["Referenzjahr"], errors="coerce").fillna(data["Referenzjahr"]).astype("Int64")
        data["Gueltig bis"] = pd.to_numeric(data["Gueltig bis"], errors="coerce").fillna(data["Gueltig bis"]).astype("Int64")

        # Drop columns with all NaN values
        data = data.drop(columns=data.columns[data.isna().all()])

        # Replace empty strings with NaN in the columns before converting to Int64
        data["Referenzjahr"] = pd.to_numeric(data["Referenzjahr"].replace("", np.nan), errors="coerce").fillna(data["Referenzjahr"]).astype("Int64")
        data["Gueltig bis"] = pd.to_numeric(data["Gueltig bis"].replace("", np.nan), errors="coerce").fillna(data["Gueltig bis"]).astype("Int64")

        # Split into specific and generic datasets
        specific_data = data[data["Typ"] == "specific dataset"]
        generic_data = data[data["Typ"] == "generic dataset"]

        specific = pd.DataFrame(specific_data).drop_duplicates(subset=["UUID"])
        generic = pd.DataFrame(generic_data).drop_duplicates(subset=["UUID"])

        # Fill missing text
        specific[["UUID", "Name (en)", "Kategorie (en)", "Bezugseinheit"]] = specific[
            ["UUID", "Name (en)", "Kategorie (en)", "Bezugseinheit"]
        ].fillna(value="").infer_objects()
        generic[["UUID", "Name (en)", "Kategorie (en)", "Bezugseinheit"]] = generic[
            ["UUID", "Name (en)", "Kategorie (en)", "Bezugseinheit"]
        ].fillna(value="").infer_objects()

        return specific, generic


def preprocess(data_path: Path, output_folder: Path) -> None:
    print("Preprocessing data...")
    dataset = MyDataset(data_path)
    dataset.preprocess(output_folder)


if __name__ == "__main__":
    typer.run(lambda: preprocess(
        data_path=Path(typer.prompt("Enter the path to the data file")),
        output_folder=Path("data/processed")
    ))
