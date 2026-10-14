from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict
from schemas import base

#新闻是否被收藏的状态类
class FavoriteCheckResponse(BaseModel):
    is_favorite: bool = Field(...,alias="isFavorite")

#要添加的收藏新闻id类
class FavoriteAddRequest(BaseModel):
    news_id: int = Field(...,alias="newsId")

#要取消的收藏新闻id类
class FavoriteDelRequest(BaseModel):
    news_id: int = Field(...,alias="newsId")

#新闻模型类+收藏模型类
class FavoriteNewsItemResponse(base.NewsItemBase):
    favorite_id: int = Field(...,alias="favoriteId")
    favorite_time: datetime = Field(...,alias="favoriteTime")
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )

#收藏列表接口响应模型类
class FavoriteListResponse(BaseModel):
    list:list[FavoriteNewsItemResponse]
    sum:int
    has_more: bool = Field(...,alias="hasMore")

    #允许别名与字段名兼容 允许从orm对象中提取属性值
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )