from collections.abc import Mapping
from typing import Any, Optional

from fastapi import Depends
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError, ExpiredSignatureError
from pymongo.database import Database

from dependencies.mongodb import MongoDBClient
from src.env_variables.env import env_variables
from src.models.user import BaseUserModel
from src.shared.exceptions import AuthException
from src.utils.constants import ErrorsDescriptions, ErrorsIDs, ErrorsDescriptionsObject

api_key_scheme = APIKeyHeader(name="x-api-key", auto_error=False)
auth_scheme = HTTPBearer(auto_error=False)


def validate_bearer_token(
        credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
        mongo_client: Database[Mapping[str, Any]] = Depends(MongoDBClient())
):
    try:
        token = credentials.credentials
        scheme = credentials.scheme

        if not credentials:
            raise AuthException(error_id=ErrorsIDs.UNAUTHORIZED, description=ErrorsDescriptions.UNAUTHORIZED)

        if scheme.lower() != 'bearer':
            raise AuthException(error_id=ErrorsIDs.AUTH_SCHEME_NOT_VALID,
                                description=ErrorsDescriptions.AUTH_SCHEME_NOT_VALID)

        exist_token_db = mongo_client.session_token.find_one({'data.access_token': token}) is not None

        if not exist_token_db:
            raise AuthException(error_id=ErrorsIDs.AUTH_TOKEN_NOT_VALID,
                                description=ErrorsDescriptions.AUTH_TOKEN_NOT_VALID)

        payload = jwt.decode(
            token=token,
            key=env_variables.auth_secret_key,
            algorithms=[env_variables.auth_algorithm]
        )

        return payload['sub']

    except ExpiredSignatureError as err:
        raise AuthException(error_id=ErrorsIDs.AUTH_TOKEN_EXPIRED, description=ErrorsDescriptions.AUTH_TOKEN_EXPIRED)

    except JWTError as err:
        raise AuthException(
            error_id=ErrorsIDs.AUTH_TOKEN_COULD_NOT_BE_VALIDATED,
            description=ErrorsDescriptions.AUTH_TOKEN_COULD_NOT_BE_VALIDATED
        )

    except Exception as ex:
        raise ex


def get_current_user(
        current_user: str = Depends(validate_bearer_token),
        mongo_client: Database[Mapping[str, Any]] = Depends(MongoDBClient())
):
    user = mongo_client.user.find_one({'email.value': current_user})
    user_preferences = mongo_client.preferences.find_one({'user_id': str(user['_id'])})

    user_model = BaseUserModel(
        id=str(user['_id']),
        stripeId=user['stripe_id'],
        name=user['name'],
        lastName=user['last_name'],
        email=user['email'],
        phone=user.get('phone'),
        role=user['role'],
        preferences=user_preferences['preferences']
    )

    return user_model


def validate_api_key(
        api_key: str = Depends(api_key_scheme),
        mongo_client: Database[Mapping[str, Any]] = Depends(MongoDBClient())
):
    if not api_key:
        raise AuthException(error_id=ErrorsIDs.UNAUTHORIZED, description=ErrorsDescriptions.UNAUTHORIZED)

    api_key_db = mongo_client.api_key.find_one({'value': api_key})

    if not api_key_db:
        raise AuthException(error_id=ErrorsIDs.API_KEY_NOT_VALID, description=ErrorsDescriptions.API_KEY_NOT_VALID)

    return None


def validate_api_key_or_auth(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(auth_scheme),
        api_key: Optional[str] = Depends(api_key_scheme),
        mongo_client: Database[Mapping[str, Any]] = Depends(MongoDBClient())
):
    if credentials:
        return get_current_user(validate_bearer_token(credentials, mongo_client), mongo_client)

    if api_key:
        return validate_api_key(api_key, mongo_client)

    raise AuthException(error_id=ErrorsIDs.AUTH_CREDENTIALS_COULD_NOT_BE_VALIDATED,
                        description=ErrorsDescriptionsObject[ErrorsIDs.AUTH_CREDENTIALS_COULD_NOT_BE_VALIDATED])
