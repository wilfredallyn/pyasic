import asyncio
import pandas as pd
import sqlite3
from pyasic.miners.factory import get_miner


def connect_db(db_file="pyasic.db") -> sqlite3.Connection:
    try:
        conn = sqlite3.connect(db_file)
        # conn = create_engine(f'sqlite:///{db_file}') sqlalchemy engine
        return conn
    except sqlite3.Error:
        raise ConnectionError(f"Cannot open sqlite database")


def preprocess_data(miner_data: dict) -> pd.DataFrame:
    hashboards = flatten_hashboards(miner_data["hashboards"])
    fans = flatten_fans(miner_data["fans"])

    # TODO: handle errors list
    exclude_cols = ["config", "hashboards", "fans", "errors"]

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


async def save_miner_data(
    ip: str, db_file: str = "miner.db", table_name: str = "data", sleep_mins: int = 5
):
    miner = await get_miner(ip)
    if miner is None:
        return
    try:
        while True:
            miner_data = await miner.get_data()
            df = preprocess_data(miner_data.as_dict())
            with sqlite3.connect(db_file) as conn:
                df.to_sql(table_name, conn, if_exists="append", index=False)
            await asyncio.sleep(sleep_mins * 60)
    except asyncio.CancelledError:
        print(f"Stopped saving miner data to {db_file}")
        # TODO: cleanup
        raise
