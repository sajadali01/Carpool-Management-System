from init import db
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Time, Date
from sqlalchemy.orm import relationship

    
class CarOwner(db.Model):
    __tablename__ = 'car_owners'
    
    owner_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True, nullable=False)
    whatsapp_number = db.Column(db.String(15), unique=True, nullable=False)
    off_day = db.Column(db.String(30))
    
    vehicles = db.relationship('Vehicle', backref='owner', lazy=True)
    rides = db.relationship('Ride', backref='owner', lazy=True)

