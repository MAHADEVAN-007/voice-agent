from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, Text, Numeric, Float, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

from typing import Optional
from decimal import Decimal


class Inventory(Base):
    __tablename__ = "inventory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product: Mapped[str] = mapped_column(String(200), nullable=False, unique=True, index=True)
    quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    mrp: Mapped[Decimal] = mapped_column(Numeric(10,2), nullable=False)
    price_per_case: Mapped[Decimal] = mapped_column(Numeric(10,2), nullable=False)
    schemes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now())


