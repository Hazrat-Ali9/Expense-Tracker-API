from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import Select, func, select

from app.api.deps import CurrentUser, DbSession
from app.models.transaction import Transaction
from app.schemas.transaction import (
    DeleteResponse,
    TransactionCreate,
    TransactionPublic,
    TransactionType,
    TransactionUpdate,
)


router = APIRouter(prefix="/transactions", tags=["Transactions"])


def owned_transaction_query(transaction_id: int, owner_id: int) -> Select[tuple[Transaction]]:
    return select(Transaction).where(
        Transaction.id == transaction_id, Transaction.owner_id == owner_id
    )


def get_owned_transaction(
    transaction_id: int, owner_id: int, db: DbSession
) -> Transaction:
    transaction = db.scalar(owned_transaction_query(transaction_id, owner_id))
    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    return transaction


@router.post("", response_model=TransactionPublic, status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: TransactionCreate, current_user: CurrentUser, db: DbSession
) -> Transaction:
    transaction = Transaction(**payload.model_dump(), owner_id=current_user.id)
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


@router.get("", response_model=list[TransactionPublic])
def get_transactions(current_user: CurrentUser, db: DbSession) -> list[Transaction]:
    statement = (
        select(Transaction)
        .where(Transaction.owner_id == current_user.id)
        .order_by(Transaction.date.desc(), Transaction.id.desc())
    )
    return list(db.scalars(statement).all())


@router.get("/filter", response_model=list[TransactionPublic])
def filter_transactions(
    current_user: CurrentUser,
    db: DbSession,
    transaction_type: Annotated[TransactionType | None, Query(alias="type")] = None,
    category: Annotated[str | None, Query(min_length=1, max_length=80)] = None,
    minimum_amount: Annotated[float | None, Query(gt=0)] = None,
    maximum_amount: Annotated[float | None, Query(gt=0)] = None,
) -> list[Transaction]:
    if (
        minimum_amount is not None
        and maximum_amount is not None
        and minimum_amount > maximum_amount
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="minimum_amount cannot be greater than maximum_amount",
        )

    statement = select(Transaction).where(Transaction.owner_id == current_user.id)
    if transaction_type is not None:
        statement = statement.where(Transaction.type == transaction_type)
    if category is not None:
        statement = statement.where(
            func.lower(Transaction.category) == category.strip().lower()
        )
    if minimum_amount is not None:
        statement = statement.where(Transaction.amount >= minimum_amount)
    if maximum_amount is not None:
        statement = statement.where(Transaction.amount <= maximum_amount)

    statement = statement.order_by(Transaction.date.desc(), Transaction.id.desc())
    return list(db.scalars(statement).all())


@router.get("/{transaction_id}", response_model=TransactionPublic)
def get_transaction(
    transaction_id: int, current_user: CurrentUser, db: DbSession
) -> Transaction:
    return get_owned_transaction(transaction_id, current_user.id, db)


@router.put("/{transaction_id}", response_model=TransactionPublic)
def update_transaction(
    transaction_id: int,
    payload: TransactionUpdate,
    current_user: CurrentUser,
    db: DbSession,
) -> Transaction:
    transaction = get_owned_transaction(transaction_id, current_user.id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(transaction, field, value)

    db.commit()
    db.refresh(transaction)
    return transaction


@router.delete("/{transaction_id}", response_model=DeleteResponse)
def delete_transaction(
    transaction_id: int, current_user: CurrentUser, db: DbSession
) -> DeleteResponse:
    transaction = get_owned_transaction(transaction_id, current_user.id, db)
    db.delete(transaction)
    db.commit()
    return DeleteResponse(message="Transaction deleted successfully")

