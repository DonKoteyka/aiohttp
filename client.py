import asyncio
import aiohttp


data_json = {
    'article': 'valideted art',
    'description': 'some discription',
    'owner': 'Host'       
             }

async def main():
    client = aiohttp.ClientSession()
    response = await client.post('http://0.0.0.0:8080/api/', json=data_json)
    print(response.status)
    # print(await response.json())

    await client.close()




if __name__ == '__main__':
    asyncio.run(main())

