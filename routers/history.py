from fastapi import APIRouter, Depends, HTTPException,Query
from models.history import History
from utils.auth import get_current_user
from utils.response import success_response
from models.users import User
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import get_db
from crud import history
from  schemas.history import HistoryAddRequest


router = APIRouter(prefix="/api/history",tags=["history"])

#添加浏览记录
@router.post("/add")
async def add_history(
        news:HistoryAddRequest,
        #确认登录
        user:User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await history.add_history(db,news.news_id, user.id)
    return success_response(msg = "添加浏览历史成功",data=result)

#获取浏览历史列表
@router.get("/list")
async def get_history_list(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1,le=100,alias="pageSize"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    sum,rows = await history.get_history_list(db,user.id, page, page_size)
    hasMore = page * page_size < sum
    history_list = [{
        **news.__dict__,
        "viewTime": view_time,
        "historyId": history_id

    }for news,view_time,history_id in rows]
    data = {
        "list": history_list,
        "sum": sum,
        "hasMore": hasMore
    }
    return success_response(msg = "获取新闻列表成功",data = data)

#删除一条历史记录
@router.delete("/delete/{news_id}")
async def delete_history(
        news_id: int,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await history.delete_history(db,user.id, news_id)
    if not result:
        raise HTTPException(status_code=404,detail="浏览记录不存在")
    return success_response(msg = "删除浏览记录成功")

#清空浏览历史
@router.delete("/clear")
async def clear_history(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await history.clear_history(db,user.id)
    if not result:
        raise HTTPException(status_code=404,detail="用户浏览记录不存在")

    return success_response(msg = "清空成功")
