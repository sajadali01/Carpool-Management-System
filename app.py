from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, request, flash, redirect, url_for, render_template, session
import secrets
import json
from authlib.integrations.flask_client import OAuth
import re
from urllib.parse import quote_plus, urlencode
from models.car_owner import CarOwner
from config import Config
from models.ride import Ride
from models.route import Route
from models.user import User
from models.vehicle import Vehicle
from datetime import date
from init import app, db

oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=Config.AUTH0_CLIENT_ID,
    client_secret=Config.AUTH0_CLIENT_SECRET,
    client_kwargs={"scope": "openid profile email"},
    server_metadata_url=f'https://{Config.AUTH0_DOMAIN}/.well-known/openid-configuration'
)


@app.route('/')
def index():
    print(User.query.all())
    user = session.get("user")
    
    daily_vehicles = Vehicle.query.filter_by(duration='daily').all()
    monthly_vehicles = Vehicle.query.filter_by(duration='monthly').all()
    semester_vehicles = Vehicle.query.filter_by(duration='semester').all()
    
    # Render the template with the data
    return render_template(
        "index.html", 
        session=user, 
        daily_vehicles=daily_vehicles,
        monthly_vehicles=monthly_vehicles,
        semester_vehicles=semester_vehicles
    )



import re

@app.route("/callback", methods=["GET", "POST"])
def callback():
    try:
        token = oauth.auth0.authorize_access_token()
        session["user"] = token
        user_info = token.get("userinfo")
        
        user_name = user_info.get("name")
        email = user_info.get("email")

        if user_name and email:
            patterns = [
                r'[a-zA-Z]\d{6}',               
                r'\d{2}[a-zA-Z]-\d{4}'          
            ]
            for pattern in patterns:
                user_name = re.sub(pattern, '', user_name)
            
            user_name = user_name.strip()

            if not user_name:
                flash("Invalid user name. Please try again.", "danger")
                return redirect(url_for("index"))

            existing_user = User.query.filter_by(email=email).first()
            if not existing_user:
                new_user = User(user_name=user_name, email=email)
                db.session.add(new_user)
                db.session.commit()
    except Exception as e:
        app.logger.error(f"Authentication failed: {e}")
        flash("Authentication failed. Please try again.", "danger")
        return redirect(url_for("index"))

    return redirect(url_for("index"))


@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        f"https://{Config.AUTH0_DOMAIN}/v2/logout?"
        + urlencode({
            "returnTo": url_for("index", _external=True),
            "client_id": Config.AUTH0_CLIENT_ID,
        }, quote_via=quote_plus)
    )


