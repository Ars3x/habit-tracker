from cryptography.hazmat.primitives import serialization
import base64

with open('vapid_public.pem', 'rb') as f:
    public_key = serialization.load_pem_public_key(f.read())

public_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.X962,
    format=serialization.PublicFormat.UncompressedPoint
)
public_b64 = base64.urlsafe_b64encode(public_bytes).decode().rstrip('=')
print("Публичный ключ (вставьте в JS):", public_b64)