from init import db
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Time, Date
from sqlalchemy.orm import relationship
class Ride(db.Model):
    __tablename__ = 'rides'
    
    ride_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)  
    date= db.Column(db.Date)
    departure_time= db.Column(db.String(20))
    return_time= db.Column(db.String(20))
    
    owner_id = db.Column(db.Integer, db.ForeignKey('car_owners.owner_id'), nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.route_id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.vehicle_id', ondelete="CASCADE"))
