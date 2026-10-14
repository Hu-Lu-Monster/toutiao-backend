from fastapi import HTTPException
from models.users import User, UserToken
from sqlalchemy import select,update
from sqlalchemy.ext.asyncio import AsyncSession
from utils import security
import uuid
from datetime import datetime, timedelta
from schemas.users import UserUpdateResponse,UserChangePwdRequest

#根据用户名查询数据库
async def get_user_by_username(db: AsyncSession,username: str):
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    return result.scalar_one_or_none()

#创建用户
async def create_user(db: AsyncSession,username: str,password: str):
    #先把密码加密处理 passlib加密
    hashed_password = security.get_hash_password(password)
    user = User(username=username, password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user) #从数据库读回最新的user
    return user

#生成token
async def create_token(db: AsyncSession,user_id: int):
    # 先生成token并设置过期时间 再查询数据库当前用户是否有token  如果有 更新 如果没有 添加
    token = str(uuid.uuid4())
    #过期时间
    expires_at = datetime.now() + timedelta(days=7)
    query = select(UserToken).where(UserToken.user_id == user_id)
    result = await db.execute(query)
    user_token = result.scalar_one_or_none()
    if user_token:
        user_token.token = token
    else:
        user_token = UserToken(user_id=user_id, token=token,expires_at=expires_at)
        db.add(user_token)
        await db.commit()
    return token

#验证用户
async def authenticate_user(db: AsyncSession,username: str,password: str):
    user = await get_user_by_username(db, username)
    if not user:
        return None
    if not security.verify_password(password,user.password):
        return None
    return user

#根据token来查询用户
async def get_user_by_token(db: AsyncSession,token: str):
    query = select(UserToken).where(UserToken.token == token)
    result = await db.execute(query)
    db_token = result.scalar_one_or_none()
    #验证token是否存在并且有效
    if not db_token or db_token.expires_at < datetime.now():
        return None
    #有效 查询用户信息
    query = select(User).where(User.id == db_token.user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

#更改用户信息
async def update_user_info(db: AsyncSession,username:str,user_data: UserUpdateResponse):
    query = update(User).where(User.username == username).values(**user_data.model_dump(
        exclude_unset=True,
        exclude_none=True,        #有值的才更新到数据库 这样如果用户不设置值 不会更新为默认值
    ))
    result = await db.execute(query)
    await db.commit()

    #检查更新
    if result.rowcount == 0:
        raise HTTPException(status_code=404,detail="用户不存在")

    #获取更新后的用户
    update_user = await get_user_by_username(db, username)
    return update_user

#更改密码
async def update_password(db: AsyncSession,user:User,password_data : UserChangePwdRequest):
    #验证旧密码
    if not security.verify_password(password_data.oldPassword,user.password):
        return False
    #加密新密码
    #注意这里 也可以直接给user.password赋值让他等于hashed_newPassword orm操作 然后提交的时候sqlalchemy会自动更新数据库变化
    hashed_newPassword = security.get_hash_password(password_data.newPassword)
    query = update(User).where(User.username == user.username).values(password = hashed_newPassword)
    result = await db.execute(query)
    await db.commit()
    await db.refresh(user)
    return True
