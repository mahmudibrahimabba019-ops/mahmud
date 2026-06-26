import json
import urllib.request
import urllib.error

API = 'http://127.0.0.1:8001'
headers = {'Content-Type': 'application/json'}

try:
    # Create guest customer
    cust = {
        'email': 'test+automation@example.com',
        'phone': '08000000002',
        'first_name': 'Auto',
        'last_name': 'Tester',
        'address': '123 Script Lane',
        'city': 'Scriptville',
        'state': 'SV',
        'password': ''
    }
    req = urllib.request.Request(API + '/customers/guest', data=json.dumps(cust).encode('utf-8'), headers=headers)
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read().decode())
    print('Customer create response:', data)
    customer_id = data.get('customer_id')

    # Create order with payment_reference
    order = {
        'customer_id': customer_id,
        'items': [
            {
                'product_id': 1,
                'product_name': 'All spice',
                'quantity': 1,
                'price_at_time': 8000,
                'subtotal': 8000
            }
        ],
        'subtotal': 8000,
        'delivery_fee': 3000,
        'total_amount': 11000,
        'delivery_address': '123 Script Lane',
        'delivery_phone': '08000000002',
        'delivery_city': 'Scriptville',
        'delivery_state': 'SV',
        'delivery_note': '',
        'payment_reference': 'PYTEST-REF-12345'
    }
    req2 = urllib.request.Request(API + '/orders/create', data=json.dumps(order).encode('utf-8'), headers=headers)
    resp2 = urllib.request.urlopen(req2, timeout=10)
    data2 = json.loads(resp2.read().decode())
    print('Order create response:', data2)
    order_id = data2.get('order_id')

    # Fetch created order
    resp3 = urllib.request.urlopen(API + f'/orders/{order_id}', timeout=10)
    data3 = json.loads(resp3.read().decode())
    print('Fetched order:', data3)
    print('\nPersisted payment_reference:', data3.get('payment_reference'))

except urllib.error.HTTPError as e:
    try:
        body = e.read().decode()
    except Exception:
        body = ''
    print('HTTPError:', e.code, e.reason, body)
except Exception as e:
    print('Error:', e)
