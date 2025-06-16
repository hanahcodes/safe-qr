import uuid
import os
import numpy as np
import cv2
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pyzbar.pyzbar import decode
from skimage.metrics import structural_similarity as ssim
import io
from PIL import Image
from .database import database, products
from .schemas import Product, ProductCreate, VerificationResponse

# --- PHASE 2 CONSTANTS ---
PATTERN_SIZE = (48, 48)  # The resolution of our security pattern
MASTER_PATTERN_DIR = "backend/master_patterns"
os.makedirs(MASTER_PATTERN_DIR, exist_ok=True)

app = FastAPI(title="Secure QR Brand Protection - Phase 2")

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


def generate_and_save_pattern(unique_id: str) -> str:
    """Generates a random noise pattern and saves it as an image."""
    pattern_data = np.random.randint(0, 256, (PATTERN_SIZE[0], PATTERN_SIZE[1], 1), dtype=np.uint8)
    filepath = os.path.join(MASTER_PATTERN_DIR, f"{unique_id}.png")
    cv2.imwrite(filepath, pattern_data)
    return filepath


@app.post("/products/", response_model=Product, status_code=201)
async def create_product(product: ProductCreate):
    """
    Generates a new product, creates its unique master pattern,
    and stores both in the database.
    """
    unique_id = str(uuid.uuid4())
    master_pattern_path = generate_and_save_pattern(unique_id)

    query = products.insert().values(
        unique_id=unique_id,
        product_name=product.product_name,
        company_name=product.company_name,
        master_pattern_path=master_pattern_path,
    )
    last_record_id = await database.execute(query)
    return {
        "id": last_record_id,
        "unique_id": unique_id,
        "master_pattern_path": master_pattern_path,
        **product.dict(),
    }


@app.get("/products/{unique_id}/master_pattern")
async def get_master_pattern(unique_id: str):
    """Allows the generator client to download the master pattern."""
    query = products.select().where(products.c.unique_id == unique_id)
    result = await database.fetch_one(query)
    if not result or not os.path.exists(result["master_pattern_path"]):
        raise HTTPException(status_code=404, detail="Product or pattern not found.")
    return FileResponse(result["master_pattern_path"])


def compare_patterns(image1_path, image2_data) -> float:
    """Compares two patterns using Structural Similarity Index (SSIM)."""
    master_pattern = cv2.imread(image1_path, cv2.IMREAD_GRAYSCALE)
    
    # Convert uploaded image data from bytes to a numpy array
    nparr = np.frombuffer(image2_data, np.uint8)
    uploaded_image = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    
    # Extract the central pattern from the uploaded QR code image
    # Note: This assumes the generator always places the pattern perfectly in the center.
    h, w = uploaded_image.shape
    center_x, center_y = w // 2, h // 2
    p_h, p_w = PATTERN_SIZE
    
    start_x = center_x - p_w // 2
    start_y = center_y - p_h // 2
    
    extracted_pattern = uploaded_image[start_y : start_y + p_h, start_x : start_x + p_w]

    if extracted_pattern.shape != master_pattern.shape:
        # Resize for a basic comparison if shapes don't match
        extracted_pattern = cv2.resize(extracted_pattern, master_pattern.shape[::-1])
        
    # Calculate the structural similarity
    score, _ = ssim(master_pattern, extracted_pattern, full=True)
    return score


@app.post("/verify/image", response_model=VerificationResponse)
async def verify_product_by_image(file: UploadFile = File(...)):
    """
    The CORE of Phase 2. Receives an image, finds the QR code and pattern,
    and compares it to the master pattern.
    """
    image_data = await file.read()

    # 1. Decode the unique ID from the QR code within the image
    try:
        decoded_objects = decode(Image.open(io.BytesIO(image_data)))
        if not decoded_objects:
            raise HTTPException(status_code=400, detail="No QR code found in the image.")
        unique_id = decoded_objects[0].data.decode("utf-8")
    except Exception as e:
        # Catch potential decoding errors
        raise HTTPException(status_code=400, detail=f"Could not process image: {e}")
    
    # 2. Fetch the product from the database
    query = products.select().where(products.c.unique_id == unique_id)
    product_record = await database.fetch_one(query)

    if not product_record:
        return VerificationResponse(
            status="COUNTERFEIT",
            message="This product code does not exist. This is a suspected counterfeit.",
        )

    # 3. Compare the embedded pattern with the master pattern
    master_pattern_path = product_record["master_pattern_path"]
    try:
        similarity_score = compare_patterns(master_pattern_path, image_data)
    except Exception as e:
        # If comparison fails for any reason (e.g., can't find pattern)
        return VerificationResponse(
            status="UNABLE_TO_VERIFY",
            message=f"Could not analyze security pattern. Error: {e}",
            product_data=Product(**product_record)
        )

    # 4. Make a decision based on the similarity score
    AUTHENTICITY_THRESHOLD = 0.90  # 90% similarity required. You can tune this!

    if similarity_score >= AUTHENTICITY_THRESHOLD:
        return VerificationResponse(
            status="AUTHENTIC",
            message="This product is authentic.",
            similarity_score=similarity_score,
            product_data=Product(**product_record),
        )
    else:
        return VerificationResponse(
            status="COUNTERFEIT",
            message="The security pattern does not match the original. This is a suspected counterfeit.",
            similarity_score=similarity_score,
            product_data=Product(**product_record),
        )