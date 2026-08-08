import os, requests, hmac, hashlib, json
from dotenv import load_dotenv
load_dotenv()

BASE = "http://127.0.0.1:8001"  # UPDATE THIS to match the actual confirmed port from step 1
secret = os.getenv("PAYSTACK_SECRET_KEY").encode()

payload = {
    "event": "charge.success",
    "data": {"reference": "HHS-3D7910F74F8D", "amount": 700000, "status": "success"}
}
body = json.dumps(payload).encode()
sig = hmac.new(secret, body, hashlib.sha512).hexdigest()
headers = {"Content-Type": "application/json", "x-paystack-signature": sig}

r1 = requests.post(f"{BASE}/webhook/paystack", data=body, headers=headers)
print("CALL 1:", r1.status_code, r1.text)

r2 = requests.post(f"{BASE}/webhook/paystack", data=body, headers=headers)
print("CALL 2:", r2.status_code, r2.text)

r3 = requests.post(f"{BASE}/webhook/paystack", data=body, headers={"Content-Type": "application/json", "x-paystack-signature": "invalid"})
print("BAD SIG CALL:", r3.status_code, r3.text)

r4 = requests.get(f"{BASE}/api/verify-payment/HHS-FAKE00000000")
print("FAKE REF:", r4.status_code, r4.text)
