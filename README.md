# AI Based Child Monitoring System

A comprehensive web-based platform designed to connect parents and daycares, facilitating child monitoring, activity tracking, and developmental milestone management.

## Features

*   **Role-Based Access Control**: specialized dashboards for Admins, Daycares, and Parents.
*   **Daycare Management**: Profile management, child enrollment handling, and activity reporting.
*   **Parent Portal**: view child's daily activities, track milestones, and communicate with daycares.
*   **Child Activity Tracking**: Daily reports with descriptions and images.
*   **Milestone Tracking**: Monitor developmental milestones (Motor Skills, Language, Social, Cognitive) with status updates.
*   **AI Suggestions**: Personalized parenting insights and activity suggestions powered by Google Gemini.
*   **Chat System**: Built-in messaging between parents and daycares.
*   **Rating System**: Parents can rate and review daycares.
*   **Notifications**: Real-time alerts for messages and milestone updates.

## Project Structure

```text
Ai_Based_Child_Monitoring_System/
├── child_monitoring/       # Project configuration
│   ├── settings.py         # Django settings
│   ├── urls.py             # Root URL configuration
│   └── ...
├── core/                   # Main application app
│   ├── migrations/         # Database migrations
│   ├── templates/          # HTML templates
│   │   ├── admin_dashboard.html
│   │   ├── daycare_dashboard.html
│   │   ├── parent_dashboard.html
│   │   ├── my_child.html
│   │   └── ...
│   ├── models.py           # Database models (Child, Parent, Daycare, Milestone, etc.)
│   ├── views.py            # Application logic and view functions
│   ├── urls.py             # App-specific URL routing
│   └── utils.py            # Utility functions (AI integration, age calculation)
├── media/                  # User-uploaded content (images, documents)
├── templates/              # Base templates (layout.html)
├── manage.py               # Django command-line utility
├── requirements.txt        # Project dependencies
└── README.md               # Project documentation
```

## Installation and Setup

Follow these steps to set up the project locally.

### Prerequisites

*   Python 3.8 or higher
*   Git

### 1. Clone the Repository

```bash
git clone https://github.com/pankaj8128/Ai_Based_Child_Monitoring_System.git
cd Ai_Based_Child_Monitoring_System
```

### 2. Create and Activate a Virtual Environment

It is recommended to use a virtual environment to manage dependencies.

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

Install the required Python packages listed in `requirements.txt`.

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the root directory and add your Google Gemini API key:

```text
GEMINI_API_KEY=your_api_key_here
```

### 5. Database Setup

Apply database migrations to set up the schema and insert default data (including milestones).

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a Superuser (Admin)

Create an admin account to manage the system.

```bash
python manage.py createsuperuser
```

### 7. Run the Development Server

Start the Django development server.

```bash
python manage.py runserver
```

Open your browser and navigate to `http://127.0.0.1:8000/` to access the application.

## Usage Guide

*   **Registration**: Users can register as a Parent or Daycare.
*   **Admin**: Log in with the superuser account to verify daycares and manage users.
*   **Daycare**: Complete your profile, verify your account, enroll children, and post daily activity reports.
*   **Parent**: Complete your profile, enroll your child in a daycare, view reports, and track milestones.

## Technologies Used

*   **Backend**: Django, Python
*   **Frontend**: HTML, CSS, JavaScript (Bootstrap/Vanilla)
*   **Database**: SQLite (default)
*   **AI Integration**: Google Generative AI (Gemini)
*   **Image Processing**: Pillow
