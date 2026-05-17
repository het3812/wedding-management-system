# Wedding Management System

A full-featured wedding management web application with **Admin**, **Host**, and **Vendor** roles. Built with Flask, MySQL, and Bootstrap.

## Features

### Admin (System Administrator)
- **Dashboard**: View all invitations from all hosts, vendor & host counts
- **Host Activity**: See all hosts with invitation/guest/event counts; drill into any host to see their full activity (invitations, guests, events)
- **Vendor Activity**: See all vendors and **View All Vendor Services** — one list of every service from every vendor
- **Host Management**: Create host accounts for wedding couples
- **Vendor Management**: View all vendors, approve/disable, view each vendor’s services
- **Full Invitation Access**: Edit, manage guests, events, upload images for any invitation

### Host (Wedding Couple / Event Host)
- **Self-registration**: Create your own account at `/host/register` — no approval needed; start creating invitations right after login.
- **Own Dashboard**: Manage only your invitations
- **Guest Management**: Add/edit/delete guests, categories (Family/Friend/VIP), RSVP status
- **Wedding Event Schedule**: Add events (Haldi, Mehndi, Wedding, Reception) with date, time, venue
- **Invitations & Gallery**: Create invitations, upload images (album-wise), share links

### Vendor
- **Separate Login**: `/vendor/login` – vendors have their own login page
- **Registration**: Name, service type, contact (admin approves before visibility)
- **Service Upload**: Title, description, price, image for each service
- **Dashboard**: View and manage own services (edit/delete)

### Guest (No Login)
- **Invitation View**: Token-based public link with bride/groom, date, venue, event schedule
- **Photo Gallery**: Album-wise view, access only via invitation link

## Tech Stack

- **Frontend**: HTML, CSS, Bootstrap 5
- **Backend**: Python Flask
- **Database**: MySQL (XAMPP)
- **Storage**: Local files in `static/uploads/`

---

## Setup (XAMPP)

### 1. Prerequisites

- Python 3.8+
- XAMPP (Apache + MySQL)
- Git (optional)

### 2. Start XAMPP

1. Open XAMPP Control Panel
2. Start **Apache** and **MySQL**

### 3. Create Database

**Fresh install:**
1. Open `http://localhost/phpmyadmin`
2. Create database `wedding_db`
3. Select it, go to SQL tab, run `database.sql`

**Existing DB (had previous version):**
1. Run `database_migration.sql` in phpMyAdmin to add new tables (guests, events, vendors, vendor_services)

### 4. Configure Environment

Edit `config.py` if your MySQL settings differ:

- **DB_HOST**: `localhost` (default)
- **DB_USER**: `root` (default for XAMPP)
- **DB_PASSWORD**: `` (empty for XAMPP default)
- **DB_NAME**: `wedding_db`

Or set environment variables:

```bash
set DB_PASSWORD=your_password   # Windows
export DB_PASSWORD=your_password  # Linux/Mac
```

### 5. Install Dependencies

```bash
cd wedding_management_system
pip install -r requirements.txt
```

### 6. Initialize Users

```bash
 
```

This creates the default users:
- **Admin**: admin@wedding.com / admin123
- **Host**: host@wedding.com / host123

**Change these passwords after first login!**

**Account model:** There is only **one Admin** (or a few, created manually). You can create **many Hosts** and **many Vendors** as below.

### 7. Run the Application

```bash
python app.py
```

Open: **http://127.0.0.1:5000**

---

## Creating More Host and Vendor Accounts

### Host accounts (many allowed)
- **Self-registration:** Hosts can create their own account with no approval needed. On the home page click **Host Login**, then **Create your account**, or go to `/host/register`. Enter name, email, and password — then login and start creating invitations.
- **Admin can also add hosts:** Log in as Admin → **Hosts** → **+ Add Host** (e.g. to create an account on behalf of someone).

