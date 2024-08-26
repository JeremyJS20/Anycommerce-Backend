import re
from collections.abc import Mapping
from typing import Annotated, Union, List, Any

from bson import ObjectId
from fastapi import APIRouter, Depends, Query, Path
from fastapi import status
from pymongo.database import Database

from dependencies.auth import get_current_user, validate_api_key, validate_api_key_or_auth
from dependencies.mongodb import MongoDBClient
from src.models.product import ProductModel
from src.models.request.review import ReviewRequest
from src.models.responses.product import ProductResponse, ProductsResponse, \
    ProductResponseAdditionalData
from src.models.responses.review import ReviewResponse
from src.models.responses.user import UserResponse
from src.models.user import BaseUserModel
from src.shared.exceptions import HttpException
from src.shared.generics import ErrorResponse, Data, \
    Error, DataWithAdditional, PaginationData
from src.utils.constants import ErrorsIDs, ErrorsDescriptions, Params
from src.utils.utils import convert_currency

product_router = APIRouter()

product_router.tags = ['Product']


@product_router.post('/create', responses={
    status.HTTP_201_CREATED: {"model": Data[ProductModel], 'description': 'Product Created'},
}, status_code=status.HTTP_201_CREATED)
def create_product(
        product: ProductModel,
        _: Annotated[BaseUserModel, Depends(get_current_user)],
        mongo_client: Database[Mapping[str, Any]] = Depends(MongoDBClient())
):
    try:
        product_id = mongo_client.product.insert_one(product.to_schema()).inserted_id

        product.id = str(product_id)

        return Data[ProductModel](
            data=product.to_json()
        )

    except HttpException as ex:
        raise ex

    except Exception as ex:
        raise ex


@product_router.get('/', responses={
    status.HTTP_200_OK: {"model": DataWithAdditional[List[ProductsResponse], PaginationData],
                         'description': 'Products Found'},
    status.HTTP_404_NOT_FOUND: {"model": Error[ErrorResponse], 'description': 'Products Not Found'},
}, status_code=status.HTTP_200_OK)
def get_products(
        current_user: Annotated[Union[BaseUserModel, str], Depends(validate_api_key_or_auth)],
        search: Union[str, None] = None,
        price_min: Union[int, None] = Query(default=None, alias='priceMin'),
        price_max: Union[int, None] = Query(default=None, alias='priceMax'),
        rating: Union[int, None] = None,
        category: Union[str, None] = None,
        subcategory: Union[str, None] = None,
        sort: Union[str, None] = None,
        index: int = Query(default=1, gt=0),
        mongo_client: Database[Mapping[str, Any]] = Depends(MongoDBClient())
):
    try:
        queries = []

        if search:
            search_patterns = [
                {"name": {"$regex": re.compile(f".*{re.escape(word)}.*", re.IGNORECASE)}}
                for word in search.split(sep=" ")
            ]

            queries.append({"$or": search_patterns})

            # pattern = "|".join(search.split(sep=' '))
            # regex_pattern = re.compile(pattern, re.IGNORECASE)
            # query['name'] = {"$regex": regex_pattern}

        if price_min and price_max:
            price_pattern = [{'cost': {'$gte': price_min}}, {'cost': {'$lte': price_max}}]

            queries.append({"$and": price_pattern})

        if rating:
            rating_pattern = [{'rating': {'$gte': rating}}]

            queries.append({"$and": rating_pattern})

        if category:
            category_pattern = [{'category': {'$eq': category}}]

            queries.append({"$and": category_pattern})

        if subcategory:
            subcategory_pattern = [{'subcategory': {'$eq': subcategory}}]

            queries.append({"$and": subcategory_pattern})

        query = {"$and": queries} if len(queries) > 0 else {}

        offset = (index - 1) * Params.RECORDS_LIMIT

        if len(queries) > 0:
            offset = 1
            index = 1

        products_db = None
        total_products = None

        if sort:
            sort_conditions = []

            match sort:
                case 'priceAsc':
                    sort_conditions.append(('cost', 1))
                case 'priceDesc':
                    sort_conditions.append(('cost', -1))
                case 'alphabeticallyAsc':
                    sort_conditions.append(('name', 1))
                case 'alphabeticallyDesc':
                    sort_conditions.append(('name', -1))
                case 'dateAsc':
                    sort_conditions.append(('date.creation', 1))
                case 'dateDesc':
                    sort_conditions.append(('date.creation', -1))

            products_db = mongo_client.product.find(query).skip(offset).limit(Params.RECORDS_LIMIT).sort(
                sort_conditions)
            total_products = mongo_client.product.count_documents(query)
        else:
            products_db = mongo_client.product.find(query).skip(offset).limit(Params.RECORDS_LIMIT)
            total_products = mongo_client.product.count_documents(query)

        products = [ProductsResponse(
            id=str(product['_id']),
            name=product['name'],
            cost=convert_currency(base_currency=product['currency'],
                                  target_currency=current_user.preferences.currency if current_user else product['currency'],
                                  amount=product['cost'],
                                  mongo_client=mongo_client
                                  ),
            currency=current_user.preferences.currency if current_user else product['currency'],
            stock=product['stock'],
            category=product['category'],
            subcategory=product['subcategory'],
            rating=product.get('rating'),
            imgs=product.get('imgs')
        ).to_json() for product in products_db]

        if len(products) <= 0:
            raise HttpException(
                status_code=status.HTTP_404_NOT_FOUND,
                error_id=ErrorsIDs.NO_RECORDS_FOUND,
                description=ErrorsDescriptions.NO_RECORDS_FOUND.value.format('products')
            )

        total_page_records = len(products)

        def calculate_total_pages():
            if total_products % Params.RECORDS_LIMIT == 0:
                return int(total_products / Params.RECORDS_LIMIT)

            return int(total_products / Params.RECORDS_LIMIT) + 1

        return DataWithAdditional[List[ProductsResponse], PaginationData](
            data=products,
            additionalData=PaginationData(
                currentPage=index,
                totalPageRecords=total_page_records,
                totalRecords=total_products,
                totalPages=calculate_total_pages()
            ).to_json()
        )

    except HttpException as ex:
        raise ex

    except Exception as ex:
        raise ex


