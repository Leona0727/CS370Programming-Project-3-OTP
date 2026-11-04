import time
import hmac
import hashlib
import struct
import base64
import secrets
import argparse
import qrcode
from urllib.parse import quote


# User information
USER_ID = "student@example.com"
ISSUER = "My OTP Project"

SECRET_FILE = "secret.txt"


#Create a secret key if it does not exist
def get_secret():

    try:
        with open(SECRET_FILE, "r") as file:
            secret = file.read().strip()

    except FileNotFoundError:
        secret = base64.b32encode(secrets.token_bytes(20)).decode("utf-8").replace("=", "")

        with open(SECRET_FILE, "w") as file:
            file.write(secret)

    return secret


# Generate a TOTP code
def generate_otp(secret):

    # Change the Base32 secret into bytes
    key = base64.b32decode(secret + "=" * ((8 - len(secret) % 8) % 8))

    # Get the current time and divide it into 30-second periods
    current_time = int(time.time())
    counter = current_time // 30

    # Convert the counter into 8 bytes
    message = struct.pack(">Q", counter)

    # Calculate HMAC-SHA1
    hash_value = hmac.new(key, message, hashlib.sha1).digest()

    #find the position of the 4 bytes
    offset = hash_value[-1] & 0x0F

    # Get 4 bytes from the hash value
    four_bytes = hash_value[offset:offset + 4]
    
    # Convert the bytes into a number
    number = struct.unpack(">I", four_bytes)[0]
    
    # Remove the first bit
    number = number & 0x7FFFFFFF

    # Make a 6-digit OTP
    otp = number % 1000000

    return str(otp).zfill(6)


# Generate a QR code
def generate_qr(secret):

    uri = (
        "otpauth://totp/"
        + quote(ISSUER + ":" + USER_ID)
        + "?secret=" + secret
        + "&issuer=" + quote(ISSUER)
        + "&algorithm=SHA1&digits=6&period=30"
    )

    qr = qrcode.QRCode(box_size=10,border=4 )

    qr.add_data(uri)
    qr.make(fit=True)

    image = qr.make_image(fill_color="black", back_color="white")
    image = image.convert("RGB")
    image.save("otp_qr.jpg")

    print("QR code was created: otp_qr.jpg")


# Main program
def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--generate-qr", action="store_true")
    parser.add_argument("--get-otp", action="store_true")

    args = parser.parse_args()

    secret = get_secret()

    if args.generate_qr:
        generate_qr(secret)

    elif args.get_otp:
        otp = generate_otp(secret)
        print("Your OTP is:", otp)

    else:
        print("Please use --generate-qr or --get-otp")


if __name__ == "__main__":
    main()
