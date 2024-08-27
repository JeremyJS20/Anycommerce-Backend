import secrets
from datetime import timedelta, timezone, datetime
from typing import Annotated, Any, Mapping

import stripe
from fastapi import APIRouter, Depends, Form, Query
from fastapi import status
from jose import jwt, ExpiredSignatureError, JWTError
from passlib.context import CryptContext
from pymongo.database import Database

from dependencies.auth import get_current_user, validate_api_key
from dependencies.mongodb import MongoDBClient
from src.env_variables.env import env_variables
from src.models.responses.auth import SignUpResponse
from src.models.responses.token import TokenResponse
from src.models.user import BaseUserModel, CreateUserModel
from src.shared.exceptions import HttpException, AuthException
from src.shared.generics import ErrorResponse, Error, Data, MessageResponse
from src.utils.constants import ErrorsIDs, ErrorsDescriptions, Params, ResponseDescriptions, ErrorsDescriptionsObject

auth_router = APIRouter(tags=['Auth'])


@auth_router.post('/sign-up', responses={
    status.HTTP_201_CREATED: {"model": Data[SignUpResponse], 'description': 'User Created'},
    status.HTTP_400_BAD_REQUEST: {"model": Error[ErrorResponse], 'description': 'Bad Request Error'}
}, status_code=status.HTTP_201_CREATED)
def create_new_user(
        user: CreateUserModel,
        _: str = Depends(validate_api_key),
        mongo_client: Database[Mapping[str, Any]] = Depends(MongoDBClient())
):
    pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
    stripe.api_key = env_variables.stripe_secret_key
    try:
        user_exists = mongo_client.user.find_one({'email.value': user.email.value}) is not None

        if user_exists:
            raise HttpException(status_code=status.HTTP_400_BAD_REQUEST, error_id=ErrorsIDs.EMAIL_USER_EXISTS,
                                description=ErrorsDescriptions.EMAIL_USER_EXISTS.value.format(user.email.value))

        stripe_user = stripe.Customer.create(
            email=user.email.value,
            name=f"{user.name} {user.lastName}"
        )

        user.password = pwd_context.hash(user.password)
        user.stripeId = stripe_user.id

        user_id = mongo_client.user.insert_one(user.to_schema()).inserted_id

        return Data[SignUpResponse](
            data=SignUpResponse(userId=str(user_id)).to_json()
        )

    except HttpException as ex:
        raise ex

    except Exception as ex:
        raise ex


