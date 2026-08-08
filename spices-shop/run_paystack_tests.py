import json
import hmac
import hashlib
import urllib.request
import urllib.error
import urllib.parse
import sqlite3
from pathlib import Path

BASE = 'http://127.0.0.1:8002'
DB_PATH = 'halari_spices.db'
OUTPUT = 'paystack_test_results.txt'


def read_secret():
    env = {}
    for line in Path('.env').read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if line and '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip()
    return env['PAYSTACK_SECRET_KEY']


def db_query(sql, params=()):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.execute(sql, params)
        return cur.fetchall()
    finally:
        conn.close()


def get_recent_paid_order():
    rows = db_query("SELECT id, order_number, payment_reference, payment_status, status, total_amount FROM orders WHERE payment_status = 'paid' ORDER BY id DESC LIMIT 1")
    return dict(rows[0]) if rows else None


def get_order(order_number):
    rows = db_query("SELECT id, order_number, payment_reference, payment_status, status, total_amount FROM orders WHERE order_number = ?", (order_number,))
    return dict(rows[0]) if rows else None


def get_order_items(order_id):
    rows = db_query("SELECT product_id, product_name, quantity FROM order_items WHERE order_id = ?", (order_id,))
    return [dict(r) for r in rows]


def get_product_stock(product_id):
    rows = db_query("SELECT stock_quantity FROM products WHERE id = ?", (product_id,))
    return dict(rows[0])['stock_quantity'] if rows else None


def send_json(method, path, payload=None, headers=None):
    data = None
    if payload is not None:
        data = json.dumps(payload).encode('utf-8')
    req_headers = {}
    if headers:
        req_headers.update(headers)
    if data is not None:
        req_headers['Content-Type'] = 'application/json'
    req = urllib.request.Request(BASE + path, data=data, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode('utf-8')
            return resp.status, body
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        return e.code, body
    except Exception as e:
        return 599, str(e)


def main():
    secret = read_secret()
    order = get_recent_paid_order()
    lines = []
    lines.append('RECENT_PAID ' + json.dumps(order, indent=2))

    # Test 1
    reference = order['payment_reference']
    amount_kobo = int(round(order['total_amount'] * 100))
    payload = {'event': 'charge.success', 'data': {'reference': reference, 'amount': amount_kobo, 'status': 'success'}}
    raw_body = json.dumps(payload).encode('utf-8')
    sig = hmac.new(secret.encode('utf-8'), raw_body, hashlib.sha512).hexdigest()
    headers = {'x-paystack-signature': sig}

    before = get_order(order['order_number'])
    before_items = get_order_items(before['id'])
    before_stocks = []
    for item in before_items:
        before_stocks.append((item['product_id'], item['product_name'], item['quantity'], get_product_stock(item['product_id'])))

    status1, body1 = send_json('POST', '/webhook/paystack', payload, headers)
    status2, body2 = send_json('POST', '/webhook/paystack', payload, headers)

    after = get_order(order['order_number'])
    after_items = get_order_items(after['id'])
    after_stocks = []
    for item in after_items:
        after_stocks.append((item['product_id'], item['product_name'], item['quantity'], get_product_stock(item['product_id'])))

    lines.append('TEST1_STATUS1 ' + str(status1))
    lines.append('TEST1_BODY1 ' + body1)
    lines.append('TEST1_STATUS2 ' + str(status2))
    lines.append('TEST1_BODY2 ' + body2)
    lines.append('TEST1_BEFORE_STOCK ' + json.dumps(before_stocks))
    lines.append('TEST1_AFTER_STOCK ' + json.dumps(after_stocks))
    lines.append('TEST1_ORDER_AFTER ' + json.dumps(after))

    # Test 2
    cases = [
        ('fake', 'HHS-FAKE00000000'),
        ('malformed', 'random-ref'),
        ('blank', ' '),
    ]
    for name, ref in cases:
        status, body = send_json('GET', '/api/verify-payment/' + urllib.parse.quote(ref))
        lines.append('TEST2 ' + name + ' ' + ref + ' ' + str(status) + ' ' + body)

    # Find unpaid order
    unpaid_rows = db_query("SELECT id, order_number, payment_reference, payment_status FROM orders WHERE payment_status != 'paid' ORDER BY id DESC LIMIT 1")
    if unpaid_rows:
        unpaid = dict(unpaid_rows[0])
        status, body = send_json('GET', '/api/verify-payment/' + urllib.parse.quote(unpaid['payment_reference']))
        lines.append('TEST2_UNPAID ' + json.dumps(unpaid) + ' ' + str(status) + ' ' + body)

    # Test3
    bad_headers = {'x-paystack-signature': 'wrong-signature'}
    status3, body3 = send_json('POST', '/webhook/paystack', payload, bad_headers)
    lines.append('TEST3_STATUS ' + str(status3))
    lines.append('TEST3_BODY ' + body3)

    Path(OUTPUT).write_text('\n'.join(lines), encoding='utf-8')

if __name__ == '__main__':
    main()
