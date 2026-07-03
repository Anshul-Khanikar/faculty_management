# Faculty Management System

A simple, modern, and responsive web application built with Python (Flask) and SQLite to manage college faculty directories and details.

## Features

- **Admin Dashboard**:
  - Secure authentication (Admin login credentials).
  - Complete CRUD operations (Create, Read, Update, Delete) on faculty records.
  - Interactive details editing via modal dialogs.
  - Quick update of Admin login credentials.
- **Teacher View**:
  - Personalized login using system-assigned ID and passcode.
  - Secure, read-only profile access displaying personal details (salary, Aadhaar, PAN card, assignment status).
- **Responsive Layout**: Designed with a clean dark theme styled using modern CSS Grid and Flexbox layouts.

## Tech Stack

- **Backend**: Python 3, Flask framework
- **Database**: SQLite3 (embedded file-based relational database)
- **Frontend**: Vanilla HTML5, CSS3, and JavaScript
- **Styling**: Vanilla CSS (Variables, Flexbox, CSS Grid) with a dark theme

## Getting Started

### Prerequisites

Make sure you have Python 3 installed. Install Flask:

```bash
pip install flask
```

### Running the Application

1. Clone or download the repository.
2. Navigate to the project root directory.
3. Run the application:

```bash
python app.py
```

4. Open your browser and go to `http://127.0.0.1:5000`.

### Default Credentials

- **Admin Login**:
  - Username: `admin`
  - Password: `admin123`
- **Teacher Login**:
  - ID: The database auto-incremented ID (e.g. `1`, `2`, `3`)
  - Password: Set by Admin during registration