@product_router.get('/{productId}', responses={
    status.HTTP_200_OK: {"model": DataWithAdditional[ProductResponse, ProductResponseAdditionalData],
                         'description': 'Product Found'},
    status.HTTP_404_NOT_FOUND: {"model": Error[ErrorResponse], 'description': 'Product Not Found'},
}, status_code=status.HTTP_200_OK)
def get_product_by_id(
        current_user: Annotated[Union[BaseUserModel, str], Depends(validate_api_key_or_auth)],
        product_id: str = Path(alias='productId'),
        mongo_client: Database[Mapping[str, Any]] = Depends(MongoDBClient())
):
    try:
        product = mongo_client.product.find_one({'_id': ObjectId(product_id)})

        if not product:
            raise HttpException(
                status_code=status.HTTP_404_NOT_FOUND,
                error_id=ErrorsIDs.NO_RECORDS_FOUND,
                description=ErrorsDescriptions.NO_RECORDS_FOUND.value.format('product')
            )

        product_reviews_db = (mongo_client.review.find({'product_id': product_id})
                              .limit(Params.REVIEWS_LIMIT)
                              .sort([('date', -1)]))

        product_reviews: List[ReviewResponse] = []

        for review in product_reviews_db:
            user_review: dict = mongo_client.user.find_one({'_id': ObjectId(review['user_id'])})

            product_review: ReviewResponse = ReviewResponse(
                id=str(review['_id']),
                title=review['title'],
                opinion=review['opinion'],
                rating=review['rating'],
                date=review['date'],
                customer=UserResponse(
                    id=str(user_review['_id']),
                    name=user_review['name'],
                    lastName=user_review['last_name'],
                    profilePhoto=user_review.get('profilePhoto')
                ),
                media=review.get('media')
            )

            product_reviews.append(product_review.to_json())

        total_reviews = mongo_client.review.count_documents({'product_id': product_id})

        response = ProductResponse(
            id=str(product['_id']),
            storeId=str(product['store_id']),
            name=product['name'],
            cost=convert_currency(base_currency=product['currency'],
                                  target_currency=current_user.preferences.currency if current_user else product['currency'],
                                  amount=product['cost'],
                                  mongo_client=mongo_client
                                  ),
            currency=current_user.preferences.currency if current_user else product['currency'],
            stock=product['stock'],
            category=product['category'],
            subcategory=product['subcategory'],
            rating=product.get('rating'),
            imgs=product.get('imgs'),
            dates=product['dates'],
            details=product['details'],
            variants=product.get('variants'),
            reviews=product_reviews
        )

        response_additional = ProductResponseAdditionalData(
            totalReviews=total_reviews
        )

        return DataWithAdditional[ProductResponse, ProductResponseAdditionalData](
            data=response.to_json(),
            additionalData=response_additional.to_json()
        )

    except HttpException as ex:
        raise ex

    except Exception as ex:
        raise ex


@product_router.post('/{productId}/add-review', responses={
    status.HTTP_201_CREATED: {"model": Data[str], 'description': 'Review added'},
}, status_code=status.HTTP_201_CREATED)
def add_product_review(
        current_user: Annotated[BaseUserModel, Depends(get_current_user)],
        review: ReviewRequest,
        product_id: str = Path(alias='productId'),
        mongo_client: Database[Mapping[str, Any]] = Depends(MongoDBClient())
):
    try:
        review.userId = current_user.id
        review.productId = product_id

        review_id = mongo_client.review.insert_one(review.to_schema()).inserted_id

        product_reviews_db = mongo_client.review.find({'product_id': product_id})

        product_reviews = [pr for pr in product_reviews_db]

        rating = float(str(sum([pr['rating'] for pr in product_reviews]) / len(product_reviews))[:3])

        mongo_client.product.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": {'rating': rating}}
        )

        return Data[str](
            data=str(review_id)
        )

    except HttpException as ex:
        raise ex

    except Exception as ex:
        raise ex
