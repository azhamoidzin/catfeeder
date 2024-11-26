from datetime import datetime, timedelta
import asyncio


class GlobalState:
    def __init__(self):
        self.time_offset = timedelta(0)
        self.time_lock = asyncio.Lock()

    def get_current_time(self):
        return datetime.now() + self.time_offset

    def time_warp(self, days: int = 0):
        self.time_offset += timedelta(days=days)

    async def get_time_lock(self):
        async with self.time_lock:
            yield


GLOBAL_STATE = GlobalState()
