from fastapi.encoders import jsonable_encoder
from torch._higher_order_ops import strict_mode
from cache.news_cache import (
    get_cached_categories
, set_cache_categories
, get_cache_news_list
, set_cache_news_list, get_cache_related_news, set_cache_related_news
)
from models.news import Category, News
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,func,update
from fastapi import Depends, HTTPException

#获取新闻分类
async def get_categories(db: AsyncSession,skip: int = 0,limit: int = 100):
    #先尝试从缓存中获取数据
    cached_categories = await get_cached_categories()
    if cached_categories:
        return cached_categories
    stmt = select(Category).offset(skip).limit(limit)
    result =  await db.execute(stmt)
    categories =  result.scalars().all()
    #写入缓存
    if categories:
        categories = jsonable_encoder(categories)
        await set_cache_categories(categories)
    return  categories

#查询指定分类下的所有新闻
async def get_news_list(db: AsyncSession,category_id: int,skip: int = 0,limit: int = 10):
    #先从缓存中获取数据
    page = skip // limit + 1
    news_list = await get_cache_news_list(category_id,page,limit)
    if news_list:
        return [News(**item) for item in news_list] #要的是orm格式
    #如果没有  则从数据库中读取并存入缓存
    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    news_list = result.scalars().all()
    #写入缓存 应该是转格式 把orm转为json
    if news_list:
        news_list = jsonable_encoder(news_list)
        await set_cache_news_list(category_id,page,limit,news_list)
    return  news_list

async def get_news_count(db: AsyncSession,category_id: int):
    #查询指定分类下的新闻数量总量
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one()#必须返回一个结果  如果返回多个 就报错

async def get_news_detail(db: AsyncSession,news_id: int):
    #查询指定种类下的特定id的内容
    stmt = select(News).where(News.id == news_id)
    #update(News).where(News.id == id).values(News.views = (News.views + 1))

    result = await db.execute(stmt)
    #select(News).where(News.category_id == result.category_id and News.id != result.id)
    return result.scalar_one_or_none()

async def add_news_views(db: AsyncSession,news_id: int):
    #将查询过的新闻浏览量增加1
    stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
    result = await db.execute(stmt)
    await db.commit()
    #数据库更新
    #检查数据库是否能真的更新数据 一般更新操作要检查
    return result.rowcount > 0

async def get_related_news(db: AsyncSession,category_id: int,news_id: int,limit: int = 5):
    #先查询缓存
    related_news = await get_cache_related_news(news_id,category_id,limit)
    if related_news is not None:
        return related_news
    #查询当前类型下除了本id外的其他新闻
    stmt = select(News).where(
    News.category_id == category_id,
                          News.id != news_id
    ).order_by(
        News.views.desc()
    ).limit(limit)
    result = await db.execute(stmt)
    #return result.scalars().all()
    related_news = result.scalars().all()
    data = [{
        "id": news_detail.id,
        "title": news_detail.title,
        "content": news_detail.content,
        "image": news_detail.image,
        "author": news_detail.author,
        "publishTime": news_detail.publish_time,
        "categoryId": news_detail.category_id,
        "views": news_detail.views  # 浏览量
    } for news_detail in related_news]
    data = jsonable_encoder(data)
    await set_cache_related_news(news_id,category_id,limit,data)
    #列表推导式、推导出新闻的核心数据 再return
    return data
