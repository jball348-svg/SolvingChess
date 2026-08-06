import pandas as pd


def save_csv(records, filename):
    """
    Saves encoded positions to CSV.
    """

    dataframe = pd.DataFrame(records)

    dataframe.to_csv(
        filename,
        index=False
    )
