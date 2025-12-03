# Fitness Class Booking System

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation & Setup](#installation--setup)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Demo Instructions](#demo-instructions)
- [LLM Integration](#llm-integration)

## Overview

A comprehensive fitness class booking system with instructor assignments, user profiles, booking management, and AI-powered workout generation. This Django REST Framework application provides a complete solution for fitness studios to manage classes, instructors, and member bookings with email confirmations.

## Features

### Core Features
- **Class Management**: CRUD operations for fitness classes with instructor assignments
- **Instructor Management**: Detailed instructor profiles with specializations
- **User Management**: Role-based users (members, instructors, admins)
- **Booking System**: Class bookings with email confirmation and cancellation
- **Fitness Profiles**: Detailed user fitness metrics and goals tracking

### Advanced Features
- **LLM-Powered Workouts**: AI-generated personalized workout plans
- **Fake Data Generation**: Comprehensive demo data for testing
- **RESTful API**: Full-featured API with browsable interface
- **Admin Dashboard**: Django admin for system management

## Technology Stack

- **Backend**: Django 4.2, Django REST Framework
- **Database**: PostgreSQL/SQLite
- **Authentication**: JWT & Session-based
- **LLM Integration**: OpenAI GPT (or mock service for demo)
- **Tools**: Poetry for dependency management

## Installation & Setup

### Prerequisites
- Python 3.9+
- Poetry
- PostgreSQL

### Step-by-Step Installation

1. **Clone the repository**
```bash
git clone https://github.com/Da1nji/FitnessClassBookingSystem
cd fitness-booking-system
```

2. **Install dependencies with Poetry**
```bash
poetry install
```

3. **Activate virtual environment**
```bash
poetry shell
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Run migrations**
```bash
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Run development server**
```bash
python manage.py runserver
```

Access the application at `http://localhost:8000`

## 📁 Project Structure

```
fitness_booking_system/
├── users/                    # User management app
│   ├── models.py            # Custom User & FitnessProfile models
│   ├── serializers.py       # User serializers
│   ├── views.py             # User views & profile management
│   ├── services.py          # LLM workout generation service
│   └── management/commands/ # Management commands
├── instructors/             # Instructor management
│   ├── models.py           # Instructor model
│   ├── serializers.py      # Instructor serializers
│   └── views.py            # Instructor views
├── classes/                 # Core booking system
│   ├── models.py           # ClassType, Level, FitnessClass, Booking
│   ├── serializers.py      # All class-related serializers
│   ├── views.py            # Class & booking views
│   ├── services.py         # Email services
│   └── templates/emails/   # Email templates
├── fitness_booking_system/  # Project settings
│   ├── settings.py         # Django settings
│   ├── urls.py            # URL configuration
│   └── wsgi.py            # WSGI configuration
└── templates/              # HTML templates
```

## 📚 API Documentation

### Authentication Endpoints
```
POST    /api/users/login/            # User login
POST    /api/users/register/         # User registration
GET     /api/users/me/              # Current user info
GET     /api/users/me_with_profile/ # User with fitness profile
```

### Class Management
```
GET     /api/classes/class-types/    # List class types
GET     /api/classes/levels/         # List difficulty levels
GET     /api/classes/classes/        # List all classes
POST    /api/classes/classes/        # Create class
GET     /api/classes/classes/{id}/   # Class details
PUT     /api/classes/classes/{id}/   # Update class
DELETE  /api/classes/classes/{id}/   # Delete class
POST    /api/classes/classes/{id}/assign_instructor/  # Assign instructor
POST    /api/classes/classes/{id}/cancel/            # Cancel class
```

### Booking System
```
GET     /api/classes/bookings/       # List user bookings
POST    /api/classes/bookings/       # Create booking
GET     /api/classes/bookings/{id}/  # Booking details
POST    /api/classes/bookings/{id}/confirm/  # Confirm booking (email)
POST    /api/classes/bookings/{id}/cancel/   # Cancel booking
GET     /api/classes/bookings/upcoming/      # Upcoming bookings
GET     /api/classes/bookings/history/       # Past bookings
```

### Fitness Profiles
```
GET     /api/users/profiles/mine/           # Get my profile
PUT     /api/users/profiles/mine/           # Update profile
POST    /api/users/profiles/update_bmi/     # Update height/weight
POST    /api/users/profiles/update_goals/   # Update fitness goals
POST    /api/users/profiles/add_workout_history/  # Log workout
GET     /api/users/profiles/llm_context/    # Get LLM prompt context
POST    /api/users/profiles/generate_workout_plan/ # Generate AI workout
GET     /api/users/profiles/workout_history/ # View workout history
GET     /api/users/profiles/recommendations/ # Get recommendations
```

### Instructor Management
```
GET     /api/instructors/            # List instructors
POST    /api/instructors/            # Create instructor
GET     /api/instructors/{id}/       # Instructor details
PUT     /api/instructors/{id}/       # Update instructor
DELETE  /api/instructors/{id}/       # Delete instructor
GET     /api/instructors/specializations/ # List specializations
```

## 🎪 DEMO Instructions

### Complete Demo Flow

#### Step 1: Setup Demo Data
```bash
# Generate comprehensive demo data
poetry run python manage.py create_fake_data \
  --users 30 \
  --instructors 8 \
  --classes 50

# Default password for all demo users: "password123"
```

#### Step 2: Access Admin Interface
1. Go to `http://localhost:8000/admin/`
2. Login with superuser credentials
3. Explore: Users, Instructors, Classes, Bookings

#### Step 3: API Demo Flow

**1. Authentication & User Setup**
```bash
# Login as a member
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user1", "password": "password123"}'
# Save the access token from response
```

**2. Browse Available Classes**
```bash
# Get upcoming classes
curl "http://localhost:8000/api/classes/classes/?is_upcoming=true" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Filter by class type
curl "http://localhost:8000/api/classes/classes/?class_type_id=1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**3. Create a Fitness Profile**
```bash
# Update profile with fitness data
curl -X PUT http://localhost:8000/api/users/profiles/mine/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "height_cm": 175,
    "weight_kg": 70,
    "primary_goal": "muscle_gain",
    "activity_level": "moderate",
    "experience_level": "intermediate",
    "months_experience": 12
  }'
```

**4. Book a Class**
```bash
# Create booking
curl -X POST http://localhost:8000/api/classes/bookings/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"fitness_class_id": 1}'

# Check email console for confirmation link
```

**5. Confirm Booking**
```bash
# Confirm via email token
curl -X POST http://localhost:8000/api/classes/bookings/1/confirm/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"token": "CONFIRMATION_TOKEN_FROM_CONSOLE"}'
```

**6. Generate AI Workout Plan**
```bash
# Generate 7-day personalized workout
curl -X POST http://localhost:8000/api/users/profiles/generate_workout_plan/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"days": 7}'

# Get LLM context
curl "http://localhost:8000/api/users/profiles/llm_context/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**7. Log a Workout**
```bash
# Add workout to history
curl -X POST http://localhost:8000/api/users/profiles/add_workout_history/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "workout": {
      "type": "strength",
      "exercises": ["Squats", "Bench Press"],
      "duration_minutes": 60,
      "notes": "Great session!"
    }
  }'
```

**8. View Progress**
```bash
# Check workout history
curl "http://localhost:8000/api/users/profiles/workout_history/" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get recommendations
curl "http://localhost:8000/api/users/profiles/recommendations/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Demo Scenarios for Presentation

#### Scenario A: New Member Journey
1. Register account
2. Complete fitness profile
3. Browse beginner classes
4. Book first class
5. Receive confirmation email
6. View upcoming bookings

#### Scenario B: Fitness Progress Tracking
1. Update profile with metrics
2. Generate AI workout plan
3. Log completed workouts
4. Track progress over time
5. Get updated recommendations

#### Scenario C: Studio Management (Admin)
1. Create new class types
2. Assign instructors
3. View booking statistics
4. Manage cancellations
5. Send bulk notifications

## ⚙️ Management Commands

### Data Generation Commands
```bash
# Generate all demo data
poetry run python manage.py create_fake_data \
  --users 50 \
  --instructors 15 \
  --classes 100

# Individual commands
poetry run python manage.py create_fake_class_data    # Class types & levels
poetry run python manage.py create_fake_users --count 50      # Users
poetry run python manage.py create_fake_instructors --count 15 # Instructors
poetry run python manage.py create_fake_classes --count 100 --days 60 # Classes
poetry run python manage.py create_fake_bookings --count 200  # Bookings
```

## 🤖 LLM Integration

### Setup Real OpenAI Integration
1. Get OpenAI API key from [platform.openai.com](https://platform.openai.com)
2. Add to `.env` file:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```
3. The system will use GPT-3.5-turbo for workout generation

### Prompt Engineering
The system creates detailed prompts including:
- User fitness metrics (BMI, goals, experience)
- Workout history and preferences
- Equipment availability
- Medical considerations


### Debug Tools
```bash
# Django shell
python manage.py shell

# Check database
python manage.py dbshell

# Check URLs
python manage.py show_urls
```