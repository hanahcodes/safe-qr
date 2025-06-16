import qrcode
import numpy as np
from PIL import Image
import os

# --- Configuration ---
DATA_TO_ENCODE = "https://mybrand.com/product/12345-abcde"
PATTERN_SIZE = 48  # The width and height of our security pattern in pixels
OUTPUT_DIR = "before_and_after"

def generate_standard_qr(data, filepath):
    """Generates a plain, standard QR code."""
    print("1. Generating the 'Before' image: A standard QR code...")
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L, # Standard, low error correction
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filepath)
    print(f"   -> Saved to {filepath}\n")

def generate_secure_qr(data, filepath):
    """Generates a QR code with an embedded copy detection pattern."""
    print("2. Generating the 'After' image: A Secure QR code...")

    # --- Step A: Create the random, high-entropy copy detection pattern ---
    # We use numpy to create a grid of random grayscale pixel values (0-255)
    pattern_array = np.random.randint(0, 256, (PATTERN_SIZE, PATTERN_SIZE), dtype=np.uint8)
    pattern_img = Image.fromarray(pattern_array, mode='L') # 'L' mode is for grayscale
    print("   -> Created a random grayscale security pattern.")

    # --- Step B: Create a base QR code with HIGH error correction ---
    # This is the critical step. ERROR_CORRECT_H makes space for our pattern.
    qr = qrcode.QRCode(
        version=3, # A slightly larger version to ensure enough space
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    # Generate the QR as a Pillow Image object so we can manipulate it
    qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
    print("   -> Generated a base QR code with High (H) error correction.")

    # --- Step C: Paste the pattern into the center of the QR code ---
    qr_width, qr_height = qr_img.size
    pattern_width, pattern_height = pattern_img.size
    
    # Calculate the top-left position to paste the pattern for centering
    position = (
        (qr_width - pattern_width) // 2,
        (qr_height - pattern_height) // 2
    )
    
    qr_img.paste(pattern_img, position)
    print("   -> Pasted the security pattern onto the center of the QR code.")

    # --- Step D: Save the final, composite image ---
    qr_img.save(filepath)
    print(f"   -> Saved final secure image to {filepath}\n")


if __name__ == "__main__":
    # Create the output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Define filepaths
    standard_qr_path = os.path.join(OUTPUT_DIR, "standard_qr.png")
    secure_qr_path = os.path.join(OUTPUT_DIR, "secure_qr.png")
    
    # Run the generation process
    generate_standard_qr(DATA_TO_ENCODE, standard_qr_path)
    generate_secure_qr(DATA_TO_ENCODE, secure_qr_path)
    
    print("--- Process Complete! ---")
    print(f"Check the '{OUTPUT_DIR}' folder to see the 'before' and 'after' images.")