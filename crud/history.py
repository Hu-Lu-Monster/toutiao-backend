from unittest import result
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,delete,update,func
from datetime import datetime
from models.favorite import Favorite
from models.history import History
from models.news import News


#在某用户账户下添加一条浏览历史记录
async  def add_history(
        db : AsyncSession,
        new_id: int,
        user_id: int
):
    #检查是否是浏览过的新闻
    query = select(History).where(History.news_id == new_id,History.user_id == user_id)
    result = await db.execute(query)
    history = result.scalar_one_or_none()
    #如果命中了 确实有这条新闻 那么更新时间
    if history is not None:
        query = (update(History)
                 .where(History.news_id == new_id,History.user_id == user_id)
                 .values(view_time = datetime.now()))
        await db.execute(query)
    #如果没命中  新建一个history类添加进入数据库
    else:
        history = History(news_id=new_id, user_id=user_id)
        db.add(history)
    await db.commit()
    await db.refresh(history)
    return history

#获取某用户的全部浏览历史
async def get_history_list(
        db : AsyncSession,
        user_id: int,
        page: int,
        page_size: int
):
    #获取总数
    query = select(func.count()).where(History.user_id==user_id)
    result = await db.execute(query)
    sum = result.scalar_one()

    #联表查询浏览历史信息
    query = (
        select(News,History.view_time,History.id.label('history_id'))
        .join(History,News.id == History.news_id)
        .where(History.user_id == user_id)
        .order_by(History.view_time.desc())
        .offset((page-1)*page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    rows = result.all()
    return sum, rows

#删除某用户的一条浏览记录
async def delete_history(
        db : AsyncSession,
        user_id: int,
        news_id: int
):
    #查看这条记录是否存在
    query = delete(History).where(History.user_id == user_id,History.news_id == news_id)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount > 0

#清空浏览记录
async def clear_history(
        db : AsyncSession,
        user_id: int
):
    query = delete(History).where(History.user_id == user_id)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount > 0