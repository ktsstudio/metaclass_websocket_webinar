import asyncio
from typing import Awaitable, Callable, Any


async def do_by_timeout_wrapper(callback: Callable[[Any], Awaitable[Any]], timeout: int, args: list):
    await asyncio.sleep(timeout)
    return await callback(*args)
