import asyncio
from pyasic import save_miner_data


if __name__ == "__main__":
    ip = "192.168.0.159"
    asyncio.run(save_miner_data(ip, sleep_mins=1))
