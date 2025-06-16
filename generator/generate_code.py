import requests
import qrcode
import os

# Ensure the output directory exists
output_dir = "generator/generated_qrcodes"
os.makedirs(output_dir, exist_ok=True)

API_URL = "http://127.0.0.1:8000"

def generate_new_product_qr():
    print("--- Creating a new Secure QR Code ---")
    product_name = input("Enter the product name (e.g., 'Luxury Watch Model X'): ")
    company_name = input("Enter the company name (e.g., 'Swiss Watches Inc.'): ")

    payload = {
        "product_name": product_name,
        "company_name": company_name,
    }

    try:
        # 1. Register the product with the backend to get a unique ID
        response = requests.post(f"{API_URL}/products/", json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes
        product_data = response.json()
        unique_id = product_data["unique_id"]
        
        print(f"\n[SUCCESS] Product registered with Unique ID: {unique_id}")

        # 2. Generate the QR code containing the unique ID
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(unique_id)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        
        # 3. Save the QR code image
        filename = f"{product_name.replace(' ', '_')}_{unique_id[:8]}.png"
        filepath = os.path.join(output_dir, filename)
        img.save(filepath)
        
        print(f"[SUCCESS] QR Code image saved to: {filepath}")
        
    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR] Could not connect to the backend API: {e}")
    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred: {e}")

if __name__ == "__main__":
    generate_new_product_qr()