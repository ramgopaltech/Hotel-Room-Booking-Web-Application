import random
import string
from functools import wraps
from datetime import datetime, date
from flask import session, flash, redirect, url_for, request
from models import db, User, Room, RoomImage, Booking, Payment, Review

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('main.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Admin authentication required.', 'warning')
            return redirect(url_for('main.login', next=request.url))
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('Access denied. Administrator privileges required.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


def generate_booking_id():
    """Generate unique booking code like HB-8X92F"""
    chars = string.ascii_uppercase + string.digits
    suffix = ''.join(random.choices(chars, k=6))
    return f"HB-{suffix}"


def generate_transaction_id():
    """Generate unique transaction code like TXN-9418247"""
    digits = ''.join(random.choices(string.digits, k=8))
    return f"TXN-{digits}"


def is_room_available(room_id, check_in_date, check_out_date, exclude_booking_id=None):
    """
    Check if a room is available between check_in and check_out.
    Overlapping condition: 
    (Booking.check_in < new_check_out) AND (Booking.check_out > new_check_in)
    """
    if isinstance(check_in_date, str):
        check_in_date = datetime.strptime(check_in_date, '%Y-%m-%d').date()
    if isinstance(check_out_date, str):
        check_out_date = datetime.strptime(check_out_date, '%Y-%m-%d').date()

    query = Booking.query.filter(
        Booking.room_id == room_id,
        Booking.booking_status.in_(['Confirmed', 'Pending']),
        Booking.check_in < check_out_date,
        Booking.check_out > check_in_date
    )

    if exclude_booking_id:
        query = query.filter(Booking.id != exclude_booking_id)

    overlapping = query.first()
    return overlapping is None


def seed_initial_data():
    """Seed initial luxury rooms, admin, sample customer, and sample reviews if database is empty."""
    # Check if admin exists
    admin = User.query.filter_by(email='admin@hotel.com').first()
    if not admin:
        admin = User(
            name='Grand Admin',
            email='admin@hotel.com',
            phone='+1 800 555 0199',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)

    # Check if sample customer exists
    customer = User.query.filter_by(email='john@example.com').first()
    if not customer:
        customer = User(
            name='John Doe',
            email='john@example.com',
            phone='+1 555 014 2891',
            is_admin=False
        )
        customer.set_password('user123')
        db.session.add(customer)

    db.session.commit()

    # Check if rooms exist
    if Room.query.count() == 0:
        seed_rooms = [
            {
                'room_name': 'Royal Imperial Suite',
                'room_number': '101',
                'type': 'Penthouse',
                'capacity': 4,
                'price': 850.0,
                'description': 'Experience uncompromised grandeur in our flagship Royal Imperial Suite. Featuring panoramic ocean views, private marble jacuzzi, personal butler service, handcrafted gold accents, and a expansive wrap-around private terrace.',
                'wifi': True,
                'ac': True,
                'breakfast': True,
                'tv': True,
                'image': '/static/images/room_penthouse.jpg',
                'rating': 5.0,
                'additional_images': [
                    '/static/images/room_penthouse_2.jpg',
                    '/static/images/room_penthouse_3.jpg'
                ]
            },
            {
                'room_name': 'Grand Oceanfront Villa',
                'room_number': '102',
                'type': 'Suite',
                'capacity': 3,
                'price': 620.0,
                'description': 'Sublime coastal luxury with floor-to-ceiling glass walls directly overlooking pristine sapphire waters. Includes a king-size plush bed, infinity balcony, complimentary vintage wine bar, and rain shower.',
                'wifi': True,
                'ac': True,
                'breakfast': True,
                'tv': True,
                'image': '/static/images/room_ocean.jpg',
                'rating': 4.9,
                'additional_images': [
                    '/static/images/room_ocean_2.jpg'
                ]
            },
            {
                'room_name': 'Executive Skyline Suite',
                'room_number': '201',
                'type': 'Executive',
                'capacity': 2,
                'price': 450.0,
                'description': 'Tailored for discerning business travelers and couples seeking urban sophistication. Features ergonomic work studio, high-speed fiber Wi-Fi, executive club lounge access, and acoustic soundproofing.',
                'wifi': True,
                'ac': True,
                'breakfast': True,
                'tv': True,
                'image': '/static/images/room_executive.jpg',
                'rating': 4.8,
                'additional_images': []
            },
            {
                'room_name': 'Deluxe Garden Haven',
                'room_number': '202',
                'type': 'Deluxe',
                'capacity': 2,
                'price': 320.0,
                'description': 'Immerse yourself in lush botanical surroundings. Soft natural lighting, bespoke wooden furnishings, Egyptian cotton linens, and a cozy private garden deck.',
                'wifi': True,
                'ac': True,
                'breakfast': False,
                'tv': True,
                'image': '/static/images/room_deluxe.jpg',
                'rating': 4.7,
                'additional_images': []
            },
            {
                'room_name': 'Classic Elegance Room',
                'room_number': '301',
                'type': 'Standard',
                'capacity': 2,
                'price': 220.0,
                'description': 'Timeless comfort paired with modern convenience. Designed for relaxing getaways with ambient dimming lights, smart entertainment hub, and premium bath amenities.',
                'wifi': True,
                'ac': True,
                'breakfast': False,
                'tv': True,
                'image': '/static/images/room_classic.jpg',
                'rating': 4.6,
                'additional_images': []
            },
            {
                'room_name': 'Presidential Ocean Sanctuary',
                'room_number': '302',
                'type': 'Penthouse',
                'capacity': 5,
                'price': 1100.0,
                'description': 'The pinnacle of luxury hospitality. Spanning 2,500 sq ft across the top floor with private plunge pool, private elevator access, wine cellar, and 360-degree panoramic ocean and city views.',
                'wifi': True,
                'ac': True,
                'breakfast': True,
                'tv': True,
                'image': '/static/images/room_presidential.jpg',
                'rating': 5.0,
                'additional_images': []
            }
        ]

        for r_data in seed_rooms:
            add_imgs = r_data.pop('additional_images', [])
            room = Room(**r_data)
            db.session.add(room)
            db.session.flush()
            for img_path in add_imgs:
                db.session.add(RoomImage(room_id=room.id, image_url=img_path))
        
        db.session.commit()

        # Seed sample reviews
        first_room = Room.query.first()
        if first_room and customer:
            rev1 = Review(
                user_id=customer.id,
                room_id=first_room.id,
                rating=5,
                comment="Absolute perfection! The view from the balcony during sunset was breathtaking and the staff made our stay unforgettable."
            )
            db.session.add(rev1)
            db.session.commit()
