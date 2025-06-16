import requests
from pyzbar.pyzbar import decode
from PIL import Image
import argparse

API_URL = "http://127.0.0.1:8000"

def verify_qr_code(image_path: str):
    """
    Reads a QR code from an image, and sends the data to the verification API.
    """
    print(f"--- Verifying QR Code from: {image_path} ---")
    try:
        # 1. Decode the QR code from the image
        decoded_objects = decode(Image.open(image_path))
        if not decoded_objects:
            print("[ERROR] No QR code found in the image.")
            return

        unique_id = decoded_objects[0].data.decode("utf-8")
        print(f"Found Unique ID in QR Code: {unique_id}")
        
        # 2. Send the unique ID to the backend for verification
        response = requests.get(f"{API_URL}/verify/{unique_id}")
        response.raise_for_status()
        
        verification_data = response.json()
        
        # 3. Display the result
        print("\n--- VERIFICATION RESULT ---")
        print(f"Status: {verification_data['status']}")
        print(f"Message: {verification_data['message']}")
        
        if verification_data.get("product_data"):
            product = verification_data["product_data"]
            print("\n--- Product Details ---")
            print(f"  Product Name: {product['product_name']}")
            print(f"  Company: {product['company_name']}")
            print(f"  System ID: {product['unique_id']}")
            print("-------------------------")

    except FileNotFoundError:
        print(f"[ERROR] Image file not found at path: {image_path}")
    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR] Could not connect to the backend API: {e}")
    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify a product's QR code.")
    parser.add_argument("image_path", type=str, help="The path to the QR code image file.")
    args = parser.parse_args()
    
    verify_qr_code(args.image_path)