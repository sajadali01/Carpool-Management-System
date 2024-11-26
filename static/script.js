document.addEventListener('DOMContentLoaded', function() {
    showContent('daily');
});

function showContent(period) {
    const sections = document.getElementsByClassName('content-section');
    for(let section of sections) {
        section.style.display = 'none';
    }
    
    document.getElementById(period + '-content').style.display = 'block';
    
    const buttons = document.getElementsByClassName('period-btn');
    for(let button of buttons) {
        button.classList.remove('active');
    }
    event.target.classList.add('active');
}
function handleSeatsChange() {
    const seatsDropdown = document.getElementById("seats");
    const customSeatsContainer = document.getElementById("custom-seats-container");

    if (seatsDropdown.value === "four+") {
        customSeatsContainer.style.display = "block"; 
    } else {
        customSeatsContainer.style.display = "none"; 
    }
}

let map;
let fromAutocomplete;
let toAutocomplete;

function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: 24.860966, lng: 66.990501 }, 
        zoom: 13
    });

    fromAutocomplete = new google.maps.places.Autocomplete(
        document.getElementById('from-input'),
        { types: ['geocode'] }
    );
    fromAutocomplete.bindTo('bounds', map);

    toAutocomplete = new google.maps.places.Autocomplete(
        document.getElementById('to-input'),
        { types: ['geocode'] }
    );
    toAutocomplete.bindTo('bounds', map);

    const placeMarker = (autocomplete, label) => {
        autocomplete.addListener('place_changed', () => {
            const place = autocomplete.getPlace();
            if (!place.geometry) {
                console.log(`No details available for ${label}: '${place.name}'`);
                return;
            }

            if (place.geometry.viewport) {
                map.fitBounds(place.geometry.viewport);
            } else {
                map.setCenter(place.geometry.location);
                map.setZoom(17); 
            }

            new google.maps.Marker({
                position: place.geometry.location,
                map: map,
                title: label
            });
        });
    };

    placeMarker(fromAutocomplete, "Starting Location");
    placeMarker(toAutocomplete, "Destination");
}

document.addEventListener('DOMContentLoaded', function() {
    async function handleSubmit(event) {
        event.preventDefault();
        
        const formData = new FormData();
        
        formData.append('vehicle_type', document.getElementById('vehicle_type').value);
        formData.append('duration', document.getElementById('duration').value);
        formData.append('seats', document.getElementById('seats').value);
        formData.append('carname', document.getElementById('carname').value);
        formData.append('car_description', document.getElementById('car_description').value);
        formData.append('number_plate', document.getElementById('number_plate').value);
        formData.append('from', document.getElementById('from-input').value);
        formData.append('to', document.getElementById('to-input').value);
        formData.append('departure_time', document.getElementById('departure_time').value);
        formData.append('return_time', document.getElementById('return_time').value);
        formData.append('whatsapp_num', document.getElementById('whatsapp_num').value);
        formData.append('off_day', document.getElementById('off_day').value);
        
        try {
            const response = await fetch('/add_vehicle', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok) {
                alert('Vehicle added successfully!');
                window.location.href = '/';
            } else {
                console.log('hereere');
                alert('Error: ' + data.error);
            }
        } catch (error) {
            alert('Error submitting form: ' + error);
        }
    }
    
    const form = document.getElementById('add-vehicle-form');
    form.addEventListener('submit', handleSubmit);
});

function handleSeatsChange() {
    const seatsSelect = document.getElementById('seats');
    const customSeatsContainer = document.getElementById('custom-seats-container');
    
    if (seatsSelect.value === 'four+') {
        customSeatsContainer.style.display = 'block';
    } else {
        customSeatsContainer.style.display = 'none';
    }
}