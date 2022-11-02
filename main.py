import asyncio

from instances import Material

loop = asyncio.get_event_loop()


if __name__ == "__main__":
    loop.run_until_complete(Material().findByKeys(['id'], [1]))

