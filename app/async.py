from rich import print
import time
import asyncio


async def endpoint(route: str) -> str:
  print(f">>handling {route}")

  await asyncio.sleep(1)

  print(f"<< response {route}")
  return route


async def server():
  tests = (
    "GET /shipment?id=1",
    "PATCH /shipment?id=4",
    "GET /shipment?id=3"
  )
  start = time.perf_counter()

  requests = [asyncio.create_task(endpoint(route)) for route in tests]

  done,pending = await asyncio.wait(requests)

  for task in done:
    print(f"Result:{task.result()}")


  end = time.perf_counter()
  print(f"taketime:{end-start}s")

asyncio.run(server())

