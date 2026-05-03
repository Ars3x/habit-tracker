from py_vapid import Vapid

vapid = Vapid()
private_key, public_key = vapid.generate_keys()

print(f"VAPID_PRIVATE_KEY={private_key}")
print(f"VAPID_PUBLIC_KEY={public_key.decode('utf-8')}")
