
from decimal import Decimal
from pydantic import BaseModel,Field


class Book(BaseModel):
    name: str = Field(..., min_length=2, max_length=20)
    author: str = Field(min_length=2, max_length=10)
    chuBanShe: str = Field(default="黑马出版社")
    price: Decimal = Field(...,gt=0)


@app.post()
async def Book(book: Book):
    return book