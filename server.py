import json
from aiohttp import web
from models import engine, Session, Article, init_db
from sqlalchemy.exc import IntegrityError



app = web.Application(debug=True)

@web.middleware
async def session_middleware(request: web.Request, handler):
    async with Session() as session:
        request.session = session
        response = await handler(request)
        return response
    

async def init_orm(app: web.Application):
    print('start')
    await init_db()
    yield
    await engine.dispose()
    print('finish')


app.cleanup_ctx.append(init_orm)
app.middlewares.append(session_middleware)

def get_http_error(error_class, message):
    error = error_class(
        body=json.dumps({"error": message}), content_type="application/json")
    return error

async def get_article_by_id(session: Session, article_id: int):
    article = await session.get(Article, article_id)
    if article in None:
        raise get_http_error(web.HTTPNotFound, f"The {article_id=} is not found")
    return article

async def add_article(session: Session, article: Article):
    try:
        session.add(article)
        await session.commit()
    except IntegrityError as error:
        raise get_http_error(web.HTTPConflict, "Article already exists")
    return article


class ArticleView(web.View):

    @property
    def article_id(self):
        return int(self.request.match_info['article_id'])
    

    async def get_current_article(self):
        return await get_article_by_id(self.request.session, self.article_id)

    async def get(self):
        article = await self.get_current_article()

    async def post(self):
        json_data = await self.request.json()
        article = Article(**json_data)
        article = await add_article(self.request.session, article)
        return web.json_response({'id': article.id})


    async def patch(self):
        json_data = await self.request.json()
        article = await self.get_current_article()
        for field, value in json_data.items():
            setattr(article, field, value)
        article = await add_article(self.request.session, article)
        return web.json_response({'id': article.dict})

    async def delete(self):
        article = await self.get_current_article()



async def hello_world(request):
    return web.json_response({'hello': 'world'})





app.add_routes((
    web.get('/', hello_world),
    web.post('/api', ArticleView),
    web.get('/api/{article_id:\d+}', ArticleView),
    web.patch('/api/{article_id:\d+}', ArticleView),
    web.delete('/api/{article_id:\d+}', ArticleView)
    ))

web.run_app(app)