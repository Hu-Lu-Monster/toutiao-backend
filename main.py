from fastapi import FastAPI
#
from fastapi.middleware.cors import CORSMiddleware
from routers import news, users, favorite,history
from utils.exception_handlers import register_exception_handlers

app = FastAPI()

#注册异常处理器 如果真的有异常 现在是它来接管报错
register_exception_handlers(app)

@app.get("/")
async def root():
    return {"message": "Hello World"}

#挂载路由
app.include_router(news.router)

#允许的来源
#同源的三个要求 协议 域名 端口
origins = [
##正常来说 允许访问的源地址写这里 在下面添加的时候再引用
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],     #允许访问的源
    allow_credentials = True,   #允许携带cookie
    allow_methods = ["*"],       #允许访问的方法
    allow_headers = ["*"],       #允许访问的请求头
)

#挂载路由
app.include_router(users.router)

#挂载收藏路由
app.include_router(favorite.router)

#挂载浏览历史路由
app.include_router(history.router)
