from typing import Generic, TypeVar, Optional, List, Any
from pydantic import BaseModel

T = TypeVar("T")

class StandardResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[T] = None

class PaginationMeta(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int
    has_next: bool
    has_prev: bool

class PaginatedData(BaseModel, Generic[T]):
    items: List[T]
    meta: PaginationMeta
