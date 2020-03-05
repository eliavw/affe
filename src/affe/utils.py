import pandas as pd

def flatten_dict(d, separator="."):
    return pd.json_normalize(d, sep=separator).to_dict(orient="records").pop()