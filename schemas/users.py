import xxsubtype
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class UserRequest(BaseModel):
    username: str
    password: str


class UserInfoBase(BaseModel):
    """用户信息基础数据模型。"""
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")

#user_info对应的类:基础类+Info类
class UserInfoResponse(UserInfoBase):
    id: int
    username: str
    #模型类配置
    # 模型类配置
    model_config = ConfigDict(
        from_attributes=True,  # 允许从orm对象中取值
    )

#data 数据类型
class UserAuthResponse(BaseModel):
    token: str
    user_info: UserInfoResponse = Field(...,alias="userInfo")

    #模型类配置
    model_config = ConfigDict(
        populate_by_name=True,#别名与字段名兼容
        from_attributes=True,#允许从orm对象中取值
    )

#更新用户信息的模型类
class UserUpdateResponse(BaseModel):
    nickname: str = None
    avatar: str = None
    gender: str = None
    bio: str = None
    phone : str = None

    #修改密码的模型类
class UserChangePwdRequest(BaseModel):
    oldPassword: str = Field(...,alias = "oldPassword",description = "旧密码")
    newPassword: str = Field(...,min_length = 6, alias = "newPassword",description = "新密码")