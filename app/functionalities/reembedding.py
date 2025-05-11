"""This is the place to put re-embedding functions for after an update of the Ökobaudat data set was made.
Unfortunately, it could not be implemented before the project was over."""

import pandas as pd

class ReEmbedder():
    """Re-embeds available datasets, usually after an update has been made"""

    def __init__(self):
        #self.obd_data: pd.DataFrame
        pass


    def run_reembedding(self):
        """Re-embeds Ökobaudat data"""
        pass

    def create_best_matches_csv(self):
        """Compares Ökobaudat embeddings and finds generic datasets that match specific datasets.
        Returns a csv with the 3 best matches for every orphaned specific material"""
        pass