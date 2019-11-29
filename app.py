from flask import Flask
import cfg
import requests
from requests.auth import HTTPBasicAuth
import random
from faker import Faker

app = Flask(__name__)
fake = Faker()

def authenticate():
    if cfg.ENV == "production":
        base_safaricom_url = cfg.LIVE_URL
    else:
        base_safaricom_url = cfg.SANDBOX_URL
    authenticate_uri = "/oauth/v1/generate?grant_type=client_credentials"
    authenticate_url = "{0}{1}".format(base_safaricom_url, authenticate_uri)
    r = requests.get(authenticate_url,auth=HTTPBasicAuth(cfg.CONSUMER_KEY, cfg.CONSUMER_SECRET))
    token = r.json()['access_token']
    return token

@app.route('/register')
def register():
    """This method uses Mpesa's C2B API to register validation and confirmation URLs on M-Pesa.
   **Returns:**
       - OriginatorConversationID (str): The unique request ID for tracking a transaction.
       - ConversationID (str): The unique request ID returned by mpesa for each request made
       - ResponseDescription (str): Response Description message
"""
    payload = {
        "ShortCode": cfg.SHORTCODE,
        "ResponseType": cfg.RESPONSE_TYPE,
        "ConfirmationURL": cfg.CONFIRMATION_URL,
        "ValidationURL": cfg.VALIDATION_URL
    }
    headers = {'Authorization': 'Bearer {0}'.format(authenticate()), 'Content-Type': "application/json"}
    if cfg.ENV == "production":
        base_safaricom_url = cfg.LIVE_URL
    else:
        base_safaricom_url = cfg.SANDBOX_URL
    saf_url = "{0}{1}".format(base_safaricom_url, "/mpesa/c2b/v1/registerurl")
    r = requests.post(saf_url, headers=headers, json=payload)
    return r.json()
@app.route('/confirmation')
def confirm():
    return 'Hello World!'
@app.route('/validation')
def validate():
    return 'Hello World!'
@app.route('/simulate')
def simulate():
    payload = {
        "ShortCode": cfg.SHORTCODE,
        "CommandID": "CustomerPayBillOnline", #CustomerPayBillOnline|CustomerBuyGoodsOnline
        "Amount": 5,
        "Msisdn": cfg.TEST_MSISDN,
        "BillRefNumber": fake.text(max_nb_chars=10)
    }
    headers = {'Authorization': 'Bearer {0}'.format(authenticate()), 'Content-Type': "application/json"}
    if cfg.ENV == "production":
        base_safaricom_url = cfg.LIVE_URL
    else:
        base_safaricom_url = cfg.SANDBOX_URL
    saf_url = "{0}{1}".format(base_safaricom_url, "/mpesa/c2b/v1/simulate")
    r = requests.post(saf_url, headers=headers, json=payload)
    return r.json()
@app.route('/reverse')
def reverse():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
