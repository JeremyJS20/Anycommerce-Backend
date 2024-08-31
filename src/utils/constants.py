from enum import Enum


class ErrorsIDs:
    INTERNAL_SERVER_ERROR = 0
    VALIDATION_ERROR = 1000
    NO_RECORDS_FOUND = 1001
    EMAIL_OR_PASSWORD_INVALID = 1002
    UNAUTHORIZED = 1003
    EMAIL_USER_EXISTS = 1004
    API_KEY_NOT_VALID = 1005
    AUTH_HEADER_MISSING = 1006
    AUTH_SCHEME_NOT_VALID = 1007
    AUTH_TOKEN_MISSING = 1008
    AUTH_TOKEN_EXPIRED = 1009
    AUTH_TOKEN_NOT_VALID = 1010
    AUTH_TOKEN_COULD_NOT_BE_VALIDATED = 1011
    REFRESH_TOKEN_NOT_VALID = 1012
    USER_ALREADY_HAVE_CART = 1013
    USER_ALREADY_HAVE_DEFAULT = 1014
    AUTH_CREDENTIALS_COULD_NOT_BE_VALIDATED = 1015
    REFRESH_TOKEN_EXPIRED = 1016
    REFRESH_TOKEN_COULD_NOT_BE_VALIDATED = 1017


ErrorsDescriptionsObject = {
    ErrorsIDs.USER_ALREADY_HAVE_CART: 'User already have a cart',
    ErrorsIDs.USER_ALREADY_HAVE_DEFAULT: 'User already have a default {}',
    ErrorsIDs.NO_RECORDS_FOUND: "No {0} found",
    ErrorsIDs.AUTH_CREDENTIALS_COULD_NOT_BE_VALIDATED: "Could not validate credentials",
    ErrorsIDs.REFRESH_TOKEN_EXPIRED: "Refresh token expired",
    ErrorsIDs.REFRESH_TOKEN_COULD_NOT_BE_VALIDATED: "Refresh token could not be validated",
}


class ErrorsDescriptions(Enum):
    INTERNAL_SERVER_ERROR = "Internal server error"
    VALIDATION_ERROR = "Validation error"
    NO_RECORDS_FOUND = "No {0} found"
    EMAIL_OR_PASSWORD_INVALID = "Email or password incorrect"
    UNAUTHORIZED = 'Not authorized'
    EMAIL_USER_EXISTS = 'User with email {0} already exists'
    API_KEY_NOT_VALID = 'Api key is not valid'
    AUTH_HEADER_MISSING = 'Authorization header missing'
    AUTH_SCHEME_NOT_VALID = 'Authorization scheme is not valid'
    AUTH_TOKEN_MISSING = 'Authorization token missing'
    AUTH_TOKEN_EXPIRED = 'Authorization token expired'
    AUTH_TOKEN_NOT_VALID = 'Authorization token is not valid'
    AUTH_TOKEN_COULD_NOT_BE_VALIDATED = 'Authorization token could not be validated'
    REFRESH_TOKEN_NOT_VALID = 'Refresh token is not valid'
    ErrorsIDs.USER_ALREADY_HAVE_CART = 'User already have a cart'


class StripeErrorsIDs:
    GENERIC_DECLINE = 2001
    INSUFFICIENT_FUNDS = 2002
    LOST_CARD = 2003
    STOLEN_CARD = 2004
    EXPIRED_CARD = 2005
    INCORRECT_CVC = 2006
    CARD_VELOCITY_EXCEEDED = 2007
    CARD_DECLINED = 2008


StripeErrorsDescriptionsObject = {
    StripeErrorsIDs.GENERIC_DECLINE: 'Your card has been declined.',
    StripeErrorsIDs.INSUFFICIENT_FUNDS: "Your card doesn't have enough funds.",
    StripeErrorsIDs.LOST_CARD: 'Your card has been reported as lost.',
    StripeErrorsIDs.STOLEN_CARD: 'Your card has been reported as stolen.',
    StripeErrorsIDs.EXPIRED_CARD: 'Your card has expired.',
    StripeErrorsIDs.INCORRECT_CVC: "Your card's cvc is incorrect.",
    StripeErrorsIDs.CARD_VELOCITY_EXCEEDED: 'Card velocity exceeded',
    StripeErrorsIDs.CARD_DECLINED: 'Your card has been declined.',
}


class ResponseDescriptions:
    USER_SIGNED_OUT_SUCCESS = "User signed out successfully"
    USER_CREATED_SUCCESS = "User created successfully"
    RECORD_DELETED_SUCCESS = "{0} deleted successfully"
    RECORD_CREATED_SUCCESS = "{0} created successfully"
    RECORD_ADDED_SUCCESS = "{0} added successfully"
    RECORD_UPDATED_SUCCESS = "{0} updated successfully"
    DEFAULT_ADDRESS_CHANGED = "Default address changed"
    ORDER_PLACED_SUCCESS = "Orders placed successfully"
    PROCESSING_PAYMENT = "Your payment is being processed"


class Params:
    ACCESS_TOKEN_EXPIRE_MINUTES = 60
    REFRESH_TOKEN_EXPIRE_MINUTES = 14400
    RECORDS_LIMIT = 12
    REVIEWS_LIMIT = 5


class DateFormats:
    DATETIME_YYYY_MM_DD_HH_MM_SS = '%Y-%m-%d %H:%M:%S'
    DATE_YYYY_MM_DD = '%Y-%m-%d'


class PaymentMethodType(Enum):
    CARD = "CARD"
    SERVICE = "SERVICE"


class PaymentMethodTypeService(Enum):
    PAYPAL = 'PAYPAL'


class PaymentIntentStatus(Enum):
    INITIATED = "INITIATED"
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    AWAITING_CONFIRMATION = "AWAITING_CONFIRMATION"
    SUCCESSFUL = "SUCCEEDED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"
    EXPIRED = "EXPIRED"
    REQUIRES_ACTION = "REQUIRES_ACTION"
    ON_HOLD = "ON_HOLD"
    REFUNDED = "REFUNDED"
    PARTIALLY_REFUNDED = "PARTIALLY_REFUNDED"
    DISPUTED = "DISPUTED"
    CHARGEBACK = "CHARGEBACK"


class OrderStatus(Enum):
    ORDER_PLACED = "ORDER_PLACED"
    PAYMENT_CONFIRMED = "PAYMENT_CONFIRMED"
    ORDER_PROCESSING = "ORDER_PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    RETURNED = "RETURNED"