### Vendor accounts (many allowed)
- **Who creates them:** Vendors **self-register** (no admin needed to create the account).
- **How:** On the home page, click **Vendor Login**, then **Register here** (or go to `/vendor/register`).
- Fill in name, email, password, business name, service type, contact. After registration, **Admin** must approve the vendor in **Vendors** before they are fully active.

### Admin (only one by default)
- The single admin is created by `python init_db.py`. To add more admins you would need to insert a user with `role = 'admin'` in the database (e.g. via phpMyAdmin) or add an “Add Admin” feature restricted to existing admins.

---

## Application Flow

### Admin Flow

1. Login at `/login`
2. **Dashboard** (`/admin/`): View all invitations, create new ones
3. **Create Invitation**: Enter bride/groom names, date, venue, message
4. **Share Link**: Copy the generated `/invite/<token>` URL (e.g. share on WhatsApp)
5. **Upload Images**: Add wedding photos for each invitation
6. **Control Access**: Toggle invitation active/inactive in Edit

### Guest Flow

1. Receive invitation link (e.g. `http://localhost:5000/invite/abc123...`)
2. Open link → View wedding invitation
3. Click **View Photo Gallery** → Access private gallery (token stored in session)

### Security

- Guests **must** open the invitation link first to access the gallery
- Direct `/gallery/<token>` access works only if:
  - User is logged-in admin, OR
  - User has the token in session (visited invitation page)
- Invalid/expired tokens show friendly error pages

---

## Project Structure

```
wedding_app/
├── app.py                 # Main Flask app
├── config.py              # Configuration (DB, uploads, secret)
├── db.py                  # Database connection helper
├── init_db.py             # Create tables & default admin
├── database.sql           # MySQL schema
├── requirements.txt
├── blueprints/
│   ├── auth.py            # Login, logout
│   ├── admin.py           # Dashboard, invitations, uploads
│   ├── invitation.py      # Public /invite/<token>
│   └── gallery.py         # /gallery/<token>
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── admin_dashboard.html
│   ├── admin_invitation_form.html
│   ├── admin_upload.html
│   ├── invitation.html
│   ├── invitation_error.html
│   ├── gallery.html
│   └── gallery_error.html
└── static/
    ├── css/
    └── uploads/           # Wedding images stored here
```

---

## Routes Summary

| Route | Access | Description |
|-------|--------|-------------|
| `/` | Public | Home – Admin, Host, or Vendor login choice |
| `/login` | Public | Admin login |
| `/host/login` | Public | Host login |
| `/host/register` | Public | Host self-registration |
| `/vendor/login` | Public | Vendor login |
| `/vendor/register` | Public | Vendor registration |
| `/vendor/` | Vendor | Vendor dashboard |
| `/admin/` | Admin | Admin dashboard (all invitations) |
| `/admin/hosts` | Admin | Host activity & management (counts + View Activity per host) |
| `/admin/hosts/<id>/activity` | Admin | One host’s full activity (invitations, guests, events) |
| `/host/` | Host | Host dashboard (own invitations) |
| `/admin/invitation/<id>/guests` | Admin | Guest management |
| `/admin/invitation/<id>/events` | Admin | Event schedule |
| `/admin/vendors` | Admin | Vendor management |
| `/admin/vendors/all-services` | Admin | All vendor services (one list) |
| `/invite/<token>` | Public | View invitation (events, gallery link) |
| `/gallery/<token>` | Admin or Guest | Album-wise gallery |

---

## Troubleshooting

**Database connection failed**
- Ensure MySQL is running in XAMPP
- Verify `wedding_db` exists
- Check `config.py` credentials

**Module not found**
- Run `pip install -r requirements.txt`

**Upload fails**
- Ensure `static/uploads/` folder exists and is writable
- Check file size (max 16MB) and type (png, jpg, jpeg, gif, webp)

---

## Academic Use

This project is suitable for final-year or internship projects. Key concepts demonstrated:

- Flask Blueprints
- Session-based authentication
- Role-based access control
- Secure token generation
- File upload validation
- MySQL CRUD operations
- Responsive Bootstrap UI

---

## License

Academic / educational use.
