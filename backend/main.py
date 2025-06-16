import uuid
from fastapi import FastAPI
from .database import database, products
from .schemas import Product, ProductCreate, VerificationResponse

app = FastAPI(title="Secure QR Brand Protection MVP")

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Secure QR Brand Protection API"}

@app.post("/products/", response_model=Product, status_code=201)
async def create_product(product: ProductCreate):
    """
    Generates a new unique product entry in the database.
    This is called by the 'generator' script.
    """
    unique_id = str(uuid.uuid4())
    query = products.insert().values(
        unique_id=unique_id,
        product_name=product.product_name,
        company_name=product.company_name,
    )
    last_record_id = await database.execute(query)
    return {"id": last_record_id, "unique_id": unique_id, **product.dict()}

@app.get("/verify/{unique_id}", response_model=VerificationResponse)
async def verify_product(unique_id: str):
    """
    Simulates the mobile app scanning a QR code and verifying its ID.
    """
    query = products.select().where(products.c.unique_id == unique_id)
    result = await database.fetch_one(query)

    if not result:
        return VerificationResponse(
            status="COUNTERFEIT",
            message="This product code does not exist in our system. This is a suspected counterfeit.",
        )

    # In a real app, you might check if a code has been scanned too many times.
    # For now, if it exists, it's authentic.
    return VerificationResponse(
        status="AUTHENTIC",
        message="This product is authentic.",
        product_data=Product(**result)
    )