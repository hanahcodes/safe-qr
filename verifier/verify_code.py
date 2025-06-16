import requests
import argparse

API_URL = "http://127.0.0.1:8000"

def verify_qr_code_image(image_path: str):
    """
    Sends a QR code image to the backend for full verification (Phase 2).
    """
    print(f"--- Verifying Secure QR Code from: {image_path} ---")
    try:
        with open(image_path, 'rb') as f:
            files = {'file': (image_path, f, 'image/png')}
            response = requests.post(f"{API_URL}/verify/image", files=files)
        
        response.raise_for_status()
        verification_data = response.json()
        
        print("\n--- VERIFICATION RESULT ---")
        print(f"Status: {verification_data['status']}")
        print(f"Message: {verification_data['message']}")
        if verification_data.get('similarity_score') is not None:
             print(f"Similarity Score: {verification_data['similarity_score']:.4f}")

        if verification_data.get("product_data"):
            product = verification_data["product_data"]
            print("\n--- Product Details ---")
            print(f"  Product Name: {product['product_name']}")
            print(f"  Company: {product['company_name']}")
            print("-------------------------")

    except FileNotFoundError:
        print(f"[ERROR] Image file not found: {image_path}")
    except requests.exceptions.HTTPError as e:
        print(f"\n[ERROR] Verification failed. Server responded with: {e.response.status_code}")
        print(f"         Details: {e.response.json().get('detail', 'No details provided.')}")
    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify a product's secure QR code image.")
    parser.add_argument("image_path", type=str, help="The path to the secure QR code image file.")
    args = parser.parse_args()
    
    verify_qr_code_image(args.image_path)