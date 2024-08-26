import logging

import uvicorn

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from starlette import status
from starlette.middleware.cors import CORSMiddleware

from src.env_variables.env import env_variables
from src.routers.catalogs import catalogs_router
from src.routers.cron_tasks import cron_router
from src.shared.exceptions import HttpException, http_response_exception_handler, internal_server_exception_handler, \
    request_validation_error_exception_handler, auth_exception_handler, AuthException
from src.shared.generics import ErrorResponse, Error, ValidationError
from src.routers.auth import auth_router
from src.routers.product import product_router
from src.routers.user import user_router
from src.routers.stripe_router import stripe_router

# logging.basicConfig(level=logging.DEBUG)

app = FastAPI(responses={
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": Error[ErrorResponse], 'description': 'Internal Error'},
    status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": Error[ValidationError], 'description': 'Validation Error'}
})

app.version = '1.0.0'
app.title = 'AnyCommerce API'

origins = [
    env_variables.origin
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix='/auth')
app.include_router(user_router, prefix='/user')
app.include_router(product_router, prefix='/products')
app.include_router(stripe_router, prefix='/stripe')
app.include_router(catalogs_router, prefix='/catalogs')
app.include_router(cron_router, include_in_schema=False)

app.add_exception_handler(HttpException, http_response_exception_handler)
app.add_exception_handler(Exception, internal_server_exception_handler)
app.add_exception_handler(RequestValidationError, request_validation_error_exception_handler)
app.add_exception_handler(AuthException, auth_exception_handler)

if __name__ == '__main__':
    uvicorn.run(app="main:app", host=env_variables.host, port=int(env_variables.port), reload=True)
