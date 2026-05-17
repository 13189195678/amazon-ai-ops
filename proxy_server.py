import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'venv_pkgs'))

import json
import time
import requests
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='.')
CORS(app)

config_path = os.path.join(os.path.dirname(__file__), 'config.json')
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

LX_CONFIG = config['lingxing']
SERVER_CONFIG = config['server']

token_info = {
    'access_token': None,
    'expires_at': 0
}

def get_token():
    now = time.time()
    if token_info['access_token'] and now < token_info['expires_at'] - 60:
        return token_info['access_token']

    try:
        resp = requests.post(
            f"{LX_CONFIG['api_base_url']}/auth/login",
            json={
                'account_id': LX_CONFIG['account_id'],
                'api_key': LX_CONFIG['api_key']
            },
            timeout=10
        )
        data = resp.json()
        if data.get('code') == 0:
            token_info['access_token'] = data['data']['token']
            token_info['expires_at'] = now + 7200
            return token_info['access_token']
        else:
            raise Exception(f"Auth failed: {data.get('message')}")
    except Exception as e:
        raise Exception(f"Auth error: {str(e)}")

def call_lx_api(endpoint, params=None):
    token = get_token()
    headers = {'Authorization': f'Bearer {token}'}
    url = f"{LX_CONFIG['api_base_url']}{endpoint}"
    resp = requests.post(url, json=params or {}, headers=headers, timeout=30)
    data = resp.json()
    if data.get('code') == 0:
        return data.get('data', {})
    raise Exception(f"API error: {data.get('message', 'unknown')}")

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'configured': LX_CONFIG['account_id'] != 'YOUR_ACCOUNT_ID'})

@app.route('/api/sales')
def api_sales():
    try:
        sales_data = call_lx_api('/erp/sc/data/sales/daily', {
            'start_date': time.strftime('%Y-%m-%d', time.localtime(time.time() - 15*86400)),
            'end_date': time.strftime('%Y-%m-%d'),
            'page': 1,
            'page_size': 100
        })
        return jsonify({'code': 0, 'data': sales_data})
    except Exception as e:
        return jsonify({'code': -1, 'message': str(e)})

@app.route('/api/inventory')
def api_inventory():
    try:
        inv_data = call_lx_api('/erp/sc/data/local_inventory/warehouse', {
            'type': 3,
            'is_delete': 0,
            'offset': 0,
            'length': 100
        })
        return jsonify({'code': 0, 'data': inv_data})
    except Exception as e:
        return jsonify({'code': -1, 'message': str(e)})

@app.route('/api/forecast')
def api_forecast():
    try:
        forecast_data = call_lx_api('/erp/sc/data/forecast/monthly', {
            'start_month': time.strftime('%Y-%m'),
            'months': 6
        })
        return jsonify({'code': 0, 'data': forecast_data})
    except Exception as e:
        return jsonify({'code': -1, 'message': str(e)})

if __name__ == '__main__':
    app.run(
        host=SERVER_CONFIG['host'],
        port=SERVER_CONFIG['port'],
        debug=False
    )