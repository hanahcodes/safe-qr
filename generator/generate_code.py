import requests
import qrcode
import os
from PIL import Image
import io

# Ensure the output directory exists
output_dir = "generator/generated_qrcodes"
os.makedirs(output_dir, exist_ok=True)

API_URL = "http://127.0.0.1:8000"
PATTERN_SIZE = (48, 48)  # Must match the backend

def generate_new_product_qr():
    print("--- Creating a new Secure QR Code (Phase 2) ---")
    product_name = input("Enter the product name: ")
    company_name = input("Enter the company name: ")

    payload = {"product_name": product_name, "company_name": company_name}

    try:
        # 1. Register product, backend creates master pattern
        response_create = requests.post(f"{API_URL}/products/", json=payload)
        response_create.raise_for_status()
        product_data = response_create.json()
        unique_id = product_data["unique_id"]
        print(f"\n[SUCCESS] Product registered with Unique ID: {unique_id}")

        # 2. Fetch the master pattern image from the backend
        response_pattern = requests.get(f"{API_URL}/products/{unique_id}/master_pattern")
        response_pattern.raise_for_status()
        pattern_img = Image.open(io.BytesIO(response_pattern.content))
        print("[SUCCESS] Master security pattern downloaded.")

        # 3. Generate the base QR code
        qr = qrcode.QRCode(version=3, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
        qr.add_data(unique_id)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

        # 4. Embed the pattern into the center of the QR code
        qr_w, qr_h = qr_img.size
        p_w, p_h = pattern_img.size
        position = ((qr_w - p_w) // 2, (qr_h - p_h) // 2)
        qr_img.paste(pattern_img, position)
        
        # 5. Save the final composite QR code image
        filename = f"SECURE_{product_name.replace(' ', '_')}_{unique_id[:8]}.png"
        filepath = os.path.join(output_dir, filename)
        qr_img.save(filepath)
        
        print(f"[SUCCESS] Secure QR Code image saved to: {filepath}")
        
    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR] API request failed: {e}")
    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred: {e}")

if __name__ == "__main__":
    generate_new_product_qr()