#存放新闻相关的缓存方法:新闻分类的读取和写入
from _pyrepl import keymap

from torch._dynamo import resume_execution

CATEGORIES_KEY = "news:categories"
NEWS_LIST_PRIFIX = "news_list"

from typing import List, Dict, Any, Optional
from config.cache_conf import get_cache,get_json_cache,set_cache
from fastapi import FastAPI,HTTPException
#获取新闻分类缓存
async def get_cached_categories():
    return await get_json_cache(CATEGORIES_KEY)

#写入新闻分类缓存
#分类、配置 通常过期时间7200 如果列表等 600 详情 1800 验证码 120 -- 数据越稳定 缓存越持久
async def set_cache_categories(data:List[Dict[str,Any]],expire:int = 7200):
    return await set_cache(CATEGORIES_KEY,data,expire)

#获取新闻列表缓存
async def get_cache_news_list(category_id:Optional[int],
                              page:int,
                              page_size:int):
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_PRIFIX}{category_part}:{page}:{page_size}"
    return await get_json_cache(key)

#写入新闻列表缓存
async def set_cache_news_list(category_id:Optional[int],
                              page:int,
                              page_size:int,
                              news_list:List[Dict[str,Any]],
                              expire:int = 3600
):
    #调用封装的Redis的设置方法 存新闻列表到缓存
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_PRIFIX}{category_part}:{page}:{page_size}"
    return await set_cache(key,news_list,expire)

#获取新闻推荐缓存
async def get_cache_related_news(news_id:int,category_id:Optional[int],page_size:int):
    related_news_part = f"{news_id}:{category_id}" if category_id is not None else "all"
    key = f"news:related:{related_news_part}:{page_size}"
    return await get_json_cache(key)

#写入新闻推荐缓存
async def set_cache_related_news(news_id:int,category_id:Optional[int],
                                 page_size:int,related_news:List[Dict[str,Any]],expire:int = 1800):
    related_news_part = f"{news_id}:{category_id}" if category_id is not None else "all"
    key = f"news:related:{related_news_part}:{page_size}"
    return await set_cache(key,related_news,expire)
