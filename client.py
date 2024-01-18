import asyncio
import aiohttp

numb = 4

data_json = {
    'article': f'valideted art{numb}',
    'description': f'some discription{numb}',
    'owner': f'Host{numb}'       
             }

async def main():
    client = aiohttp.ClientSession()
    response = await client.post('http://0.0.0.0:8080/api', json=data_json)
    print(response.status)
    # response_2 = await client.get('http://0.0.0.0:8080/')
    # print(response_2)
    # print(await response.json())

    await client.close()




if __name__ == '__main__':
    asyncio.run(main())

