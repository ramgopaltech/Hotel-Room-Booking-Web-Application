import os
from datetime import datetime, date
from werkzeug.utils import secure_filename
from flask import (
    Blueprint, render_template, request, redirect, 
    url_for, flash, session, jsonify, current_app
)
from models import db, User, Room, RoomImage, Booking, Payment, Review
from utils import (
    login_required, admin_required, generate_booking_id, 
    generate_transaction_id, is_room_available
)

# Blueprints Definition
main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)
booking_bp = Blueprint('booking', __name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
api_bp = Blueprint('api', __name__, url_prefix='/api')


# ==============================================================================
# MAIN BLUEPRINT (Homepage, Rooms, Room Details, Contact)
# ==============================================================================

@main_bp.route('/')
def index():
    featured_rooms = Room.query.filter_by(status='Available').limit(3).all()
    reviews = Review.query.order_by(Review.created_at.desc()).limit(5).all()
    room_types = db.session.query(Room.type).distinct().all()
    room_types = [t[0] for t in room_types]
    return render_template('index.html', 
                           featured_rooms=featured_rooms, 
                           reviews=reviews,
                           room_types=room_types)


@main_bp.route('/rooms')
def rooms():
    # Filter parameters
    room_type = request.args.get('type', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    capacity = request.args.get('capacity', type=int)
    wifi = request.args.get('wifi')
    ac = request.args.get('ac')
    breakfast = request.args.get('breakfast')
    tv = request.args.get('tv')
    sort_by = request.args.get('sort', 'recommended')
    search_q = request.args.get('q', '')

    query = Room.query

    if search_q:
        query = query.filter(Room.room_name.ilike(f'%{search_q}%') | Room.description.ilike(f'%{search_q}%'))
    if room_type:
        query = query.filter(Room.type == room_type)
    if min_price is not None:
        query = query.filter(Room.price >= min_price)
    if max_price is not None:
        query = query.filter(Room.price <= max_price)
    if capacity:
        query = query.filter(Room.capacity >= capacity)
    if wifi == '1':
        query = query.filter(Room.wifi == True)
    if ac == '1':
        query = query.filter(Room.ac == True)
    if breakfast == '1':
        query = query.filter(Room.breakfast == True)
    if tv == '1':
        query = query.filter(Room.tv == True)

    # Sorting
    if sort_by == 'price_low':
        query = query.order_by(Room.price.asc())
    elif sort_by == 'price_high':
        query = query.order_by(Room.price.desc())
    elif sort_by == 'rating':
        query = query.order_by(Room.rating.desc())
    else:
        query = query.order_by(Room.id.asc())

    all_rooms = query.all()
    room_types = db.session.query(Room.type).distinct().all()
    room_types = [t[0] for t in room_types]

    return render_template('rooms.html', 
                           rooms=all_rooms, 
                           room_types=room_types,
                           selected_type=room_type,
                           selected_sort=sort_by,
                           min_price=min_price,
                           max_price=max_price,
                           capacity=capacity,
                           wifi=wifi, ac=ac, breakfast=breakfast, tv=tv,
                           search_q=search_q)


@main_bp.route('/rooms/<int:room_id>')
def room_details(room_id):
    room = Room.query.get_or_404(room_id)
    similar_rooms = Room.query.filter(Room.id != room.id, Room.type == room.type).limit(3).all()
    reviews = Review.query.filter_by(room_id=room.id).order_by(Review.created_at.desc()).all()
    today_str = date.today().strftime('%Y-%m-%d')
    return render_template('room_details.html', room=room, similar_rooms=similar_rooms, reviews=reviews, today_str=today_str)


@main_bp.route('/contact')
def contact():
    return render_template('contact.html')


@main_bp.route('/contact/send', methods=['POST'])
def contact_send():
    name = request.form.get('name')
    email = request.form.get('email')
    subject = request.form.get('subject')
    message = request.form.get('message')
    
    flash(f"Thank you, {name}! Your message regarding '{subject}' has been received. Our concierge team will reach out shortly.", "success")
    return redirect(url_for('main.contact'))


# ==============================================================================
# AUTHENTICATION BLUEPRINT (Register, Login, Logout, Profile)
# ==============================================================================

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validations
        if not name or not email or not phone or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('An account with this email address already exists.', 'warning')
            return render_template('register.html')

        new_user = User(name=name, email=email, phone=phone, is_admin=False)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()

        # Log in the new user immediately
        session['user_id'] = new_user.id
        session['user_name'] = new_user.name
        session['user_email'] = new_user.email
        session['is_admin'] = new_user.is_admin

        flash(f'Welcome to Grand Royale, {new_user.name}! Your account has been created successfully.', 'success')
        return redirect(url_for('main.index'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember')

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash('Invalid email or password. Please try again.', 'danger')
            return render_template('login.html')

        # Set session
        session['user_id'] = user.id
        session['user_name'] = user.name
        session['user_email'] = user.email
        session['is_admin'] = user.is_admin
        if remember:
            session.permanent = True

        flash(f'Welcome back, {user.name}!', 'success')
        
        next_page = request.args.get('next')
        if user.is_admin:
            return redirect(next_page or url_for('admin.dashboard'))
        return redirect(next_page or url_for('main.index'))

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_info':
            name = request.form.get('name', '').strip()
            phone = request.form.get('phone', '').strip()
            if name and phone:
                user.name = name
                user.phone = phone
                db.session.commit()
                session['user_name'] = user.name
                flash('Profile details updated successfully.', 'success')
            else:
                flash('Name and Phone are required.', 'danger')
                
        elif action == 'change_password':
            current_pass = request.form.get('current_password', '')
            new_pass = request.form.get('new_password', '')
            confirm_pass = request.form.get('confirm_password', '')
            
            if not user.check_password(current_pass):
                flash('Current password is incorrect.', 'danger')
            elif new_pass != confirm_pass:
                flash('New passwords do not match.', 'danger')
            elif len(new_pass) < 6:
                flash('New password must be at least 6 characters.', 'danger')
            else:
                user.set_password(new_pass)
                db.session.commit()
                flash('Password changed successfully.', 'success')

        return redirect(url_for('auth.profile'))

    return render_template('profile.html', user=user)


# ==============================================================================
# BOOKING & PAYMENT BLUEPRINT
# ==============================================================================

@booking_bp.route('/book/initiate/<int:room_id>', methods=['POST'])
@login_required
def initiate_booking(room_id):
    room = Room.query.get_or_404(room_id)
    
    check_in_str = request.form.get('check_in')
    check_out_str = request.form.get('check_out')
    guests = request.form.get('guests', type=int, default=1)

    if not check_in_str or not check_out_str:
        flash('Check-in and Check-out dates are required.', 'danger')
        return redirect(url_for('main.room_details', room_id=room.id))

    try:
        check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
        check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format selected.', 'danger')
        return redirect(url_for('main.room_details', room_id=room.id))

    today = date.today()
    if check_in < today:
        flash('Check-in date cannot be in the past.', 'danger')
        return redirect(url_for('main.room_details', room_id=room.id))

    if check_out <= check_in:
        flash('Check-out date must be after Check-in date.', 'danger')
        return redirect(url_for('main.room_details', room_id=room.id))

    if guests > room.capacity:
        flash(f'Guest count exceeds room capacity of {room.capacity}.', 'danger')
        return redirect(url_for('main.room_details', room_id=room.id))

    # Check availability
    if not is_room_available(room.id, check_in, check_out):
        flash('Sorry, this room is already booked for the selected dates. Please choose different dates.', 'danger')
        return redirect(url_for('main.room_details', room_id=room.id))

    # Calculate total nights and total price
    nights = (check_out - check_in).days
    total_price = room.price * nights

    # Create Booking in Pending state
    b_id = generate_booking_id()
    booking = Booking(
        booking_id=b_id,
        user_id=session['user_id'],
        room_id=room.id,
        check_in=check_in,
        check_out=check_out,
        guests=guests,
        total_price=total_price,
        booking_status='Pending',
        payment_status='Unpaid'
    )

    db.session.add(booking)
    db.session.commit()

    return redirect(url_for('booking.booking_summary', booking_id=booking.booking_id))


@booking_bp.route('/booking/summary/<booking_id>')
@login_required
def booking_summary(booking_id):
    booking = Booking.query.filter_by(booking_id=booking_id, user_id=session['user_id']).first_or_404()
    return render_template('booking.html', booking=booking)


@booking_bp.route('/payment/<booking_id>')
@login_required
def payment_page(booking_id):
    booking = Booking.query.filter_by(booking_id=booking_id, user_id=session['user_id']).first_or_404()
    if booking.payment_status == 'Paid':
        flash('This booking is already paid.', 'info')
        return redirect(url_for('booking.dashboard'))
    return render_template('payment.html', booking=booking)


@booking_bp.route('/payment/process/<booking_id>', methods=['POST'])
@login_required
def process_payment(booking_id):
    booking = Booking.query.filter_by(booking_id=booking_id, user_id=session['user_id']).first_or_404()
    
    payment_method = request.form.get('payment_method', 'Credit Card')
    status_choice = request.form.get('status_choice', 'success')  # Demo status toggle

    if status_choice == 'failed':
        flash('Payment transaction failed or was declined by bank. Please try again.', 'danger')
        return redirect(url_for('booking.payment_page', booking_id=booking.booking_id))

    # Payment Success flow
    txn_id = generate_transaction_id()
    payment = Payment(
        booking_id=booking.id,
        amount=booking.total_price,
        payment_method=payment_method,
        status='Success',
        transaction_id=txn_id
    )

    booking.booking_status = 'Confirmed'
    booking.payment_status = 'Paid'

    db.session.add(payment)
    db.session.commit()

    flash('Payment successful! Your reservation is confirmed.', 'success')
    return render_template('payment.html', booking=booking, payment_success=True, payment=payment)


@booking_bp.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    user = User.query.get_or_404(user_id)
    bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.created_at.desc()).all()
    
    # Calculate stats
    total_spent = sum(b.total_price for b in bookings if b.payment_status == 'Paid')
    active_count = sum(1 for b in bookings if b.booking_status in ['Confirmed', 'Pending'])
    
    return render_template('dashboard.html', user=user, bookings=bookings, total_spent=total_spent, active_count=active_count)


@booking_bp.route('/booking/cancel/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.filter_by(id=booking_id, user_id=session['user_id']).first_or_404()
    
    if booking.booking_status == 'Cancelled':
        flash('Booking is already cancelled.', 'warning')
    else:
        booking.booking_status = 'Cancelled'
        if booking.payment_status == 'Paid':
            booking.payment_status = 'Refunded'
            if booking.payment:
                booking.payment.status = 'Refunded'
        db.session.commit()
        flash(f'Booking {booking.booking_id} has been cancelled.', 'success')

    return redirect(url_for('booking.dashboard'))


@booking_bp.route('/invoice/<booking_id>')
@login_required
def view_invoice(booking_id):
    # Admin can view any invoice, regular user can only view their own
    booking = Booking.query.filter_by(booking_id=booking_id).first_or_404()
    if not session.get('is_admin') and booking.user_id != session.get('user_id'):
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
        
    return render_template('invoice_template.html', booking=booking)


# ==============================================================================
# ADMIN BLUEPRINT (Admin Panel, Manage Rooms, Bookings, Users)
# ==============================================================================

@admin_bp.route('')
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    total_users = User.query.count()
    total_rooms = Room.query.count()
    
    # Today's bookings
    today_start = datetime.combine(date.today(), datetime.min.time())
    todays_bookings = Booking.query.filter(Booking.created_at >= today_start).count()
    
    # Revenue
    revenue = db.session.query(db.func.sum(Payment.amount)).filter(Payment.status == 'Success').scalar() or 0.0

    rooms = Room.query.order_by(Room.id.desc()).all()
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    users = User.query.order_by(User.id.desc()).all()

    return render_template('admin.html',
                           total_users=total_users,
                           total_rooms=total_rooms,
                           todays_bookings=todays_bookings,
                           revenue=revenue,
                           rooms=rooms,
                           bookings=bookings,
                           users=users)


@admin_bp.route('/rooms/add', methods=['POST'])
@admin_required
def add_room():
    room_name = request.form.get('room_name', '').strip()
    room_number = request.form.get('room_number', '').strip()
    room_type = request.form.get('type', 'Standard')
    capacity = request.form.get('capacity', type=int, default=2)
    price = request.form.get('price', type=float, default=200.0)
    description = request.form.get('description', '').strip()
    
    wifi = 'wifi' in request.form
    ac = 'ac' in request.form
    breakfast = 'breakfast' in request.form
    tv = 'tv' in request.form
    status = request.form.get('status', 'Available')

    # Handle Primary Image Upload
    file = request.files.get('image')
    image_path = '/static/images/room_classic.jpg'  # Default fallback
    
    if file and file.filename:
        filename = secure_filename(file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        saved_name = f"room_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
        file.save(os.path.join(upload_folder, saved_name))
        image_path = f"/static/uploads/{saved_name}"

    new_room = Room(
        room_name=room_name,
        room_number=room_number,
        type=room_type,
        capacity=capacity,
        price=price,
        description=description,
        wifi=wifi,
        ac=ac,
        breakfast=breakfast,
        tv=tv,
        image=image_path,
        status=status,
        rating=4.9
    )

    db.session.add(new_room)
    db.session.commit()

    # Handle multiple additional images
    additional_files = request.files.getlist('additional_images')
    for add_file in additional_files:
        if add_file and add_file.filename:
            add_fn = secure_filename(add_file.filename)
            add_saved = f"add_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{add_fn}"
            add_file.save(os.path.join(upload_folder, add_saved))
            db.session.add(RoomImage(room_id=new_room.id, image_url=f"/static/uploads/{add_saved}"))
    
    db.session.commit()

    flash(f'Room "{room_name}" (#{room_number}) created successfully.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/rooms/edit/<int:room_id>', methods=['POST'])
@admin_required
def edit_room(room_id):
    room = Room.query.get_or_404(room_id)
    
    room.room_name = request.form.get('room_name', room.room_name).strip()
    room.room_number = request.form.get('room_number', room.room_number).strip()
    room.type = request.form.get('type', room.type)
    room.capacity = request.form.get('capacity', type=int, default=room.capacity)
    room.price = request.form.get('price', type=float, default=room.price)
    room.description = request.form.get('description', room.description).strip()
    room.wifi = 'wifi' in request.form
    room.ac = 'ac' in request.form
    room.breakfast = 'breakfast' in request.form
    room.tv = 'tv' in request.form
    room.status = request.form.get('status', room.status)

    file = request.files.get('image')
    if file and file.filename:
        filename = secure_filename(file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        saved_name = f"room_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
        file.save(os.path.join(upload_folder, saved_name))
        room.image = f"/static/uploads/{saved_name}"

    db.session.commit()
    flash(f'Room "{room.room_name}" updated successfully.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/rooms/delete/<int:room_id>', methods=['POST'])
@admin_required
def delete_room(room_id):
    room = Room.query.get_or_404(room_id)
    db.session.delete(room)
    db.session.commit()
    flash(f'Room #{room.room_number} deleted successfully.', 'info')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/bookings/status/<int:booking_id>', methods=['POST'])
@admin_required
def update_booking_status(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    new_status = request.form.get('status')
    
    if new_status in ['Pending', 'Confirmed', 'Cancelled', 'Completed']:
        booking.booking_status = new_status
        if new_status == 'Confirmed' and booking.payment_status == 'Unpaid':
            booking.payment_status = 'Paid'
        db.session.commit()
        flash(f'Booking {booking.booking_id} status updated to {new_status}.', 'success')

    return redirect(url_for('admin.dashboard'))


# ==============================================================================
# API BLUEPRINT (Dynamic JS Calculations, Availability Check & Reviews)
# ==============================================================================

@api_bp.route('/check-availability', methods=['POST'])
def api_check_availability():
    data = request.get_json() or {}
    room_id = data.get('room_id')
    check_in_str = data.get('check_in')
    check_out_str = data.get('check_out')

    if not room_id or not check_in_str or not check_out_str:
        return jsonify({'success': False, 'message': 'Missing parameters'}), 400

    try:
        check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
        check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid date format'}), 400

    room = Room.query.get(room_id)
    if not room:
        return jsonify({'success': False, 'message': 'Room not found'}), 404

    nights = (check_out - check_in).days
    if nights <= 0:
        return jsonify({'success': False, 'message': 'Check-out date must be after Check-in date.'})

    available = is_room_available(room_id, check_in, check_out)
    total_price = room.price * nights

    return jsonify({
        'success': True,
        'available': available,
        'nights': nights,
        'price_per_night': room.price,
        'total_price': total_price
    })


@api_bp.route('/reviews/add', methods=['POST'])
@login_required
def api_add_review():
    room_id = request.form.get('room_id', type=int)
    rating = request.form.get('rating', type=int, default=5)
    comment = request.form.get('comment', '').strip()

    if not room_id or not comment:
        flash('Comment cannot be empty.', 'danger')
        return redirect(url_for('main.room_details', room_id=room_id))

    new_review = Review(
        user_id=session['user_id'],
        room_id=room_id,
        rating=rating,
        comment=comment
    )
    db.session.add(new_review)
    db.session.commit()

    # Recalculate room average rating
    all_reviews = Review.query.filter_by(room_id=room_id).all()
    avg_rating = round(sum(r.rating for r in all_reviews) / len(all_reviews), 1)
    room = Room.query.get(room_id)
    if room:
        room.rating = avg_rating
        db.session.commit()

    flash('Thank you! Your review has been submitted.', 'success')
    return redirect(url_for('main.room_details', room_id=room_id))
