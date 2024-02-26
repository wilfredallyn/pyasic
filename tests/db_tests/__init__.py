import pandas as pd
from pyasic.db import flatten_fans, flatten_hashboards, preprocess_data
import unittest


class DBTest(unittest.TestCase):
    def setUp(self) -> None:
        self.fan_data = [
            {"speed": 1620},
            {"speed": 960},
        ]
        self.hashboard_data = [
            {"slot": 0, "hashrate": 3.45, "temp": 71},
            {"slot": 1, "hashrate": 3.41, "temp": 74},
            {"slot": 2, "hashrate": 3.34, "temp": 73},
        ]
        self.miner_data = {
            "fans": self.fan_data,
            "hashboards": self.hashboard_data,
        }

    def test_flatten_fans(self):
        expected_dict = {
            "fan_0_speed": 1620,
            "fan_1_speed": 960,
        }
        self.assertDictEqual(flatten_fans(self.fan_data), expected_dict)

    def test_flatten_hashboards(self):
        expected_dict = {
            "hashboard_0_slot": 0,
            "hashboard_0_hashrate": 3.45,
            "hashboard_0_temp": 71,
            "hashboard_1_slot": 1,
            "hashboard_1_hashrate": 3.41,
            "hashboard_1_temp": 74,
            "hashboard_2_slot": 2,
            "hashboard_2_hashrate": 3.34,
            "hashboard_2_temp": 73,
        }
        self.assertDictEqual(flatten_hashboards(self.hashboard_data), expected_dict)

    def test_preprocess_data_returns_df(self):
        self.assertIsInstance(preprocess_data(self.miner_data), pd.DataFrame)
