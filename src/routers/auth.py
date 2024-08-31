from datetime import timedelta, timezone, datetime
from typing import Annotated

import stripe
from fastapi import APIRouter, Depends, Form, Query
from fastapi import status
from jose import jwt, ExpiredSignatureError, JWTError
from passlib.context import CryptContext

from dependencies.auth import get_current_user, validate_api_key
from src.database.mongodb.collection.session_token_collection import insert_session_token, \
    get_session_token, update_session_token_with_id, remove_session_token, remove_many_sessions_token
from src.database.mongodb.collection.user_collection import get_user_by_email, insert_user
from src.database.mongodb.schema.session_token_schema import SessionTokenCollectionSchema
from src.env_variables.env import env_variables
from src.models.request.user import UserRequest
from src.models.responses.token import TokenResponse
from src.models.user import BaseUserModel
from src.shared.exceptions import HttpException, AuthException
from src.shared.generics import ErrorResponse, Error, Data, MessageResponse
from src.utils.constants import ErrorsIDs, ErrorsDescriptions, Params, ResponseDescriptions, ErrorsDescriptionsObject

auth_router = APIRouter(tags=['Auth'])
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
stripe.api_key = env_variables.stripe_secret_key


@auth_router.post('/sign-up', responses={
    status.HTTP_201_CREATED: {"model": Data[MessageResponse], 'description': 'User Created'},
    status.HTTP_400_BAD_REQUEST: {"model": Error[ErrorResponse], 'description': 'Bad Request Error'}
}, status_code=status.HTTP_201_CREATED)
def create_new_user(
        new_user: UserRequest,
        _: str = Depends(validate_api_key)
):
    try:
        user_exists = get_user_by_email(email=new_user.email.value) is not None

        if user_exists:
            raise HttpException(status_code=status.HTTP_400_BAD_REQUEST, error_id=ErrorsIDs.EMAIL_USER_EXISTS,
                                description=ErrorsDescriptions.EMAIL_USER_EXISTS.value.format(new_user.email.value))

        new_stripe_user = stripe.Customer.create(
            email=new_user.email.value,
            name=f"{new_user.name} {new_user.lastName}"
        )

        new_user.password = pwd_context.hash(new_user.password)
        new_user.stripeId = new_stripe_user.id

        insert_user(new_user.to_schema())

        return Data[MessageResponse](data=MessageResponse(message=ResponseDescriptions.USER_CREATED_SUCCESS))

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
        username: str = Form(alias='username'),
        password: str = Form(alias='password')
):
    try:
        user = get_user_by_email(username)

        if not user:
            raise HttpException(
                status_code=status.HTTP_400_BAD_REQUEST,
                error_id=ErrorsIDs.EMAIL_OR_PASSWORD_INVALID,
                description=ErrorsDescriptions.EMAIL_OR_PASSWORD_INVALID
            )

        is_password_valid = pwd_context.verify(password, user.password)

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
                sub=user.email.value
            ),
            key=env_variables.auth_secret_key,
            algorithm=env_variables.auth_algorithm
        )

        refresh_token = jwt.encode(
            claims=dict(
                exp=refresh_token_expires,
                sub=user.email.value
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

        insert_session_token(session_token=SessionTokenCollectionSchema(
            username=user.email.value,
            session_date=datetime.now(),
            data=token.to_schema()
        ))

        return Data[TokenResponse](data=token)

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
        refresh_token: str = Query(alias="refreshToken"), _: str = Depends(validate_api_key)
):
    try:
        token = get_session_token(refresh_token=refresh_token)

        if not token:
            raise AuthException(
                error_id=ErrorsIDs.REFRESH_TOKEN_NOT_VALID,
                description=ErrorsDescriptions.REFRESH_TOKEN_NOT_VALID
            )

        try:
            jwt.decode(
                token=token.data.refreshToken,
                key=env_variables.auth_secret_key,
                algorithms=[env_variables.auth_algorithm]
            )
        except ExpiredSignatureError as err:
            remove_session_token(refresh_token=token.data.refreshToken)
            raise AuthException(error_id=ErrorsIDs.REFRESH_TOKEN_EXPIRED,
                                description=ErrorsDescriptionsObject[ErrorsIDs.REFRESH_TOKEN_EXPIRED]
                                )

        except JWTError as err:
            remove_session_token(refresh_token=token.data.refreshToken)
            raise AuthException(
                error_id=ErrorsIDs.REFRESH_TOKEN_COULD_NOT_BE_VALIDATED,
                description=ErrorsDescriptionsObject[ErrorsIDs.REFRESH_TOKEN_COULD_NOT_BE_VALIDATED]
            )

        access_token_expires = datetime.now(timezone.utc) + timedelta(minutes=Params.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = datetime.now(timezone.utc) + timedelta(minutes=Params.REFRESH_TOKEN_EXPIRE_MINUTES)

        encoded_jwt = jwt.encode(
            claims=dict(
                exp=access_token_expires,
                sub=token.username
            ),
            key=env_variables.auth_secret_key,
            algorithm=env_variables.auth_algorithm
        )

        refresh_token = jwt.encode(
            claims=dict(
                exp=refresh_token_expires,
                sub=token.username
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

        update_session_token_with_id(
            token_id=token.id,
            session_token=SessionTokenCollectionSchema(
                username=token.username,
                session_date=datetime.now(),
                data=new_token.to_schema()
            ))

        return Data[TokenResponse](
            data=new_token
        )

    except HttpException as ex:
        raise ex

    except Exception as ex:
        raise ex


@auth_router.post('/sign-out', responses={
    status.HTTP_200_OK: {"model": Data[MessageResponse], 'description': 'Sign Out Successfully'},
}, status_code=status.HTTP_200_OK)
def sign_out(
        current_user: Annotated[BaseUserModel, Depends(get_current_user)]
):
    try:
        token = get_session_token(username=current_user.email.value)

        if token:
            remove_many_sessions_token(username=current_user.email.value)

        return Data[MessageResponse](
            data=MessageResponse(message=ResponseDescriptions.USER_SIGNED_OUT_SUCCESS)
        )

    except HttpException as ex:
        raise ex

    except Exception as ex:
        raise ex
