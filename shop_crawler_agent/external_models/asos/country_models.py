from typing import Any, List, Optional

from pydantic import BaseModel


class Language(BaseModel):
    language: str
    name: str
    text: str
    languageShort: str
    isPrimary: bool


class Currency(BaseModel):
    currency: str
    symbol: str
    text: str
    isPrimary: bool
    currencyId: int


class SizeSchema(BaseModel):
    sizeSchema: str
    text: str
    isPrimary: bool


class CountryListItem(BaseModel):
    country: str
    store: Optional[str]
    name: str
    imageUrl: str
    siteUrl: str
    siteId: Optional[int]
    majorCountry: Optional[str]
    isDefaultCountry: Any
    region: Any
    legalEntity: Any
    languages: List[Language]
    currencies: List[Currency]
    sizeSchemas: List[SizeSchema]
