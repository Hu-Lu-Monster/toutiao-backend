from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

#成功响应格式
def success_response(msg: str = "success",data = None):
    #把任何的FastAPI、pydantic、ORM对象 都要正常响应
    content = {
        "code": 200,
        "msg": msg,
        "data": data
    }
    return JSONResponse(content = jsonable_encoder(content))
