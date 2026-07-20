from decimal import Decimal
from typing import Optional

from sqlalchemy import select, or_, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from models import Inventory

import logging, re

logger = logging.getLogger(__name__)

DEVANAGARI_TO_LATIN = {
        'अ': 'a', 'आ': 'aa', 'इ': 'i', 'ई': 'ee', 'उ': 'u', 'ऊ': 'oo',
    'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au', 'ऋ': 'ri',
    'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'ङ': 'ng',
    'च': 'ch', 'छ': 'chh', 'ज': 'j', 'झ': 'jh', 'ञ': 'ny',
    'ट': 't', 'ठ': 'th', 'ड': 'd', 'ढ': 'dh', 'ण': 'n',
    'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n',
    'प': 'p', 'फ': 'ph', 'ब': 'b', 'भ': 'bh', 'म': 'm',
    'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'v', 'श': 'sh',
    'ष': 'sh', 'स': 's', 'ह': 'h',
    'ा': 'aa', 'ि': 'i', 'ी': 'ee', 'ु': 'u', 'ू': 'oo',
    'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au',
    'ं': 'n', 'ः': 'h', '्': '', 'ॅ': 'e',
    'ॐ': 'om', 'ऽ': "'",
}

HINDI_STOP_WORDS = {
    "मुझे", "चाहिए", "को", "का", "की", "के", "में", "से", "पर",
    "है", "हैं", "था", "थी", "थे", "हूँ", "हो", "नहीं", "और",
    "या", "एक", "दो", "तीन", "बजे", "कर", "दो", "दीजिए",
    "बता", "बताओ", "सुनो", "सुनिए", "जी", "भाई", "सर",
    "bhej", "do", "dijiye", "chahiye", "mujhe", "nahi",
    "karo", "karein", "kar", "dena", "lena",
}

def devanagari_to_latin(text: str) -> str:
    """ Convert Devanagari Hindi text to Latin script. Handles any Hindi word """
    result = []
    for char in text:
        if '\u0900' <= char <= '\u097F':
            result.append(DEVANAGARI_TO_LATIN.get(char, ""))
        else:
            result.append(char)

    return ''.join(result).strip()

def clean_query(query: str) -> str:
    """ Full query cleaning pipeline. """
    query = query.lower().strip()
    query = devanagari_to_latin(query)
    words = query.split()
    words = [QUERY_NORMALIZE.get(w,w) for w in words]
    words = [w for w in words if w not in HINDI_STOP_WORDS]
    query = ' '.join(words)
    query = re.sub(r'(\d+)\s*(ml|l|g|gram|gm|kg|liter|litre|pkt|pack)\b', r'\1 \2', query)
    return query

QUERY_NORMALIZE= {
    "coke": "coca cola",
    "thums": "thums up",
    "thumbs": "thums up",
}

async def create_product(db: AsyncSession, product: str, quantity: int, mrp: Decimal, price_per_case: Decimal, schemes: Optional[str] =  None) -> Inventory:
    item = Inventory(
        product=product,
        quantity=quantity,
        mrp=mrp,
        price_per_case=price_per_case,
        schemes=schemes
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item

async def get_product_id(db: AsyncSession, product_id: int) -> Optional[Inventory]:
    result = await db.execute(select(Inventory).where(Inventory.id==product_id))
    product = result.scalar_one_or_none()
    return product

async def get_product_by_name(db: AsyncSession, name:str) -> Optional[Inventory]:
    result = await db.execute(select(Inventory).where(Inventory.product==name))
    product_name = result.scalar_one_or_none()
    if not product_name:
        return None
    return product_name

async def update_product(db: AsyncSession, product_id: int, **kwargs) -> Optional[Inventory]:
    item = await get_product_id(db, product_id)
    if not item:
        return None
    for key, value in kwargs.items():
        if hasattr(item, key):
            setattr(item, key, value)

    await db.commit()
    await db.refresh(item)
    return item

async def delete_product(db: AsyncSession, product_id: int) -> bool:
    item = await get_product_id(db, product_id)
    if not item:
        return False
    await db.delete(item)
    await db.commit()
    return True

# Searching the Customer's Items in the DB ->
async def search_products(db: AsyncSession, query: str) -> list[Inventory]:
    try:
        query = clean_query(query)
        words = [w for w in query.split() if w]
        if not words:
            return []

        # Strategy 1: AND — all words must match
        result = await _execute_and_search(db, words)
        if result:
            return result

        # Strategy 2: OR — any word can match
        result = await _execute_or_search(db, words)
        if result:
            return result

        # Strategy 3: Remove numbers and units, retry AND then OR
        filtered = [w for w in words if not re.match(r'^\d+(\.\d+)?$', w)
                    and w not in ('ml','l','g','gram','gm','kg','liter','litre','pkt','pack','cases','case')]
        if filtered and filtered != words:
            result = await _execute_and_search(db, filtered)
            if result:
                return result
            result = await _execute_or_search(db, filtered)
            if result:
                return result

        # Strategy 4: Try single meaningful words
        for w in filtered:
            stmt = select(Inventory).where(func.lower(Inventory.product).contains(w))
            items = list((await db.execute(stmt)).scalars().all())
            if items:
                return items

        return []
    except Exception:
        logger.exception("search_products failed")
        return []

async def _execute_and_search(db: AsyncSession, words: list[str]) -> list[Inventory]:
    stmt = select(Inventory)
    for w in words:
        stmt = stmt.where(func.lower(Inventory.product).contains(w))
    return list((await db.execute(stmt)).scalars().all())

async def _execute_or_search(db: AsyncSession, words: list[str]) -> list[Inventory]:
    filters = [func.lower(Inventory.product).contains(w) for w in words]
    stmt = select(Inventory).where(or_(*filters))
    return list((await db.execute(stmt)).scalars().all())
    

# Get the Product Stock in Inventory (DB) ->
async def get_product_stock(db: AsyncSession, product_name: str) -> dict:
    """ Return {product, qunatity, mrp, price_per_case } or None """
    product = await get_product_by_name(db, product_name)
    if not product:
        return None
    return {
        "product": product.product,
        "quantity": product.quantity,
        "mrp": float(product.mrp),
        "price_per_case": float(product.price_per_case)
    }

# Deduct Sttock from Inventory ->
async def deduct_stock(db: AsyncSession,items: list[dict]) -> dict:
    """ Deduct stock for multiple items atomically.
    items = [{"product": "Coke 600ml", "qty": 3}, ...]
    Returns {"success": bool, "message": str} """

    try:
        for item in items:
            product_name = item["product"]
            qty = item["qty"]

            stmt = update(Inventory).where(Inventory.product==product_name, Inventory.quantity>=qty).values(quantity=Inventory.quantity-qty)
            result = await db.execute(stmt)

            if result.rowcount == 0:
                await db.rollback()
                product = await get_product_by_name(db, product_name)
                if not product:
                    return {"success":False, "message":f"Product Not Found: {product_name}"}
                
                return {"success":False, "message": f"Insufficient stock for {product_name}"}
            
        await db.commit()
        return {"success": True, "message": "Stock deducted for all items"}
    
    except Exception:
        await db.rollback()
        logger.exception("deduct_stock failed")
        return {"success": False, "message": "Database error during stock deduction"}