@auth_router.post('/sign-in', responses={
    status.HTTP_200_OK: {"model": Data[TokenResponse], 'description': 'Success Authentication'},
    status.HTTP_400_BAD_REQUEST: {"model": Error[ErrorResponse], 'description': 'Bad Request Error'}

}, status_code=status.HTTP_200_OK)
def sign_in(
        _: str = Depends(validate_api_key),
        mongo_client: Database[Mapping[str, Any]] = Depends(MongoDBClient()),
        username: str = Form(alias='username'),
        password: str = Form(alias='password')
):
    pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

    try:
        user = mongo_client.user.find_one({'email.value': username})

        if not user:
            raise HttpException(
                status_code=status.HTTP_400_BAD_REQUEST,
                error_id=ErrorsIDs.EMAIL_OR_PASSWORD_INVALID,
                description=ErrorsDescriptions.EMAIL_OR_PASSWORD_INVALID
            )

        is_password_valid = pwd_context.verify(password, user['password'])

        if not is_password_valid:
            raise HttpException(
                status_code=status.HTTP_400_BAD_REQUEST,
                error_id=ErrorsIDs.EMAIL_OR_PASSWORD_INVALID,
                description=ErrorsDescriptions.EMAIL_OR_PASSWORD_INVALID
            )

        access_token_expires = datetime.now(timezone.utc) + timedelta(minutes=Params.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = datetime.now(timezone.utc) + timedelta(minutes=Params.REFRESH_TOKEN_EXPIRE_MINUTES)

        encoded_jwt = jwt.encode(
            claims=dict(
                exp=access_token_expires,
                sub=user['email']['value']
            ),
            key=env_variables.auth_secret_key,
            algorithm=env_variables.auth_algorithm
        )

        refresh_token = jwt.encode(
            claims=dict(
                exp=refresh_token_expires,
                sub=user['email']['value']
            ),
            key=env_variables.auth_secret_key,
            algorithm=env_variables.auth_algorithm
        )

        token = TokenResponse(
            accessToken=encoded_jwt,
            tokenType='bearer',
            expiresIn=access_token_expires,
            refreshToken=refresh_token
        )

        mongo_client.session_token.insert_one(
            dict(
                username=user['email']['value'],
                session_date=datetime.now(),
                data=token.to_schema()
            )
        )

        return Data[TokenResponse](
            data=token.to_json()
        )

    except HttpException as ex:
        raise ex

    except Exception as ex:
        raise ex


@auth_router.get('/current-user', responses={
    status.HTTP_200_OK: {"model": Data[BaseUserModel], 'description': 'User Authenticated'},
}, status_code=status.HTTP_200_OK)
def get_auth_current_user(current_user: Annotated[BaseUserModel, Depends(get_current_user)]):
    return Data[BaseUserModel](
        data=current_user.to_json()
    )


@auth_router.put('/refresh-token', responses={
    status.HTTP_200_OK: {"model": Data[TokenResponse], 'description': 'Refreshed Token'},
    status.HTTP_400_BAD_REQUEST: {"model": Error[ErrorResponse], 'description': 'Bad Request Error'}
}, status_code=status.HTTP_200_OK)
def refresh_access_token(
        refresh_token: str = Query(alias="refreshToken"), _: str = Depends(validate_api_key),
        mongo_client: Database[Mapping[str, Any]] = Depends(MongoDBClient())
):
    try:
        token = mongo_client.session_token.find_one({'data.refresh_token': refresh_token})

        if not token:
            raise AuthException(
                error_id=ErrorsIDs.REFRESH_TOKEN_NOT_VALID,
                description=ErrorsDescriptions.REFRESH_TOKEN_NOT_VALID
            )

        token_data = token['data']

        try:
            jwt.decode(
                token=token_data['refresh_token'],
                key=env_variables.auth_secret_key,
                algorithms=[env_variables.auth_algorithm]
            )
        except ExpiredSignatureError as err:
            mongo_client.session_token.delete_one({'data.refresh_token': token_data['refresh_token']})
            raise AuthException(error_id=ErrorsIDs.REFRESH_TOKEN_EXPIRED,
                                description=ErrorsDescriptionsObject[ErrorsIDs.REFRESH_TOKEN_EXPIRED]
                                )

        except JWTError as err:
            mongo_client.session_token.delete_one({'data.refresh_token': token_data['refresh_token']})
            raise AuthException(
                error_id=ErrorsIDs.REFRESH_TOKEN_COULD_NOT_BE_VALIDATED,
                description=ErrorsDescriptionsObject[ErrorsIDs.REFRESH_TOKEN_COULD_NOT_BE_VALIDATED]
            )

        access_token_expires = datetime.now(timezone.utc) + timedelta(minutes=Params.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = datetime.now(timezone.utc) + timedelta(minutes=Params.REFRESH_TOKEN_EXPIRE_MINUTES)

        encoded_jwt = jwt.encode(
            claims=dict(
                exp=access_token_expires,
                sub=token['username']
            ),
            key=env_variables.auth_secret_key,
            algorithm=env_variables.auth_algorithm
        )

        refresh_token = jwt.encode(
            claims=dict(
                exp=refresh_token_expires,
                sub=token['username']
            ),
            key=env_variables.auth_secret_key,
            algorithm=env_variables.auth_algorithm
        )

        new_token = TokenResponse(
            accessToken=encoded_jwt,
            tokenType='bearer',
            expiresIn=access_token_expires,
            refreshToken=refresh_token
        )

        mongo_client.session_token.update_one(
            {"_id": token['_id']},
            {"$set": dict(
                username=token['username'],
                session_date=datetime.now(),
                data=new_token.to_schema()
            )}
        )

        return Data[TokenResponse](
            data=new_token.to_json()
        )

    except HttpException as ex:
        raise ex

    except Exception as ex:
        raise ex


@auth_router.post('/sign-out', responses={
    status.HTTP_200_OK: {"model": Data[MessageResponse], 'description': 'Sign Out Successfully'},
}, status_code=status.HTTP_200_OK)
def sign_out(
        current_user: Annotated[BaseUserModel, Depends(get_current_user)],
        mongo_client: Database[Mapping[str, Any]] = Depends(MongoDBClient())
):
    try:
        token = mongo_client.session_token.find_one({'username': current_user.email.value})

        if token:
            mongo_client.session_token.delete_many({'username': current_user.email.value})

        return Data[MessageResponse](
            data=MessageResponse(message=ResponseDescriptions.USER_SIGNED_OUT_SUCCESS).to_json()
        )

    except HttpException as ex:
        raise ex

    except Exception as ex:
        raise ex
