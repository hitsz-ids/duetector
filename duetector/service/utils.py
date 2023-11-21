import asyncio

from fastapi.concurrency import run_in_threadpool


async def ensure_async(f: callable, *args, **kwargs):
    # await async function, run sync function in thread pool
    if asyncio.iscoroutinefunction(f):
        return await f(*args, **kwargs)

    return await run_in_threadpool(f, *args, **kwargs)
