from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_conf import get_db
from crud.users import get_user_by_token
from fastapi import APIRouter, HTTPException,Header,Depends
#整合 根据token查询用户 返回用户
async def get_current_user(
        authorization: str = Header(...,alias="Authorization"),
        db:AsyncSession = Depends(get_db)
):
    token = authorization.strip()
    user = await get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="无效令牌或过期令牌")
    return user
