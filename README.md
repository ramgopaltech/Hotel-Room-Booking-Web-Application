# Grand Royale - Production-Ready Luxury Hotel Booking Web Application

Grand Royale is a full-stack, production-ready Hotel Room Booking Web Application built with **Python Flask**, **SQLite**, **SQLAlchemy ORM**, and a custom **Glassmorphism + Dark Gold Luxury Theme** (HTML5, Vanilla CSS3, JavaScript).

---

## 🌟 Key Features

### 🔐 Complete Authentication & Authorization
- User Registration, Login, Logout, Remember Me session management.
- Werkzeug security password hashing.
- Role-based Access Control (Customer vs Administrator).
- Profile management and password updates.

### 🏨 Room Listing & Filtering
- Dynamic room search by keywords.
- Filters by Price Range, Capacity, Room Type, and Amenities (WiFi, AC, Breakfast, TV).
- Real-time sorting (Price Low to High, High to Low, Guest Ratings).

### 📅 Smart Booking & Overlap Prevention
- Real-time check-in and check-out date night calculator via Vanilla JavaScript.
- Automatic price calculation.
- Date collision verification ensuring rooms cannot be double-booked for overlapping periods.
- Booking status workflow (`Pending` -> `Confirmed` -> `Cancelled` / `Completed`).

### 💳 Demo Payment Gateway & PDF/HTML Invoices
- Demo Payment portal supporting Credit Card, UPI / QR Code, and PayPal simulation.
- Payment status update (`Paid`, `Unpaid`, `Refunded`).
- Printable & downloadable luxury invoice view.

### 🛡️ Comprehensive Admin Panel
- **Overview Metrics**: Total Users, Total Rooms, Today's Bookings, Total Revenue counters.
- **Room Management (CRUD)**: Add Room with image upload, edit room details, delete room.
- **Booking Management**: Approve or Reject customer bookings, filter by reference ID.
- **Guest Directory**: Overview of registered user details and roles.

### 🎨 Premium Aesthetics
- Custom Glassmorphism UI with dark obsidian background and warm gold accents (`#d4af37`).
- Smooth scrolling, hover micro-animations, loading spinners, and toast notifications.
- Fully responsive on desktop, tablet, and mobile screens.

---

## 📁 Project Structure

```text
HotelBooking/
│
├── app.py                   # Flask Application Factory & Error Handlers
├── config.py                # Database URI & Secret Key Config
├── requirements.txt         # Dependencies
├── database.db              # SQLite Database (Auto-created on launch)
├── models.py                # SQLAlchemy ORM Models (User, Room, Booking, Payment, Review)
├── routes.py                # Blueprints (Main, Auth, Booking, Admin, API)
├── utils.py                 # Security Decorators, Availability Checker, Data Seeder
├── generate_images.py       # Seed image generator utility
│
├── static/
│   ├── css/
│   │   ├── style.css        # Main Theme, Glassmorphism, Layout
│   │   ├── admin.css        # Admin Metrics, Tables, Badges, Modals
│   │   └── auth.css         # Glass Login/Register Card Styles
│   ├── js/
│   │   ├── main.js          # Sticky Header, Mobile Navigation, Toasts
│   │   ├── booking.js       # Live Price Calculator & Gallery Lightbox
│   │   └── admin.js         # Tab Switcher & Table Search Filter
│   ├── images/              # Room & Background Seed Images
│   └── uploads/             # User & Admin Uploaded Room Images
│
└── templates/
    ├── base.html            # Master Layout Template
    ├── index.html           # Luxury Hero, Facilities, Reviews & Featured Rooms
    ├── rooms.html           # Filterable Room Listing Page
    ├── room_details.html    # Room Overview, Amenities, Live Date Picker
    ├── booking.html         # Booking Summary & Confirmation Screen
    ├── payment.html         # Demo Payment Portal
    ├── login.html           # Guest Login Screen
    ├── register.html        # Guest Account Registration
    ├── dashboard.html       # Guest Profile & Booking History
    ├── admin.html           # Admin Dashboard & Room/Booking Management
    ├── profile.html         # Profile Settings
    ├── contact.html         # Concierge Contact & Location Map
    ├── invoice_template.html# Printable Bill / Invoice Format
    ├── 404.html             # Custom Not Found Error Page
    └── 500.html             # Custom Server Error Page
```

---

## 🔑 Default Credentials

The app automatically seeds initial data and accounts on first launch:

| Account Type | Email | Password | Role |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@hotel.com` | `admin123` | Full Admin Access |
| **Sample Guest** | `john@example.com` | `user123` | Customer Access |

---

## 🚀 Quick Start Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate Luxury Seed Images (Optional / Pre-packaged)
```bash
python generate_images.py
```

### 3. Run Application
```bash
python app.py
```

Open your browser and navigate to: **`http://127.0.0.1:5000`**
