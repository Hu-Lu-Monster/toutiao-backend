from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,delete,func
from models.users import User
from models.news import News
from models.favorite import Favorite

#检查当前用户是否收藏了这一条新闻
async def is_news_favorite(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    query = select(Favorite).where(Favorite.user_id == user_id,Favorite.news_id == news_id)
    result = await db.execute(query)
    #是否有收藏记录 返回一个布尔值
    return result.scalar_one_or_none() is not None

#添加一条用户收藏的新闻
async def add_favorite(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    #构造一个orm对象
    favorite = Favorite(user_id = user_id,news_id= news_id)
    #添加到数据库中
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite

#取消一条用户收藏的新闻
async def delete_favorite(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    query = delete(Favorite).where(Favorite.user_id == user_id,
                                   Favorite.news_id == news_id)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount > 0

#获取一个用户的收藏的全部新闻信息列表
async def get_favorite_list(
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        page_size: int = 10
):
    #获取收藏列表
    query = select(func.count()).where(Favorite.user_id == user_id)
    result = await db.execute(query)
    sum = result.scalar_one()

    #联表查询 收藏的新闻列表
    query = (
        select(News,Favorite.created_at.label("favorite_time"),Favorite.id.label("favorite_id"))
        .join(Favorite,Favorite.news_id == News.id)
        .where(Favorite.user_id == user_id)
        .order_by(Favorite.created_at.desc())
        .offset((page-1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    rows = result.all()
    return rows,sum

#清空一个用户的收藏列表
async def clear_favorite(
        db: AsyncSession,
        user_id: int
):
    query = delete(Favorite).where(Favorite.user_id == user_id)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount or 0