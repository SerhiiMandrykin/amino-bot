import asyncio
import time


class DelayAction:
    TIME_DELAY = 5  # delay in seconds for sending messages
    LAST_ACTION_TIME = 0

    async def wait(self):
        time_diff = time.time() - self.LAST_ACTION_TIME
        print('Time diff is ' + str(int(time_diff)) + ' seconds')
        if time_diff < self.TIME_DELAY:
            print('Waiting for ' + str(self.TIME_DELAY - time_diff) + ' seconds')
            await asyncio.sleep(self.TIME_DELAY - time_diff)

        self.LAST_ACTION_TIME = time.time()
