import asyncio
import pandas as pd
import sqlite3
from pyasic.miners.factory import get_miner
from typing import Any


def preprocess_data(miner_data: dict) -> pd.DataFrame:
    hashboards = flatten_hashboards(miner_data["hashboards"])
    fans = flatten_fans(miner_data["fans"])

    # TODO: handle errors list
    exclude_cols = ["config", "hashboards", "fans", "errors"]

    data = {k: v for k, v in miner_data.items() if k not in exclude_cols}
    df = pd.DataFrame([{**data, **hashboards, **fans}])
    return df


def flatten_hashboards(hashboard_data: list[dict[str, Any]]) -> dict:
    """
    Flatten hashboard data
    [ {'slot': 0, 'hashrate': 3.45, ...}, ...] -> {'hashboard_0_slot': 0, 'hashboard_0_hashrate': 3.45, ...}]
    """
    hashboards = {}
    for item in hashboard_data:
        slot = item["slot"]
        for key, value in item.items():
            hashboards[f"hashboard_{slot}_{key}"] = value
    return hashboards


def flatten_fans(fan_data: list[dict[str, Any]]) -> dict:
    """Flatten fan data: [{'speed': 1620}, ...]) -> {'fan_0_speed': 1620, ...}"""
    fans = {}
    for index, item in enumerate(fan_data):
        for key, value in item.items():
            fans[f"fan_{index}_{key}"] = value
    return fans


async def write_data(
    ip: str, data_file: str = "miner.db", table_name: str = "data", sleep_mins: int = 5
) -> None:
    miner = await get_miner(ip)
    if miner is None:
        return
    try:
        while True:
            miner_data = await miner.get_data()
            df = preprocess_data(miner_data.as_dict())
            if data_file.endswith(".csv"):
                df.to_csv(data_file, index=False, mode="a")
            else:
                with sqlite3.connect(data_file) as conn:
                    df.to_sql(table_name, conn, if_exists="append", index=False)
            await asyncio.sleep(sleep_mins * 60)
    except asyncio.CancelledError:
        print(f"Stopped saving miner data to {data_file}")
        raise


def load_db(db_file: str = "miner.db", table_name: str = "data") -> pd.DataFrame:
    with sqlite3.connect(db_file) as conn:
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    return df
