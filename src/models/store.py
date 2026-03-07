from typing import Optional, List
from pydantic import Field, ConfigDict
from src.shared.generics import CommonModel
from src.utils.utils import ObjectIdTypeConverter

class StoreMetrics(CommonModel):
    rating: float
    total_reviews: int = Field(alias="totalReviews")
    follower_count: int = Field(alias="followerCount")
    joined_date: str = Field(alias="joinedDate")

class StoreVerification(CommonModel):
    is_verified: bool = Field(alias="isVerified")
    badge_type: str = Field(alias="badgeType")
    trust_score: int = Field(alias="trustScore")

class StoreFeature(CommonModel):
    key: str
    label: str
    icon: str
    details: str

class StoreSocialLinks(CommonModel):
    instagram: Optional[str] = None
    twitter: Optional[str] = None
    facebook: Optional[str] = None

class StoreContact(CommonModel):
    email: str
    support_hours: str = Field(alias="supportHours")
    base_country: str = Field(alias="baseCountry")

class StoreSettings(CommonModel):
    allow_direct_message: bool = Field(alias="allowDirectMessage")
    show_follower_count: bool = Field(alias="showFollowerCount")
    theme_color: str = Field(alias="themeColor")

class StoreModel(CommonModel):
    id: Optional[ObjectIdTypeConverter] = None
    stripe_store_id: str = Field(alias="stripeStoreId")
    name: str
    slug: str
    description: str
    logo_url: str = Field(alias="logoUrl")
    cover_image_url: str = Field(alias="coverImageUrl")
    metrics: StoreMetrics
    verification: StoreVerification
    features: List[StoreFeature]
    social_links: StoreSocialLinks = Field(alias="socialLinks")
    contact: StoreContact
    settings: StoreSettings

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": "store_01h8x9p3m2...",
                "stripeStoreId": "acct_123456789...",
                "name": "AnyCommerce Official Store",
                "slug": "anycommerce-official",
                "description": "Leading provider of high-quality electronics...",
                "logoUrl": "https://api.anycommerce.com/assets/stores/anycommerce-logo.png",
                "coverImageUrl": "https://api.anycommerce.com/assets/stores/anycommerce-banner.jpg",
                "metrics": {
                    "rating": 4.9,
                    "totalReviews": 12540,
                    "followerCount": 85200,
                    "joinedDate": "2023-01-15T00:00:00Z"
                },
                "verification": {
                    "isVerified": True,
                    "badgeType": "Official Store",
                    "trustScore": 98
                },
                "features": [
                    {
                        "key": "fast_shipping",
                        "label": "Fast Shipping Worldwide",
                        "icon": "Truck",
                        "details": "Dispatch within 24 hours"
                    }
                ],
                "socialLinks": {
                    "instagram": "https://instagram.com/anycommerce",
                    "twitter": "https://twitter.com/anycommerce",
                    "facebook": "https://facebook.com/anycommerce"
                },
                "contact": {
                    "email": "official-store@anycommerce.com",
                    "supportHours": "24/7",
                    "baseCountry": "US"
                },
                "settings": {
                    "allowDirectMessage": True,
                    "showFollowerCount": True,
                    "themeColor": "#0F172A"
                }
            }
        }
    )
