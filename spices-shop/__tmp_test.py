import json
import os
import hmac
import hashlib
import urllib.request
import urllib.error
import sys
from pathlib import Path
from database import SessionLocal
import models

BASE = 'http://127.0.0.1:8002'


def read_env():
    env = {}
    for line in Path('.env').read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if line and '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip()
    return env


def request_json(method, path, data=None, headers=None):
    body = None
    req_headers = {}
    if headers:
        req_headers.update(headers)
    if data is not None:
        body = json.dumps(data).encode('utf-8')
        req_headers['Content-Type'] = 'application/json'
    req = urllib.request.Request(BASE + path, data=body, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read().decode('utf-8')
            try:
                payload = json.loads(raw)
            except Exception:
                payload = raw
            return resp.status, payload
    except urllib.error.HTTPError as e:
        raw = e.read().decode('utf-8')
        try:
            payload = json.loads(raw)
        except Exception:
            payload = raw
        return e.code, payload
    except Exception as e:
        return 599, {'error': str(e)}


def get_order_state(order_number):
    db = SessionLocal()
    try:
        order = db.query(models.Order).filter(models.Order.order_number == order_number).first()
        if not order:
            return None
        items = db.query(models.OrderItem).filter(models.OrderItem.order_id == order.id).all()
        stock = []
        for it in items:
            prod = db.query(models.Product).filter(models.Product.id == it.product_id).first()
            stock.append((it.product_id, it.product_name, it.quantity, prod.stock_quantity if prod else None))
        return {
            'order_id': order.id,
            'order_number': order.order_number,
            'payment_reference': order.payment_reference,
            'payment_status': order.payment_status,
            'status': order.status,
            'total_amount': order.total_amount,
            'stock': stock,
        }
    finally:
        db.close()


def main():
    env = read_env()
    secret = env['PAYSTACK_SECRET_KEY']
    db = SessionLocal()
    try:
        order = db.query(models.Order).filter(models.Order.payment_status == 'paid').order_by(models.Order.id.desc()).first()
    finally:
        db.close()
    reference = order.payment_reference if order else None
    amount_kobo = int(round(order.total_amount * 100)) if order else None
    payload = {
        'event': 'charge.success',
        'data': {
            'reference': reference,
            'amount': amount_kobo,
            'status': 'success'
        }
    }
    raw_body = json.dumps(payload).encode('utf-8')
    sig = hmac.new(secret.encode('utf-8'), raw_body, hashlib.sha512).hexdigest()
    headers = {'x-paystack-signature': sig}
    before = get_order_state(order.order_number)
    status1, body1 = request_json('POST', '/webhook/paystack', payload, headers)
    status2, body2 = request_json('POST', '/webhook/paystack', payload, headers)
    after = get_order_state(order.order_number)
    results = {
        'test1': {
            'reference': reference,
            'amount_kobo': amount_kobo,
            'status1': status1,
            'body1': body1,
            'status2': status2,
            'body2': body2,
            'before': before,
            'after': after,
            'stock_changed_second_time': before['stock'] != after['stock'],
        }
    }

    verify_cases = [
        ('fake', 'HHS-FAKE00000000'),
        ('malformed', 'random-ref'),
        ('blank', ' '),
    ]
    verify_results = []
    for name, ref in verify_cases:
        status, body = request_json('GET', f'/api/verify-payment/{urllib.parse.quote(ref)}')
        verify_results.append({'case': name, 'reference': ref, 'status': status, 'body': body})

    # pick an unpaid order if possible
    db = SessionLocal()
    try:
        unpaid = db.query(models.Order).filter(models.Order.payment_status != 'paid').order_by(models.Order.id.desc()).first()
    finally:
        db.close()
    if unpaid:
        verify_results.append({'case': 'unpaid_order', 'reference': unpaid.payment_reference, 'status': None, 'body': None})
        status, body = request_json('GET', f'/api/verify-payment/{urllib.parse.quote(unpaid.payment_reference)}')
        verify_results[-1]['status'] = status
        verify_results[-1]['body'] = body

    bad_payload = {'event': 'charge.success', 'data': {'reference': reference, 'amount': amount_kobo, 'status': 'success'}}
    status_bad, body_bad = request_json('POST', '/webhook/paystack', bad_payload, {'x-paystack-signature': 'bad-signature'})
    results['test3'] = {'signature_status': status_bad, 'signature_body': body_bad}
    results['test2'] = verify_results
    Path('__tmp_test_results.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
    print(json.dumps(results, indent=2))

if __name__ == '__main__':
    import urllib.parse
    main()
