import select
from fastapi import APIRouter,Depends,HTTPException,status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import get_db
from schemas.users import (
    UserRequest,
    UserAuthResponse,
    UserInfoResponse,
    UserUpdateResponse,
    UserChangePwdRequest
)
from crud import users
from utils.response import success_response
from utils.auth import get_current_user
from models.users import User
from uuid import uuid4
router = APIRouter(prefix="/api/user", tags=["users"])

#用户注册
@router.post("/register")
async def register(userdata : UserRequest, db:AsyncSession = Depends(get_db)):
    #先检查输入用户是否存在 如果不存在 再创建用户 生成Token 响应结果
    #验证用户是否存在
    existing_user = await users.get_user_by_username(db, userdata.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="用户已存在")
    #创建用户
    user = await users.create_user(db, userdata.username, userdata.password)
    #生成访问令牌
    token = await users.create_token(db, user.id)
    response_data = UserAuthResponse(token=token,user_info = UserInfoResponse.model_validate(user))
    return success_response(msg="注册成功",data=response_data)

#用户登录
@router.post("/login")
async def login(login_data:UserRequest, db:AsyncSession = Depends(get_db)):
    user = await users.authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="用户名或密码错误")
    token = await users.create_token(db, user.id)
    response_data = UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(user))
    return success_response(msg="登录成功",data = response_data)

#获取用户信息
#查token 查用户 封装crud 功能整合为工具函数  路由导入使用
@router.get("/info")
async def get_user_info(user : User = Depends(get_current_user)):
    return success_response(msg="获取用户信息成功",data = UserInfoResponse.model_validate(user))

#修改用户信息
#验证token 更新用户信息 响应结果
@router.put("/update")
async def update_user_info(user_data: UserUpdateResponse,
                           user: User = Depends(get_current_user),
                           db: AsyncSession = Depends(get_db)):
    user = await users.update_user_info(db,user.username,user_data)
    return success_response(msg="修改用户信息成功",data = UserInfoResponse.model_validate(user))

#修改用户密码
#验证token 验证旧的密码 更新密码 加密 响应结果
@router.put("/password")
async def update_password(
                               password_data : UserChangePwdRequest,
                               user : User = Depends(get_current_user),
                               db: AsyncSession = Depends(get_db)):
    res_change_pwd = await users.update_password(db,user,password_data)
    if not res_change_pwd:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="修改密码失败，请稍后再试")
    return  success_response(msg="修改密码成功")
