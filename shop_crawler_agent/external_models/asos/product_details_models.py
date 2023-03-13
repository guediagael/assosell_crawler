from typing import Any, List, Optional
from pydantic import BaseModel


class AlternateName(BaseModel):
    locale: str
    title: str


class Brand(BaseModel):
    brandId: int
    name: str
    description: Optional[str]


class WebCategory(BaseModel):
    id: int


class Current(BaseModel):
    value: int
    text: str
    versionId: str
    conversionId: Any


class Previous(BaseModel):
    value: int
    text: str
    versionId: str
    conversionId: Any


class Rrp(BaseModel):
    value: Optional[int]
    text: Optional[str]
    versionId: str
    conversionId: Any


class Xrp(BaseModel):
    value: float
    text: str
    versionId: str
    conversionId: str


class Price(BaseModel):
    current: Current
    previous: Previous
    rrp: Rrp
    xrp: Xrp
    currency: str
    isMarkedDown: bool
    isOutletPrice: bool


class Variant(BaseModel):
    id: int
    name: str
    sizeId: int
    brandSize: str
    sizeDescription: str
    sizeOrder: int
    sku: str
    isLowInStock: bool
    isInStock: bool
    isAvailable: bool
    colourWayId: int
    colourCode: Optional[str]
    colour: str
    price: Price
    isPrimary: bool


class Image(BaseModel):
    url: str
    type: str
    colourWayId: Optional[int]
    colourCode: str
    colour: str
    isPrimary: bool


class CatwalkItem(BaseModel):
    url: str
    colourWayId: int
    colourCode: str


class Media(BaseModel):
    images: List[Image]
    catwalk: List[CatwalkItem]
    spinset: List
    swatchSprite: List


class Info(BaseModel):
    aboutMe: str
    sizeAndFit: Optional[str]
    careInfo: str


class Current1(BaseModel):
    value: int
    text: str
    versionId: str
    conversionId: Any


class Previous1(BaseModel):
    value: int
    text: str
    versionId: str
    conversionId: Any


class Rrp1(BaseModel):
    value: Optional[int]
    text: Optional[str]
    versionId: str
    conversionId: Any


class Xrp1(BaseModel):
    value: float
    text: str
    versionId: str
    conversionId: str


class Price1(BaseModel):
    current: Current1
    previous: Previous1
    rrp: Rrp1
    xrp: Xrp1
    currency: str
    isMarkedDown: bool
    isOutletPrice: bool


class ProductDetailsResponse(BaseModel):
    id: int
    name: str
    description: str
    alternateNames: List[AlternateName]
    gender: str
    productCode: str
    pdpLayout: str
    brand: Brand
    sizeGuide: Optional[str]
    isNoSize: bool
    isOneSize: bool
    isInStock: bool
    countryOfManufacture: Any
    webCategories: List[WebCategory]
    variants: List[Variant]
    media: Media
    badges: List
    info: Info
    shippingRestriction: Any
    price: Price1
    baseUrl: str
