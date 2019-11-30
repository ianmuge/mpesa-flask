import requests
from requests.auth import HTTPBasicAuth
import random
import cfg
from flask import *
from app import db,app
from models import *
from faker import Faker
import traceback, logging
from flask_paginate import Pagination, get_page_parameter


fake = Faker()
logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)

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

@app.route('/')
def index():
    transactions = Transaction.query.order_by(Transaction.timestamp.desc())
    page = request.args.get(get_page_parameter(), type=int, default=1)
    pagination = Pagination(page=page, total=transactions.count(), record_name='transactions', css_framework='bootstrap4')
    return render_template('index.html',transactions=transactions,pagination=pagination)
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
@app.route('/validation',methods=["POST"])
def validation():

    app.logger.info(request.get_data())
    logger.info(request.get_data())
    req = request.get_json()
    try:
        transaction = Transaction(
            TransID=req["TransID"],
            TransTime=req["TransTime"],
            TransAmount=req["TransAmount"],
            BillRefNumber=req["BillRefNumber"],
            MSISDN=req["MSISDN"],
            FirstName=req["FirstName"],
            MiddleName=req["MiddleName"],
            LastName=req["LastName"],
            validated=True,
            validation_timestamp=datetime.now()
        )
        db.session.add(transaction)
        db.session.commit()
        response = {"ResultCode": 0, "ResultDesc": "Accepted"}
    except Exception as exc:
        db.session.rollback()
        app.logger.exception('Exception: {0}'.format(exc))
        logger.exception('Exception: {0}'.format(exc))
        response = {"ResultCode": 1, "ResultDesc": "Rejected"}
    finally:
         return response

@app.route('/confirmation',methods=["POST"])
def confirmation():
    """
    {
      "TransactionType": "",
      "TransID": "NKU01HAV1U",
      "TransTime": "20191130011327",
      "TransAmount": "5.00",
      "BusinessShortCode": "600357",
      "BillRefNumber": "Somebody.",
      "InvoiceNumber": "",
      "OrgAccountBalance": "",
      "ThirdPartyTransID": "",
      "MSISDN": "254708374149",
      "FirstName": "John",
      "MiddleName": "J.",
      "LastName": "Doe"
    }
    """
    app.logger.info(request.get_data())
    logger.info(request.get_data())
    req=request.get_json()
    try:
        transaction = Transaction.query.filter_by(TransID = req["TransID"]).first()
        transaction.confirmation_timestamp = datetime.now()
        transaction.confirmed = True
        db.session.add(transaction)
        db.session.commit()
        response={"ResultCode": 0,"ResultDesc": "Accepted"}
        return response
    except Exception as exc:
        db.session.rollback()
        app.logger.exception('Exception: {0}'.format(exc))
        logger.exception('Exception: {0}'.format(exc))
        response = {"ResultCode": 1, "ResultDesc": "Rejected"}
    finally:
        return response
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


