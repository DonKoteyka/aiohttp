import asyncio
import aiohttp


async def main():
    client = aiohttp.ClientSession()
    response = await client.post('http://127.0.0.1:8080')
    print(response.status)




if __name__ == '__main__':
    asyncio.run(main())

