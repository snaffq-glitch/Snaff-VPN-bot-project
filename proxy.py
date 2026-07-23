import asyncio
from mtprotoproxy import MTProtoProxy

async def main():
    proxy = MTProtoProxy(
        host="127.0.0.1",
        port=1443,
        secret="dd5e85fe80c819c59d4ea6965d700ac843"
    )
    await proxy.start()

asyncio.run(main())