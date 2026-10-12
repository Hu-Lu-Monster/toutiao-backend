from fastapi import FastAPI, HTTPException
from torch.distributed.elastic.multiprocessing.errors import error_handler

from  utils.exception import http_exception_handler,integrity_error_handler,sqlalchemy_error_handler,general_exception_handler
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


def register_exception_handlers(app):
    """
    注册全局异常：子类在前 父类在后 具体在前 抽象在后
    """
    app.add_exception_handler(HTTPException,http_exception_handler) #业务层面
    app.add_exception_handler(IntegrityError,integrity_error_handler)  #数据完整性约束
    app.add_exception_handler(SQLAlchemyError,sqlalchemy_error_handler) #数据库层面错误
    app.add_exception_handler(Exception,general_exception_handler)  #其余错误