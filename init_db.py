import asyncio

from decimal import Decimal

from crud import create_product, get_product_by_name
from database import session_scope, init_db

KIRANA_PRODUCTS = [
    # === COCA-COLA (6) ===
    ("coca cola bottle 1 liter",                  12, Decimal("55.00"), Decimal("778.00"), None),
    ("coca cola bottle 250 ml",                   15, Decimal("20.00"), Decimal("505.00"), "buy 2 cases and get 3 pieces of maaza mango bottle 250 ml free"),
    ("coca cola bottle 600 ml",                   14, Decimal("38.00"), Decimal("860.00"), None),
    ("coca cola can 300 ml",                      10, Decimal("40.00"), Decimal("903.00"), None),
    ("coca cola glass bottle 200 ml",              8, Decimal("15.00"), Decimal("335.00"), None),
    ("coca cola zero bottle 750 ml",               6, Decimal("30.00"), Decimal("668.00"), None),

    # === SPRITE (4) ===
    ("sprite bottle 1 liter",                     12, Decimal("55.00"), Decimal("778.00"), None),
    ("sprite bottle 250 ml",                      14, Decimal("20.00"), Decimal("505.00"), "buy 1 case and get 2 pieces of sprite bottle 250 ml free"),
    ("sprite bottle 600 ml",                      13, Decimal("40.00"), Decimal("891.00"), None),
    ("sprite can 300 ml",                          9, Decimal("40.00"), Decimal("902.00"), None),

    # === FANTA (3) ===
    ("fanta orange bottle 250 ml",                11, Decimal("20.00"), Decimal("503.00"), "buy 2 cases and get 3 pieces of fanta orange bottle 250 ml free"),
    ("fanta orange bottle 600 ml",                10, Decimal("38.00"), Decimal("858.00"), None),
    ("fanta orange can 300 ml",                    8, Decimal("40.00"), Decimal("902.00"), None),

    # === THUMS UP (3) ===
    ("thums up bottle 250 ml",                    12, Decimal("20.00"), Decimal("505.00"), "buy 3 cases and get 1 case of thums up bottle 250 ml free"),
    ("thums up bottle 600 ml",                    11, Decimal("38.00"), Decimal("860.00"), None),
    ("thums up can 300 ml",                        9, Decimal("40.00"), Decimal("903.00"), None),

    # === LIMCA / MAAZA / MINUTE MAID (4) ===
    ("limca bottle 250 ml",                        8, Decimal("20.00"), Decimal("503.00"), None),
    ("maaza mango bottle 250 ml",                 10, Decimal("20.00"), Decimal("553.00"), None),
    ("maaza mango bottle 600 ml",                  9, Decimal("42.00"), Decimal("944.00"), None),
    ("minute maid pulpy orange bottle 250 ml",     7, Decimal("25.00"), Decimal("674.00"), None),

    # === MAGGI (8) ===
    ("maggi 2-minute masala noodles 70g",          15, Decimal("14.00"), Decimal("600.00"), "buy 2 cases and get 5 pieces free"),
    ("maggi 2-minute masala noodles 280g (4 pack)", 12, Decimal("52.00"), Decimal("1104.00"), "buy 1 case and get 2 pieces of masala-ae-magic sachet free"),
    ("maggi 2-minute chicken noodles 71g",         10, Decimal("14.00"), Decimal("600.00"), None),
    ("maggi hot heads green chilli noodles 71g",    7, Decimal("20.00"), Decimal("630.00"), None),
    ("maggi nutri-licious atta noodles 75g",        8, Decimal("15.00"), Decimal("624.00"), None),
    ("maggi cuppa masala noodles 70.5g",            6, Decimal("50.00"), Decimal("1080.00"), None),
    ("maggi masala-ae-magic sachet 6.5g",          14, Decimal("5.00"),  Decimal("420.00"), None),

    # === BRITANNIA GOOD DAY (7) ===
    ("20 wala britannia good day butter cookies",      12, Decimal("20.00"), Decimal("840.00"), "buy 2 cases and get 4 pieces free"),
    ("20 wala britannia good day cashew cookies",      10, Decimal("20.00"), Decimal("840.00"), None),
    ("20 wala britannia good day choco chip cookies",   9, Decimal("20.00"), Decimal("840.00"), None),
    ("20 wala britannia good day pista badam cookies",  7, Decimal("20.00"), Decimal("840.00"), None),
    ("45 wala britannia good day butter cookies",       8, Decimal("45.00"), Decimal("960.00"), "buy 1 case and get 3 pieces of 20 wala good day free"),
    ("45 wala britannia good day cashew cookies",       6, Decimal("45.00"), Decimal("960.00"), None),
    ("40 wala britannia good day rich butter cookies",  5, Decimal("40.00"), Decimal("1050.00"), None),

    # === LAYS (7) ===
    ("20 wala lays classic salted chips",                  13, Decimal("20.00"), Decimal("816.00"), "buy 2 cases and get 6 pieces of 10 wala free"),
    ("20 wala lays magic masala chips",                    12, Decimal("20.00"), Decimal("816.00"), "buy 3 cases and get 1 case of 10 wala free"),
    ("20 wala lays american style cream & onion chips",    11, Decimal("20.00"), Decimal("816.00"), None),
    ("20 wala lays chile limon chips",                      8, Decimal("20.00"), Decimal("816.00"), None),
    ("20 wala lays west indies hot n sweet chilli chips",   7, Decimal("20.00"), Decimal("816.00"), None),
    ("10 wala lays classic salted chips",                  10, Decimal("10.00"), Decimal("826.00"), None),

    # === BISCUITS & COOKIES (12) ===
    ("parle-g glucose biscuits 100g",                  20, Decimal("10.00"), Decimal("470.00"), "buy 3 cases get 1 case free"),
    ("parle-g gold star 200g",                         15, Decimal("20.00"), Decimal("560.00"), None),
    ("oreo vanilla cream 99g",                         18, Decimal("35.00"), Decimal("820.00"), None),
    ("oreo vanilla cream 200g",                        12, Decimal("70.00"), Decimal("1560.00"), None),
    ("hide and seek chocolate 100g",                   16, Decimal("30.00"), Decimal("720.00"), "buy 2 cases get 1 piece free per case"),
    ("hide and seek fab 150g",                         14, Decimal("45.00"), Decimal("1020.00"), None),
    ("bourbon chocolate cream 100g",                   15, Decimal("25.00"), Decimal("600.00"), None),
    ("marie gold biscuits 200g",                       20, Decimal("30.00"), Decimal("700.00"), None),
    ("sunfeast dark fantasy 150g",                     13, Decimal("50.00"), Decimal("1140.00"), None),
    ("sunfeast milky magic 150g",                      11, Decimal("40.00"), Decimal("920.00"), None),
    ("mcvitie's digestive 200g",                       10, Decimal("60.00"), Decimal("1380.00"), None),
    ("tiger biscuits 100g",                            22, Decimal("10.00"), Decimal("450.00"), "buy 4 cases get 1 case free"),

    # === SNACKS & NAMKEEN (10) ===
    ("kurkure masala munch 70g",                       18, Decimal("10.00"), Decimal("460.00"), None),
    ("kurkure green chutney 70g",                      16, Decimal("10.00"), Decimal("460.00"), None),
    ("bingo tedhe medhe 80g",                          15, Decimal("10.00"), Decimal("455.00"), None),
    ("bingo mad angles 80g",                           14, Decimal("10.00"), Decimal("455.00"), None),
    ("cheetos crunchy tomato 70g",                     12, Decimal("15.00"), Decimal("520.00"), None),
    ("balaji wafers salted 70g",                       20, Decimal("10.00"), Decimal("430.00"), "buy 3 cases get 5 pieces free"),
    ("balaji wafers pudina 70g",                       18, Decimal("10.00"), Decimal("430.00"), None),
    ("haldiram's bhujia 150g",                         15, Decimal("35.00"), Decimal("810.00"), None),
    ("haldiram's aloo bhujia 150g",                    14, Decimal("35.00"), Decimal("810.00"), None),
    ("too yumm multigrain chips 65g",                   8, Decimal("20.00"), Decimal("640.00"), None),

    # === DAIRY & CHILLED (10) ===
    ("amul butter 100g",                               15, Decimal("55.00"), Decimal("1260.00"), "buy 2 cases get 1 case free"),
    ("amul cheese block 200g",                         10, Decimal("95.00"), Decimal("2160.00"), None),
    ("amul cheese slices 10pcs",                        8, Decimal("85.00"), Decimal("1940.00"), None),
    ("amul paneer 200g",                               12, Decimal("90.00"), Decimal("2040.00"), None),
    ("amul malai paneer 200g",                         10, Decimal("100.00"), Decimal("2280.00"), None),
    ("amul fresh cream 200ml",                         14, Decimal("65.00"), Decimal("1480.00"), None),
    ("mother dairy curd 400g",                         18, Decimal("40.00"), Decimal("920.00"), None),
    ("mother dairy buttermilk 1L",                     12, Decimal("50.00"), Decimal("1140.00"), None),
    ("amul taaza toned milk 1L",                       20, Decimal("56.00"), Decimal("1280.00"), None),
    ("amul gold full cream milk 1L",                   20, Decimal("66.00"), Decimal("1500.00"), None),

    # === BEVERAGES — TEA, COFFEE, HEALTH DRINKS (8) ===
    ("taj mahal tea 100g",                             12, Decimal("80.00"), Decimal("1830.00"), None),
    ("taj mahal tea 250g",                             10, Decimal("180.00"), Decimal("4080.00"), None),
    ("bru instant coffee 100g",                         8, Decimal("190.00"), Decimal("4320.00"), None),
    ("bru gold coffee 100g",                            6, Decimal("240.00"), Decimal("5400.00"), None),
    ("bournvita chocolate drink 500g",                 10, Decimal("195.00"), Decimal("4440.00"), "buy 1 case get 2 spoons free"),
    ("horlicks classic malt 500g",                      9, Decimal("210.00"), Decimal("4740.00"), None),
    ("complan kesar badam 500g",                        7, Decimal("280.00"), Decimal("6360.00"), None),
    ("boost energy drink 500g",                         8, Decimal("220.00"), Decimal("4980.00"), None),

    # === STAPLES — RICE, ATTA, OIL, SUGAR, SALT (10) ===
    ("fortune chakki fresh atta 5kg",                  12, Decimal("165.00"), Decimal("1920.00"), None),
    ("ashirvaad shudh atta 5kg",                       12, Decimal("190.00"), Decimal("2220.00"), None),
    ("fortune basmati rice 1kg",                       10, Decimal("105.00"), Decimal("2400.00"), None),
    ("india gate basmati rice 1kg",                     8, Decimal("135.00"), Decimal("3060.00"), None),
    ("fortune sunflower oil 1L",                       12, Decimal("165.00"), Decimal("1860.00"), None),
    ("saffola gold refined oil 1L",                    10, Decimal("195.00"), Decimal("2180.00"), None),
    ("fortune sugar 1kg",                              20, Decimal("45.00"), Decimal("1040.00"), "buy 5 cases get 1 case free"),
    ("tata salt 1kg",                                  20, Decimal("18.00"), Decimal("420.00"), None),
    ("catch iodised salt 1kg",                         18, Decimal("20.00"), Decimal("450.00"), None),
    ("daawat biryani rice 1kg",                         8, Decimal("95.00"), Decimal("2160.00"), None),

    # === PERSONAL CARE & HOUSEHOLD (10) ===
    ("lifebuoy soap 100g",                             18, Decimal("38.00"), Decimal("880.00"), None),
    ("dove soap 100g",                                 15, Decimal("55.00"), Decimal("1260.00"), "buy 2 cases get 5 pieces free"),
    ("lux soap 100g",                                  20, Decimal("35.00"), Decimal("810.00"), None),
    ("head & shoulders shampoo sachet 6ml",            25, Decimal("5.00"),  Decimal("380.00"), None),
    ("clinic plus shampoo sachet 8ml",                 25, Decimal("4.00"),  Decimal("320.00"), None),
    ("colgate strong teeth 100g",                       12, Decimal("80.00"), Decimal("1820.00"), None),
    ("pepsodent germicheck 100g",                       14, Decimal("75.00"), Decimal("1720.00"), None),
    ("surf excel matic 500g",                           10, Decimal("125.00"), Decimal("2840.00"), None),
    ("ariel complete detergent 500g",                   10, Decimal("150.00"), Decimal("3400.00"), None),
    ("vim dishwash bar 200g",                           20, Decimal("15.00"), Decimal("350.00"), "buy 4 cases get 2 bars free"),
]


async def seed():
    await init_db()
    async with session_scope() as db:
        for product, quantity, mrp, price_per_case, schemes in KIRANA_PRODUCTS:
            existing = await get_product_by_name(db, product)
            if not existing:
                await create_product(db, product, quantity, mrp, price_per_case, schemes)
                print(f"Product Loading {product}")
            else:
                print(f"{product} (already exists in Inventory)")

        print(f"\n Done- {len(KIRANA_PRODUCTS)} products added in Inventory")

if __name__ == "__main__":
    asyncio.run(seed())



