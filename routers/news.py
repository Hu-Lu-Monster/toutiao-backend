from fastapi import APIRouter,Query,Depends,HTTPException,status
from fastapi.params import Depends
from sqlalchemy import Null
from sympy import categories
from sqlalchemy.ext.asyncio import AsyncSession
from crud import news, news_cache
from config.db_conf import get_db
#创建APIRouter实例
#tags：分组标签
router = APIRouter(prefix="/api/news", tags=["news"])

#接口实现流程
#模块化路由 API接口规范文档
#定义模型类  参照数据库表结构去定义
#在crud里面创建文件 封装操作数据库的方法
#在路由处理函数里面调用 响应结果

#获取新闻分类
@router.get("/categories" )
async def get_categories(db:AsyncSession = Depends(get_db),skip: int = 0, limit: int = 100):
    categories = await news_cache.get_categories(db,skip, limit)
    return {
        "code": 200,
        "msg": "success",
        "data": categories
    }

#获取新闻列表
@router.get("/list" )
async def get_news_list(
        category_id : int = Query(...,alias="categoryId"),               #alias 别名 与数据库里的列名对齐
        page: int = 1,
        page_size: int = Query(10,le = 100,alias="pageSize"),
        db: AsyncSession = Depends(get_db)
):
    #处理分页规则->查询新闻列表->计算总量->计算是否还有更多
    offset = (page-1) * page_size
    news_list = await news_cache.get_news_list(db,category_id,offset,page_size)
    total = await news.get_news_count(db,category_id)
    hasMore = (offset + len(news_list)) < total
    return {
        "code": 200,
        "msg": "success",
        "data": {
            "list": news_list,
            "total":total,
            "hasMore":hasMore
        }
    }

#获取新闻详情 并将浏览量+1 并获取相关新闻
@router.get("/detail" )
async def get_news_detail(
        news_id : int = Query(...,alias="id"),
        db: AsyncSession = Depends(get_db)
):
    news_detail = await news.get_news_detail(db, news_id)
    #判空 如果查询失败
    if not news_detail:
        raise HTTPException(status_code=404,detail="新闻不存在")
    #浏览量+1
    views_res = await  news.add_news_views(db,news_id)
    if not views_res:
        raise HTTPException(status_code=404,detail="新闻不存在")
    category_id = news_detail.category_id
    related_news = await news_cache.get_related_news(db,category_id,news_id)
    return {
        "code": 200,
        "msg": "success",
        "data": {
            "id": news_detail.id,
            "title":news_detail.title,
            "content":news_detail.content,
            "image":news_detail.image,
            "author":news_detail.author,
            "publishTime":news_detail.publish_time,
            "categoryId":news_detail.category_id,
            "views":news_detail.views, #浏览量
            "relatedNews":related_news
        }
    }