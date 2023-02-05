from typing import Any, List, Optional
from pydantic import BaseModel


class Current(BaseModel):
    value: float
    text: str


class Previous(BaseModel):
    value: Optional[int]
    text: str


class Rrp(BaseModel):
    value: Any
    text: str


class Price(BaseModel):
    current: Current
    previous: Previous
    rrp: Rrp
    isMarkedDown: bool
    isOutletPrice: bool
    currency: str


class Product(BaseModel):
    id: int
    name: str
    price: Price
    colour: str
    colourWayId: int
    brandName: str
    hasVariantColours: bool
    hasMultiplePrices: bool
    groupId: Any
    productCode: int
    productType: str
    url: str
    imageUrl: str


class FacetValue(BaseModel):
    count: int
    id: str
    name: str
    isSelected: bool


class Facet(BaseModel):
    id: str
    name: str
    facetValues: List[FacetValue]
    displayStyle: str
    facetType: str
    hasSelectedValues: bool


class RecommendationsAnalytics(BaseModel):
    personalisationStatus: int
    numberOfItems: int
    personalisationType: str
    items: List


class Diagnostics(BaseModel):
    requestId: str
    processingTime: int
    queryTime: int
    recommendationsEnabled: bool
    recommendationsAnalytics: RecommendationsAnalytics


class SearchPassMeta(BaseModel):
    isPartial: bool
    isSpellcheck: bool
    searchPass: List
    alternateSearchTerms: List


class ProductListResponse(BaseModel):
    searchTerm: str
    categoryName: str
    itemCount: int
    redirectUrl: str
    products: List[Product]
    facets: List[Facet]
    diagnostics: Diagnostics
    searchPassMeta: SearchPassMeta
    queryId: Any
    discoverSearchProductTypes: List
