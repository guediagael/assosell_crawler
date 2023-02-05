from pydantic import BaseModel
from typing import List, Optional, Any


class NavigationListItemContent(BaseModel):
    title: str
    subTitle: Optional[str]
    webLargeImageUrl: Optional[str]
    mobileImageUrl: Optional[str]


class NavigationListItem(BaseModel):
    id: str
    alias: Optional[str]
    type: str
    content: NavigationListItemContent
    # children: List[Any] TODO


class NavigationListContent(BaseModel):
    title: str
    subTitle: Optional[str]
    webLargeImageUrl: Optional[str]
    mobileImageUrl: Optional[str]


class NavigationListLink(BaseModel):
    linkType: str
    brandSectionAlias: Optional[str]
    categoryId: Optional[str]
    webUrl: str
    appUrl: Optional[str]


class NavigationList(BaseModel):
    id: str
    alias: str
    type: str
    content: NavigationListContent
    link: NavigationListLink
    children: List[NavigationListItem]


class BrandListItemContent(BaseModel):
    title: str
    subtitle: Optional[str]
    webLargeImageUrl: Optional[str]
    mobileImageUrl: Optional[str]


class BrandListItemLink(BaseModel):
    linkType: str
    brandSectionAlias: Optional[str]
    categoryId: Optional[int]
    webUrl: str
    appUrl: str


class BrandListItem(BaseModel):
    id: str
    alias: Optional[str]
    type: str
    content: BrandListItemContent
    link: BrandListItemLink


class BrandListContent(BaseModel):
    title: str
    subtitle: Optional[str]
    webLargeImageUrl: Optional[str]
    mobileImageUrl: Optional[str]


class BrandListDisplay(BaseModel):
    webLargeTemplateId: int
    webLargeTemplateName: Optional[str]
    webLargeColumnSpan: int
    mobileTemplateId: int
    mobileTemplateName: Optional[str]
    mobileDisplayLayout: str  # tells how the content of this result is displayed on mobile


class BrandList(BaseModel):
    id: str
    alias: str
    type: str
    content: BrandListContent
    display: BrandListDisplay
    link: Optional[str]
    children: List[BrandListItem]


class CategoriesResponse(BaseModel):
    navigation: List[NavigationList]
    brands: List[BrandList]
