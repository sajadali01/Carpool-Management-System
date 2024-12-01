from init import db
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Time, Date
from sqlalchemy.orm import relationship

    
class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    vehicle_id = db.Column(db.Integer, primary_key=True)
    vehicle_name = db.Column(db.String(100), nullable=False)
    vehicle_description = db.Column(db.String(255), nullable=True)
    number_plate = db.Column(db.String(50), unique=True, nullable=False)
    vehicle_type = db.Column(db.String(50), nullable=False)
    available_seats = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.String(50), nullable=False)  # Add this field
    
    owner_id = db.Column(db.Integer, db.ForeignKey('car_owners.owner_id'))


