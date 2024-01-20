import json

import pydantic
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select

from aiohttp import web
from models import Article, Session, engine, init_db
from schem import CreateArticle, UpdateArticle


async def validate(schema_class, json_data):
    try:
        return schema_class(**json_data).dict(exclude_unset=True)
    except pydantic.ValidationError as er:
        error = er.errors()[0]
        error.pop("ctx", None)
        raise get_http_error(web.HTTPNotFound, "The query has not validated")


app = web.Application(debug=True)


@web.middleware
async def session_middleware(request: web.Request, handler):
    async with Session() as session:
        request.session = session
        response = await handler(request)
        return response


async def init_orm(app: web.Application):
    print("start")
    await init_db()
    yield
    await engine.dispose()
    print("finish")


app.cleanup_ctx.append(init_orm)
app.middlewares.append(session_middleware)


def get_http_error(error_class, message):
    error = error_class(
        body=json.dumps({"error": message}), content_type="application/json"
    )
    return error


async def get_article_by_id(session: Session, article_id: int):
    article = await session.get(Article, article_id)
    if article is None:
        raise get_http_error(web.HTTPNotFound, f"The {article_id} is not found")
    return article


async def get_all_articles(session: Session):
    articles = await session.execute(select(Article))
    articles = articles.scalars()
    result = dict()
    for i in articles:
        result[i.id] = {
            "article": i.article,
            "description": i.description,
            "date_pub": str(i.date_pub),
            "owner": i.owner,
        }
    return result


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
        return int(self.request.match_info["article_id"])

    async def get_current_article(self):
        return await get_article_by_id(self.request.session, self.article_id)

    async def get(self):
        article = await self.get_current_article()
        return web.json_response(article.json)

    async def post(self):
        json_data = await validate(CreateArticle, await self.request.json())
        article = Article(**json_data)
        article = await add_article(self.request.session, article)
        return web.json_response({"id": article.id})

    async def patch(self):
        json_data = await validate(UpdateArticle, await self.request.json())
        article = await self.get_current_article()
        for field, value in json_data.items():
            setattr(article, field, value)
        article = await add_article(self.request.session, article)
        return web.json_response({"patched": article.json})

    async def delete(self):
        article = await self.get_current_article()
        await self.request.session.delete(article)
        await self.request.session.commit()
        return web.json_response({"article": "deleted"})


async def get_articles(request):
    articles = await get_all_articles(request.session)
    return web.json_response(articles)


app.add_routes(
    (
        web.get("/api", get_articles),
        web.post("/api", ArticleView),
        web.get("/api/{article_id:\d+}", ArticleView),
        web.patch("/api/{article_id:\d+}", ArticleView),
        web.delete("/api/{article_id:\d+}", ArticleView),
    )
)

web.run_app(app)
