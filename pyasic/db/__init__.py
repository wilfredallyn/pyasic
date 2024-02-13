import asyncio
import pandas as pd
from sqlalchemy import exc
import sqlite3


def get_sql_engine(db_file="pyasic.db") -> sqlite3.Connection:
    try:
        engine = sqlite3.connect(db_file)
        return engine
    except exc.OperationalError:
        raise ConnectionError(f"Cannot open sqlite database")


def preprocess_data(miner_data: dict) -> pd.DataFrame:
    hashboards = flatten_hashboards(miner_data["hashboards"])
    fans = flatten_fans(miner_data["fans"])
    exclude_cols = ["config", "hashboards", "fans"]

    data = {k: v for k, v in miner_data.items() if k not in exclude_cols}
    df = pd.DataFrame([{**data, **hashboards, **fans}])
    return df


def flatten_hashboards(hashboards_data: dict) -> dict:
    hashboards = {}
    for item in hashboards_data:
        slot = item["slot"]
        for key, value in item.items():
            hashboards[f"hashboards_{slot}_{key}"] = value
    return hashboards


def flatten_fans(fans_data: dict) -> dict:
    fans = {}
    for index, item in enumerate(fans_data):
        for key, value in item.items():
            fans[f"fans_{index}_{key}"] = value
    return fans
