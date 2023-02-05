from typing import List, Optional
from pydantic import BaseModel


class Image(BaseModel):
    colour: Optional[str] = None
    colourCode: Optional[str] = None
    isPrimary: bool
    type: str
    url: str


class Current(BaseModel):
    text: str
    value: int
    versionId: str


class Previous(BaseModel):
    text: str
    value: int
    versionId: str


class Rrp(BaseModel):
    text: str
    value: int
    versionId: str


class Xrp(BaseModel):
    conversionId: str
    text: str
    value: float
    versionId: str


class Price(BaseModel):
    currency: str
    current: Current
    isMarkedDown: bool
    isOutletPrice: bool
    previous: Previous
    rrp: Rrp
    xrp: Xrp


class Current1(BaseModel):
    text: str
    value: int
    versionId: str


class Previous1(BaseModel):
    text: str
    value: int
    versionId: str


class Rrp1(BaseModel):
    text: str
    value: int
    versionId: str


class Xrp1(BaseModel):
    conversionId: str
    text: str
    value: float
    versionId: str


class Price1(BaseModel):
    currency: str
    current: Current1
    isMarkedDown: bool
    isOutletPrice: bool
    previous: Previous1
    rrp: Rrp1
    xrp: Xrp1


class Variant(BaseModel):
    brandSize: str
    colour: str
    colourCode: str
    id: int
    isAvailable: bool
    isInStock: bool
    isLowInStock: bool
    isPrimary: bool
    name: str
    price: Price1
    productCode: str
    sizeId: int
    sizeOrder: int


class Product1(BaseModel):
    brandName: str
    colour: str
    hasMultipleColoursInStock: bool
    hasMultiplePricesInStock: bool
    id: int
    images: List[Image]
    isAvailable: bool
    isInStock: bool
    isNoSize: bool
    isOneSize: bool
    name: str
    price: Price
    productCode: str
    sizeGuide: str
    variants: List[Variant]


class Product(BaseModel):
    order: int
    product: Product1


class ProductSimilarities(BaseModel):
    baseUrl: str
    id: int
    products: List[Product]
