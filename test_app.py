import unittest
from datetime import date, timedelta
from app import create_app
from models import db, User, Room, Booking, Payment, Review

class TestHotelBookingApp(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_01_homepage_and_rooms(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'GRAND ROYALE', res.data)

        res_rooms = self.client.get('/rooms')
        self.assertEqual(res_rooms.status_code, 200)
        self.assertIn(b'Accommodations', res_rooms.data)

    def test_02_authentication(self):
        # Test Login with Admin
        res_login = self.client.post('/login', data={
            'email': 'admin@hotel.com',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertEqual(res_login.status_code, 200)
        self.assertIn(b'Admin Panel', res_login.data)

        # Logout
        self.client.get('/logout')

        # Test Registration
        res_reg = self.client.post('/register', data={
            'name': 'Test Guest',
            'email': 'testguest@hotel.com',
            'phone': '+1 555 999 1111',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(res_reg.status_code, 200)
        self.assertIn(b'GRAND ROYALE', res_reg.data)

    def test_03_booking_and_payment_flow(self):
        self.client.get('/logout')
        self.client.post('/login', data={
            'email': 'john@example.com',
            'password': 'user123'
        })

        with self.app.app_context():
            room = Room.query.first()
            room_id = room.id

        today = date.today()
        check_in = today + timedelta(days=10)
        check_out = today + timedelta(days=13)

        # Initiate booking
        res_book = self.client.post(f'/book/initiate/{room_id}', data={
            'check_in': check_in.strftime('%Y-%m-%d'),
            'check_out': check_out.strftime('%Y-%m-%d'),
            'guests': 2
        }, follow_redirects=True)
        
        self.assertEqual(res_book.status_code, 200)
        self.assertIn(b'HB-', res_book.data)

        # Check booking in DB
        with self.app.app_context():
            booking = Booking.query.filter_by(user_id=2).order_by(Booking.id.desc()).first()
            booking_id = booking.booking_id
            self.assertEqual(booking.booking_status, 'Pending')

        # Process Payment
        res_pay = self.client.post(f'/payment/process/{booking_id}', data={
            'payment_method': 'Credit Card',
            'status_choice': 'success'
        }, follow_redirects=True)

        self.assertEqual(res_pay.status_code, 200)
        self.assertIn(b'Confirmed', res_pay.data)

        with self.app.app_context():
            updated_booking = Booking.query.filter_by(booking_id=booking_id).first()
            self.assertEqual(updated_booking.booking_status, 'Confirmed')
            self.assertEqual(updated_booking.payment_status, 'Paid')

    def test_04_admin_access(self):
        self.client.get('/logout')
        self.client.post('/login', data={
            'email': 'admin@hotel.com',
            'password': 'admin123'
        })

        res_admin = self.client.get('/admin')
        self.assertEqual(res_admin.status_code, 200)
        self.assertIn(b'Overview Metrics', res_admin.data)

if __name__ == '__main__':
    unittest.main()
