from py_vapid import Vapid01

vapid = Vapid01()
vapid.generate_keys()

with open("vapid_private.pem", "wb") as f:
    f.write(vapid.private_pem())

with open("vapid_public.pem", "wb") as f:
    f.write(vapid.public_pem())

print("Keys generated")