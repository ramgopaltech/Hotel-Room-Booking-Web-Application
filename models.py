from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    bookings = db.relationship('Booking', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'is_admin': self.is_admin,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


class Room(db.Model):
    __tablename__ = 'rooms'

    id = db.Column(db.Integer, primary_key=True)
    room_name = db.Column(db.String(120), nullable=False)
    room_number = db.Column(db.String(20), unique=True, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # Suite, Deluxe, Executive, Penthouse, Standard
    capacity = db.Column(db.Integer, nullable=False, default=2)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    wifi = db.Column(db.Boolean, default=True)
    ac = db.Column(db.Boolean, default=True)
    breakfast = db.Column(db.Boolean, default=False)
    tv = db.Column(db.Boolean, default=True)
    image = db.Column(db.String(255), nullable=False)  # Primary image path/URL
    status = db.Column(db.String(20), default='Available')  # Available, Maintenance
    rating = db.Column(db.Float, default=4.9)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    additional_images = db.relationship('RoomImage', backref='room', cascade='all, delete-orphan', lazy=True)
    bookings = db.relationship('Booking', backref='room', lazy=True)
    reviews = db.relationship('Review', backref='room', cascade='all, delete-orphan', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'room_name': self.room_name,
            'room_number': self.room_number,
            'type': self.type,
            'capacity': self.capacity,
            'price': self.price,
            'description': self.description,
            'wifi': self.wifi,
            'ac': self.ac,
            'breakfast': self.breakfast,
            'tv': self.tv,
            'image': self.image,
            'status': self.status,
            'rating': self.rating,
            'images': [img.image_url for img in self.additional_images]
        }


class RoomImage(db.Model):
    __tablename__ = 'room_images'

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)


class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    guests = db.Column(db.Integer, nullable=False, default=1)
    total_price = db.Column(db.Float, nullable=False)
    booking_status = db.Column(db.String(20), default='Confirmed')  # Pending, Confirmed, Cancelled, Completed
    payment_status = db.Column(db.String(20), default='Unpaid')  # Unpaid, Paid, Refunded
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    payment = db.relationship('Payment', backref='booking', uselist=False, cascade='all, delete-orphan')

    @property
    def total_nights(self):
        if self.check_in and self.check_out:
            delta = self.check_out - self.check_in
            return max(1, delta.days)
        return 1

    def to_dict(self):
        return {
            'id': self.id,
            'booking_id': self.booking_id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else 'N/A',
            'room_id': self.room_id,
            'room_name': self.room.room_name if self.room else 'N/A',
            'room_number': self.room.room_number if self.room else 'N/A',
            'check_in': self.check_in.strftime('%Y-%m-%d'),
            'check_out': self.check_out.strftime('%Y-%m-%d'),
            'total_nights': self.total_nights,
            'guests': self.guests,
            'total_price': self.total_price,
            'booking_status': self.booking_status,
            'payment_status': self.payment_status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M')
        }


class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)  # Credit Card, UPI, PayPal, NetBanking
    status = db.Column(db.String(20), default='Success')  # Success, Failed, Refunded
    transaction_id = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False, default=5)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
