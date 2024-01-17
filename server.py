from aiohttp import web


app = web.Application(debug=True)

async def hello_world(request):
    return web.json_response({'hello': 'world'})

async def article_view(request):
    json_data = await request.json()
    print(json_data)




app.add_routes((
    web.get('/', hello_world),
    web.post('/api', article_view),
    # web.get('/api/<int:article_id>', article_view),
    ))

web.run_app(app)