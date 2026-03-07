from fastapi import APIRouter, status, Path, Depends
from dependencies.auth import validate_api_key
from src.database.mongodb.collection.store_collection import get_store_by_id_db
from src.models.store import StoreModel
from src.shared.exceptions import HttpException
from src.shared.generics import Data
from src.utils.constants import ErrorsIDs, ErrorsDescriptionsObject

store_router = APIRouter(tags=['Stores'])

@store_router.get('/stores/{storeId}', responses={
    status.HTTP_200_OK: {"model": Data[StoreModel], 'description': 'Store found'},
    status.HTTP_404_NOT_FOUND: {"model": Data, 'description': 'Store not found'},
}, status_code=status.HTTP_200_OK)
def get_store_by_id(
    _: str = Depends(validate_api_key),
    store_id: str = Path(alias='storeId', min_length=1)
):
    try:
        store = get_store_by_id_db(store_id)

        if not store:
            raise HttpException(
                status_code=status.HTTP_404_NOT_FOUND,
                error_id=ErrorsIDs.NO_RECORDS_FOUND,
                description=ErrorsDescriptionsObject[ErrorsIDs.NO_RECORDS_FOUND].format('store')
            )

        return Data[StoreModel](
            data=store
        )

    except HttpException as ex:
        raise ex

    except Exception as ex:
        raise ex