@app.route('/add_vehicle', methods=['POST'])
def add_vehicle():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    try:
        user_info = session['user']['userinfo']
        
        owner_name = user_info.get('given_name')
        print(f"Owner Name: {owner_name}")
        email = user_info.get('email')

        # Fetch or create the CarOwner record
        owner = CarOwner.query.filter_by(email=email).first()
        if not owner:
            owner = CarOwner(
                email=email,
                name=owner_name,
                whatsapp_number=request.form['whatsapp_num'],
                off_day=request.form['off_day'],
            )
            db.session.add(owner)
            db.session.flush()

        # Create the Route record
        route = Route(
            pickup_location=request.form['from'],
            dropoff_location=request.form['to']
        )
        db.session.add(route)
        db.session.flush()

        vehicle_duration = request.form['duration']  # Capture the duration field

        # Create the Vehicle record
        vehicle = Vehicle(
            vehicle_name=request.form['carname'],
            vehicle_description=request.form['car_description'],
            number_plate=request.form['number_plate'],
            vehicle_type=request.form['vehicle_type'],
            # available_seats=int(request.form['seats']) if request.form['seats'] <= 4 else int(request.form['custom_seats']),
            available_seats=int(request.form['seats']),
            duration=vehicle_duration,  # Store the captured duration here
            owner_id=owner.owner_id
        )
        if vehicle.available_seats < 1:
            raise Exception("Available Seats less than 1")
        db.session.add(vehicle)

        # Create the Ride record
        ride = Ride(
            user_id=session['user']['userinfo'].get('sub'),
            owner_id=owner.owner_id,
            route_id=route.route_id,
            date=date.today(),
            departure_time=request.form['departure_time'],
            return_time=request.form['return_time']
        )
        db.session.add(ride)

        db.session.commit()
        return jsonify({'success': True}), 200
    
    
    except Exception as e:
        db.session.rollback()   #optional
        app.logger.error(f"Error while adding vehicle: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/add_vehicle')
def add_vehicle_page():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('add_vehicle.html')


@app.route('/delete_vehicle', methods=['GET', 'POST'])
def delete_vehicle():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_info = session['user']['userinfo']
    email = user_info.get('email')
    owner = CarOwner.query.filter_by(email=email).first()

    if not owner:
        flash("You do not have any associated vehicles.", "info")
        return redirect(url_for('index'))

    if request.method == 'GET':
        vehicles = Vehicle.query.filter_by(owner_id=owner.owner_id).all()
        return render_template('delete_vehicle.html', vehicles=vehicles)
    
    if request.method == 'POST':
        vehicle_id = request.form.get('vehicle_id')
        if not vehicle_id:
            flash("Invalid vehicle selected.", "danger")
            return redirect(url_for('delete_vehicle'))
        
        try:
            vehicle = Vehicle.query.filter_by(vehicle_id=vehicle_id).first()
            if not vehicle:
                flash("Vehicle not found.", "danger")
                return redirect(url_for('delete_vehicle'))

            # Delete related rides
            rides = Ride.query.filter_by(vehicle_id=vehicle_id).all()
            for ride in rides:
                db.session.delete(ride)

            # Delete vehicle
            db.session.delete(vehicle)
            db.session.commit()
            flash("Vehicle deleted successfully.", "success")
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error deleting vehicle: {e}")
            flash("An error occurred while deleting the vehicle.", "danger")
        
        return redirect(url_for('delete_vehicle'))




@app.route('/edit_vehicle', methods=['GET', 'POST'])
def edit_vehicle():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_info = session['user']['userinfo']
    email = user_info.get('email')
    owner = CarOwner.query.filter_by(email=email).first()

    if not owner:
        flash("You do not have any associated vehicles.", "info")
        return redirect(url_for('index'))

    if request.method == 'GET':
        vehicles = Vehicle.query.filter_by(owner_id=owner.owner_id).all()
        return render_template('edit_vehicle.html', vehicles=vehicles, owner=owner)
    
    if request.method == 'POST':
        vehicle_id = request.form.get('vehicle_id')
        if not vehicle_id:
            return render_template(
                'edit_vehicle.html', 
                vehicles=Vehicle.query.filter_by(owner_id=owner.owner_id).all(), 
                owner=owner, 
                error_message="Invalid vehicle selected."
            )
        
        try:
            # Check if the number plate already exists for another vehicle
            new_number_plate = request.form['number_plate']
            existing_vehicle = Vehicle.query.filter_by(number_plate=new_number_plate).first()
            if existing_vehicle and existing_vehicle.vehicle_id != int(vehicle_id):
                raise Exception(f"Number plate '{new_number_plate}' is already in use.")

            # Update the selected vehicle details
            vehicle = Vehicle.query.filter_by(vehicle_id=vehicle_id).first()
            if not vehicle:
                raise Exception("Vehicle not found.")
            
            vehicle.vehicle_name = request.form['vehicle_name']
            vehicle.vehicle_description = request.form['vehicle_description']
            vehicle.number_plate = new_number_plate
            vehicle.vehicle_type = request.form['vehicle_type']
            vehicle.available_seats = int(request.form['available_seats'])
            vehicle.duration = request.form['duration']

            if vehicle.available_seats < 1:
                raise Exception("Available seats must be at least 1.")
            
            # Update owner details
            owner.whatsapp_number = request.form['whatsapp_number']
            owner.off_day = request.form['off_day']

            db.session.commit()
            flash("Vehicle and owner details updated successfully.", "success")
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error editing vehicle: {e}")
            return render_template(
                'edit_vehicle.html',
                vehicles=Vehicle.query.filter_by(owner_id=owner.owner_id).all(),
                owner=owner,
                error_message=str(e)
            )
        
        return redirect(url_for('edit_vehicle'))


@app.route('/get_vehicle_details/<int:vehicle_id>', methods=['GET'])
def get_vehicle_details(vehicle_id):
    if 'user' not in session:
        return jsonify({"error": "Unauthorized access"}), 401

    vehicle = Vehicle.query.filter_by(vehicle_id=vehicle_id).first()
    if not vehicle:
        return jsonify({"error": "Vehicle not found"}), 404

    owner = vehicle.owner

    response = {
        "vehicle_name": vehicle.vehicle_name,
        "vehicle_description": vehicle.vehicle_description,
        "number_plate": vehicle.number_plate,
        "vehicle_type": vehicle.vehicle_type,
        "available_seats": vehicle.available_seats,
        "duration": vehicle.duration,
        "whatsapp_number": owner.whatsapp_number,
        "off_day": owner.off_day
    }
    return jsonify(response), 200






@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=Config.PORT, debug=True)
