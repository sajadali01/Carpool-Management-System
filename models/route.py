from init import db
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Time, Date
from sqlalchemy.orm import relationship
class Route(db.Model):
    __tablename__ = 'routes'
    
    route_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pickup_location = db.Column(db.String(200), nullable=False)
    dropoff_location = db.Column(db.String(200), nullable=False)
    # one to many relationship(each route can have mutiple rides)
    rides = db.relationship('Ride', backref='route', lazy=True)