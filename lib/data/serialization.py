"""DataFrame serialization helpers for cache storage.

Converts dicts containing DataFrames to/from JSON-serializable format.
Used by middleware modules that cache financial data.
"""

import pandas as pd


def serialize_df_dict(data: dict) -> dict:
    """Convert dict containing DataFrames to JSON-serializable dict."""
    result = {}
    for k, v in data.items():
        if isinstance(v, pd.DataFrame) and not v.empty:
            df = v.copy()
            df.columns = [str(c) for c in df.columns]
            index_name = df.index.name or "index"
            df = df.reset_index()
            result[k] = {
                "__df__": True,
                "__index_col__": index_name,
                "__data__": df.to_dict(orient="list"),
            }
        elif isinstance(v, pd.DataFrame):
            result[k] = None
        else:
            result[k] = v
    return result


def restore_df_dict(data: dict) -> dict:
    """Restore dict containing serialized DataFrames."""
    result = {}
    for k, v in data.items():
        if isinstance(v, dict) and v.get("__df__"):
            df = pd.DataFrame(v["__data__"])
            index_col = v.get("__index_col__", "index")
            if index_col in df.columns:
                df = df.set_index(index_col)
                df.index.name = None
            result[k] = df
        elif isinstance(v, dict) and any(isinstance(val, list) for val in v.values()):
            df = pd.DataFrame(v)
            if "index" in df.columns:
                df = df.set_index("index")
                df.index.name = None
            result[k] = df
        else:
            result[k] = v
    return result
