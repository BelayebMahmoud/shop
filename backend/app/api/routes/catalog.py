"""Categories (FR-03) and products (FR-04, FR-10). Reads are public; writes need STAFF or ADMIN."""

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_roles
from app.api.schemas import CategoryIn, CategoryOut, ProductIn, ProductOut, ProductPage
from app.models import Category, Product, User
from app.services import catalog, search
from app.services.catalog import ProductData
from app.services.workflow import ADMIN, STAFF

categories = APIRouter(prefix="/categories", tags=["categories"])
products = APIRouter(prefix="/products", tags=["products"])
back_office = require_roles(STAFF, ADMIN)


@categories.get("", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)) -> list[Category]:
    return catalog.list_categories(db)


@categories.get("/{category_id}", response_model=CategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db)) -> Category:
    return catalog.get_category(db, category_id)


@categories.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(body: CategoryIn, _: User = Depends(back_office), db: Session = Depends(get_db)) -> Category:
    return catalog.create_category(db, body.name)


@categories.put("/{category_id}", response_model=CategoryOut)
def update_category(category_id: int, body: CategoryIn, _: User = Depends(back_office), db: Session = Depends(get_db)) -> Category:
    return catalog.update_category(db, category_id, body.name)


@categories.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, _: User = Depends(back_office), db: Session = Depends(get_db)) -> Response:
    catalog.delete_category(db, category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@products.get("", response_model=ProductPage)
def list_products(
    q: str | None = Query(None, max_length=100),
    category_id: int | None = Query(None, ge=1),
    min_price_cents: int | None = Query(None, ge=0),
    max_price_cents: int | None = Query(None, ge=0),
    in_stock: bool = False,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> ProductPage:
    items, total = search.search_products(db, q, category_id, min_price_cents, max_price_cents, in_stock, limit, offset)
    return ProductPage(items=[ProductOut.model_validate(p) for p in items], total=total)


@products.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)) -> Product:
    return catalog.get_product(db, product_id)


@products.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(body: ProductIn, user: User = Depends(back_office), db: Session = Depends(get_db)) -> Product:
    return catalog.create_product(db, user, ProductData(**body.model_dump()))


@products.put("/{product_id}", response_model=ProductOut)
def update_product(product_id: int, body: ProductIn, user: User = Depends(back_office), db: Session = Depends(get_db)) -> Product:
    return catalog.update_product(db, user, product_id, ProductData(**body.model_dump()))


@products.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, user: User = Depends(back_office), db: Session = Depends(get_db)) -> Response:
    catalog.delete_product(db, user, product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
