from app import db
from datetime import datetime
import cfg

class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = db.Column(db.Integer, primary_key=True)
    TransID=db.Column(db.String(255))
    TransTime=db.Column(db.String(255))
    TransAmount=db.Column(db.String(255))
    BillRefNumber=db.Column(db.String(255))
    MSISDN=db.Column(db.String(255))
    FirstName=db.Column(db.String(255))
    MiddleName=db.Column(db.String(255))
    LastName=db.Column(db.String(255))
    validated=db.Column(db.Boolean)
    confirmed=db.Column(db.Boolean)
    confirmation_timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    validation_timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)