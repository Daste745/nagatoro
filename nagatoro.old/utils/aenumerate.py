from collections.abc import AsyncIterator


class AsyncEnumerator(AsyncIterator):
    """Async enumerate"""

    def __init__(self, aiterable, start=0):
        self._aiterable = aiterable
        self._i = start - 1

    def __aiter__(self):
        self._ait = self._aiterable.__aiter__()
        return self

    async def __anext__(self,):
        # self._ait will raise the apropriate AsyncStopIteration
        val = await self._ait.__anext__()
        self._i += 1
        return self._i, val
