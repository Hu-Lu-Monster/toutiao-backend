from fastapi import APIRouter,Depends,HTTPException,status,Query
from pip._internal.cli import status_codes

from utils.auth import get_current_user
from models.users import User
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import get_db
from utils.response import success_response
from crud import favorite
from schemas.favorite import FavoriteCheckResponse,FavoriteAddRequest,FavoriteDelRequest,FavoriteListResponse
router = APIRouter(prefix="/api/favorite",tags=["favorite"])

#判断用户是否收藏此条信息
#验证用户登录 检查用户是否收藏当前新闻 响应结果
@router.get("/check")
async def check_favorite(
        news_id:int = Query(...,alias="newsId"),
        user : User = Depends(get_current_user),
        db:AsyncSession = Depends(get_db)
):
    is_favorited = await favorite.is_news_favorite(db,user.id,news_id)
    return success_response(msg = "获取收藏信息成功",data = FavoriteCheckResponse(isFavorite = is_favorited))

#添加收藏
@router.post("/add")
async def add_favorite(
        data: FavoriteAddRequest,
        user : User = Depends(get_current_user),
        db:AsyncSession = Depends(get_db)
):
    result = await favorite.add_favorite(db,user.id,data.news_id)
    return  success_response(msg = "添加收藏成功",data = result)

#取消收藏
@router.delete("/remove")
async def delete_favorite(
        news_id:int = Query(...,alias="newsId"),
        user : User = Depends(get_current_user),
        db:AsyncSession = Depends(get_db)
):
    result = await  favorite.delete_favorite(db,user.id,news_id)
    if not result:
        raise HTTPException(status_codes = status.HTTP_404_NOT_FOUND,detail = "收藏记录不存在")
    return success_response(msg = "取消收藏成功")

#获取收藏列表
@router.get("/list")
async def get_favorite_list(
        page: int = Query(1,ge = 1),
        page_size: int = Query(10,ge = 1,le = 100,alias="pageSize"),
        user: User = Depends(get_current_user),
        db:AsyncSession = Depends(get_db)
):
    rows,sum = await favorite.get_favorite_list(db,user.id,page,page_size)
    favorite_list = [{
        **news.__dict__,
        "favorite_time":favorite_time,
        "favorite_id":favorite_id,
    }for news,favorite_time,favorite_id in rows]

    has_more = sum > page * page_size
    data = FavoriteListResponse(list = favorite_list,sum = sum,has_more = has_more)
    return success_response(msg = "获取收藏列表成功",data = data)

#清空收藏列表
@router.delete("/clear")
async def clear_favorite(
        #确认登录
        user: User = Depends(get_current_user),
        db:AsyncSession = Depends(get_db)
):
    count = await favorite.clear_favorite(db,user.id)
    return success_response(msg = f"清空{count}条信息成功")