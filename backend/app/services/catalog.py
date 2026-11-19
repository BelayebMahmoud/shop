"""FR-03 / FR-04: categories and products. BR-07 uniqueness, BR-09 non-empty category, BR-10 product in use."""

from dataclasses import asdict, dataclass

from sqlalchemy import exists, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Category, OrderItem, Product, User
from app.services import audit
from app.services.errors import Conflict, NotFound


@dataclass(frozen=True)
class ProductData:
    sku: str
    name: str
    description: str
    price_cents: int
    stock: int
    category_id: int


def _commit_unique(db: Session, field: str) -> None:
    """Commit; a unique-index violation that raced past the pre-check is still a 409 DUPLICATE."""
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise Conflict("DUPLICATE", field=field) from exc


# ---------------------------------------------------------------- categories
def list_categories(db: Session) -> list[Category]:
    return list(db.scalars(select(Category).order_by(Category.name)).all())


def get_category(db: Session, category_id: int) -> Category:
    category = db.get(Category, category_id)
    if category is None:
        raise NotFound("NOT_FOUND")
    return category


def _check_category_name(db: Session, name: str, exclude_id: int | None = None) -> None:
    stmt = select(Category.id).where(func.lower(Category.name) == name.lower())
    if exclude_id is not None:
        stmt = stmt.where(Category.id != exclude_id)
    if db.scalar(stmt):
        raise Conflict("DUPLICATE", field="name")


def create_category(db: Session, name: str) -> Category:
    _check_category_name(db, name)
    category = Category(name=name)
    db.add(category)
    _commit_unique(db, "name")
    db.refresh(category)
    return category


def update_category(db: Session, category_id: int, name: str) -> Category:
    category = get_category(db, category_id)
    _check_category_name(db, name, exclude_id=category_id)
    category.name = name
    _commit_unique(db, "name")
    return category


def delete_category(db: Session, category_id: int) -> None:
    category = get_category(db, category_id)
    if db.scalar(select(exists().where(Product.category_id == category_id))):
        raise Conflict("CATEGORY_NOT_EMPTY")
    db.delete(category)
    db.commit()


# ---------------------------------------------------------------- products
def get_product(db: Session, product_id: int) -> Product:
    product = db.get(Product, product_id)
    if product is None:
        raise NotFound("NOT_FOUND")
    return product


def _check_product(db: Session, data: ProductData, exclude_id: int | None = None) -> None:
    if db.get(Category, data.category_id) is None:
        raise NotFound("CATEGORY_NOT_FOUND")
    stmt = select(Product.id).where(func.lower(Product.sku) == data.sku.lower())
    if exclude_id is not None:
        stmt = stmt.where(Product.id != exclude_id)
    if db.scalar(stmt):
        raise Conflict("DUPLICATE", field="sku")


def create_product(db: Session, actor: User, data: ProductData) -> Product:
    _check_product(db, data)
    product = Product(**asdict(data))
    db.add(product)
    db.flush()
    audit.record(db, actor.id, audit.PRODUCT_CREATED, "product", product.id, sku=data.sku)
    _commit_unique(db, "sku")
    db.refresh(product)
    return product


def update_product(db: Session, actor: User, product_id: int, data: ProductData) -> Product:
    product = get_product(db, product_id)
    _check_product(db, data, exclude_id=product_id)
    changed = {k: v for k, v in asdict(data).items() if getattr(product, k) != v}
    for key, value in asdict(data).items():
        setattr(product, key, value)
    audit.record(db, actor.id, audit.PRODUCT_UPDATED, "product", product_id, changed=sorted(changed))
    _commit_unique(db, "sku")
    return product


def delete_product(db: Session, actor: User, product_id: int) -> None:
    product = get_product(db, product_id)
    if db.scalar(select(exists().where(OrderItem.product_id == product_id))):
        raise Conflict("PRODUCT_IN_USE")
    db.delete(product)
    audit.record(db, actor.id, audit.PRODUCT_DELETED, "product", product_id, sku=product.sku)
    db.commit()
