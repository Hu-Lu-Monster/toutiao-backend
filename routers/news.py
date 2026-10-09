from fastapi import APIRouter
from sympy import categories

#创建APIRouter实例
router = APIRouter(prefix="/api/news", tags=["news"])

@router.get("/categories" )
async def get_categories():
    return {"msg": "获取分类成功"}