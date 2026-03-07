from typing import TypedDict, List, Optional, NotRequired
from bson import ObjectId
from src.database.mongodb.schema.common_schemas import FeatureSchema

class StoreMetricsSchema(TypedDict):
    rating: float
    total_reviews: int
    follower_count: int
    joined_date: str

class StoreVerificationSchema(TypedDict):
    is_verified: bool
    badge_type: str
    trust_score: int


class StoreSocialLinksSchema(TypedDict):
    instagram: Optional[str]
    twitter: Optional[str]
    facebook: Optional[str]

class StoreContactSchema(TypedDict):
    email: str
    support_hours: str
    base_country: str

class StoreSettingsSchema(TypedDict):
    allow_direct_message: bool
    show_follower_count: bool
    theme_color: str

class StoreCollectionSchema(TypedDict):
    _id: NotRequired[ObjectId]
    stripe_store_id: str
    name: str
    slug: str
    description: str
    logo_url: str
    cover_image_url: str
    metrics: StoreMetricsSchema
    verification: StoreVerificationSchema
    features: List[FeatureSchema]
    social_links: StoreSocialLinksSchema
    contact: StoreContactSchema
    settings: StoreSettingsSchema
