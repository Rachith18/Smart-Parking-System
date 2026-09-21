# 🚗 Smart Parking System

A web-based **Smart Parking System** developed with **Python Flask** and **Oracle Database XE 11g**. The application provides a simple interface for managing parking slots, reserving and releasing vehicles, viewing parking history, and searching vehicle records.

## ✨ Features

- 🔐 User login and session management
- 🅿️ Real-time parking slot status
- 🚗 Vehicle reservation with vehicle number
- 🔓 Release occupied parking slots
- 📋 Parking history with entry and exit time
- 🔎 Search parking records by vehicle number
- 📊 Dashboard showing total, available and occupied slots
- 👨‍💼 Admin page for adding and deleting available slots
- 🗄️ Oracle XE 11g database integration
- 🛡️ Environment variables for database credentials

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, Jinja2 |
| Backend | Python, Flask |
| Database | Oracle Database XE 11g |
| Database Driver | python-oracledb |
| Development | VS Code / PyCharm / Command Prompt |

## 📁 Project Structure

```text
Smart-Parking-System/
├── app.py
├── database.py
├── test_connection.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── database/
│   └── oracle_schema.sql
└── templates/
    ├── admin.html
    ├── dashboard.html
    ├── history.html
    ├── index.html
    ├── login.html
    └── search.html
```

## 🔄 Application Flow

```text
User Login
    ↓
Dashboard
    ↓
View Parking Slots
    ↓
Reserve Slot ──→ parking_slots
    ↓                    ↓
parking_history ← Entry Time
    ↓
Release Slot
    ↓
Exit Time + COMPLETED
    ↓
History / Vehicle Search
```

## 🗄️ Oracle Database Tables

The application uses these main tables:

- `PARKING_USERS` – login credentials and user roles
- `PARKING_SLOTS` – slot number, status and current vehicle
- `PARKING_HISTORY` – vehicle entry/exit history
- `PARKING_HISTORY_SEQ` – sequence used for history IDs

See [`database/oracle_schema.sql`](database/oracle_schema.sql) for the Oracle SQL setup.

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/Rachith18/Smart-Parking-System.git
cd Smart-Parking-System
```

### 2. Create a virtual environment

```bash
python -m venv venv
venv\\Scripts\\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Oracle

Copy `.env.example` to `.env` and enter your Oracle password and Oracle Client path.

```text
DB_USER=system
DB_PASSWORD=YOUR_ORACLE_PASSWORD
DB_DSN=localhost:1521/XE
ORACLE_CLIENT_LIB_DIR=C:\\oraclexe\\app\\oracle\\product\\11.2.0\\server\\bin
SECRET_KEY=your-secret-key
```

**Never commit `.env` to GitHub.** It is ignored by `.gitignore`.

### 5. Create the Oracle database objects

Open Oracle SQL*Plus or SQL Developer and run:

```text
database/oracle_schema.sql
```

### 6. Test the database connection

```bash
python test_connection.py
```

Expected result:

```text
Oracle Database connected successfully!
```

### 7. Start Flask

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## 🔑 Demo Login

Create your own user in Oracle using the SQL script. For the current application, the `PARKING_USERS.PASSWORD` value is checked directly by the login query.

For a portfolio/demo database, use a test account rather than a real password.

## 📸 Screenshots

Add project screenshots to a `screenshots/` folder and update this section with images of:

1. Login page
2. Dashboard
3. Parking slots
4. Reserve/release operation
5. Parking history
6. Vehicle search
7. Oracle database tables

## 🎯 Project Objective

The objective of the project is to provide a simple digital parking management system that reduces manual slot tracking and maintains vehicle parking records in an Oracle database.

## 🚀 Future Enhancements

- Online payment integration
- QR-code based vehicle entry
- Automatic number-plate recognition
- Parking duration and fee calculation
- Email/SMS notifications
- Role-based permissions with stronger password hashing
- Cloud database deployment

## 👨‍💻 Author

**Rachith B**  
BCA Student | Python | SQL | Flask | Oracle Database

GitHub: `https://github.com/Rachith18`
