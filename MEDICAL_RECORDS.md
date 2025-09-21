# Medical Health Record System

This repository now includes a comprehensive medical health record system alongside the original LG WebOS TV control functionality.

## Features

- **Patient Management**: Complete CRUD operations for patient records
- **Medical Records**: Detailed visit documentation with diagnoses, treatments, and prescriptions
- **Appointment Scheduling**: Book and manage patient appointments
- **User Authentication**: Secure JWT-based authentication with role-based access control
- **Command Line Interface**: Interactive CLI for easy management
- **Database Backend**: SQLite database for reliable data persistence

## Quick Start

### 1. Installation

```bash
pip install -e .
```

### 2. Run the Example

```bash
python examples/medical_records_example.py
```

This will create a sample database with users, patients, doctors, medical records, and appointments.

### 3. Use the CLI

```bash
# Interactive mode
python -m aiopylgtv.medical_records.cli --interactive

# Or specific commands
python -m aiopylgtv.medical_records.cli register
python -m aiopylgtv.medical_records.cli patient list
```

## System Architecture

### Models

#### Patient
- Personal information (name, DOB, contact details)
- Medical information (allergies, conditions, medications)
- Insurance information
- Emergency contacts

#### Doctor
- Professional information
- Specialization and credentials
- Contact details

#### Medical Record
- Visit documentation
- Diagnoses and treatment plans
- Vital signs and lab results
- Prescriptions and notes

#### Appointment
- Scheduling information
- Status tracking
- Duration and purpose

#### User
- Authentication credentials
- Role-based permissions

### Authentication & Authorization

The system implements a three-tier role system:

1. **User**: Basic access to view patient information
2. **Doctor**: Can create and modify patient records and medical records
3. **Admin**: Full system access including user and doctor management

### Database Schema

The system uses SQLite with the following tables:
- `patients` - Patient information
- `doctors` - Doctor information  
- `medical_records` - Visit records
- `appointments` - Appointment scheduling
- `users` - Authentication and authorization

## API Usage

### Basic Example

```python
from aiopylgtv.medical_records import HealthRecordAPI

# Initialize API
api = HealthRecordAPI("health_records.db")

# Register and login
api.register_user("doctor1", "doctor@hospital.com", "password", "doctor")
token = api.login("doctor1", "password")

# Create a patient
patient_data = {
    'first_name': 'John',
    'last_name': 'Doe',
    'date_of_birth': '1990-01-01',
    'gender': 'male',
    'phone': '555-0123',
    'email': 'john.doe@email.com',
    'blood_type': 'A+',
    'allergies': ['penicillin'],
    'medical_conditions': ['hypertension']
}

patient_id = api.create_patient(token, patient_data)

# Retrieve patient
patient = api.get_patient(token, patient_id)
print(f"Patient: {patient['full_name']}, Age: {patient['age']}")

# Clean up
api.close()
```

### CLI Usage

#### Interactive Mode

```bash
python -m aiopylgtv.medical_records.cli --interactive
```

This provides a menu-driven interface for:
- User registration and login
- Patient management
- Viewing patient information

#### Command Line Mode

```bash
# Register a new user
python -m aiopylgtv.medical_records.cli register

# List patients
python -m aiopylgtv.medical_records.cli patient list --limit 50

# Get patient details
python -m aiopylgtv.medical_records.cli patient get <patient_id>
```

## Security Features

- **Password Hashing**: PBKDF2 with salt for secure password storage
- **JWT Tokens**: Stateless authentication with configurable expiration
- **Role-Based Access**: Hierarchical permission system
- **Input Validation**: Comprehensive data validation and sanitization

## Data Models

### Patient Information
- Demographics and contact information
- Medical history and current conditions
- Allergies and medications
- Insurance and emergency contacts

### Medical Records
- Visit date and doctor information
- Chief complaints and diagnoses
- Treatment plans and prescriptions
- Vital signs and laboratory results
- Follow-up requirements

### Appointments
- Scheduling with doctors
- Status tracking (scheduled, confirmed, completed, etc.)
- Duration and purpose
- Notes and comments

## Testing

Run the test suite:

```bash
python tests/test_medical_records.py
```

The tests cover:
- Model creation and validation
- Database operations
- Authentication and authorization
- API functionality
- Permission checking

## Configuration

The system can be configured with:
- Database path (default: "health_records.db")
- JWT secret key (auto-generated if not provided)
- Token expiration time (default: 24 hours)

## Database Management

The SQLite database is automatically created with proper schema. For production use, consider:
- Regular backups
- Database encryption
- Access logging
- Data retention policies

## Integration with Existing Code

The medical records system is designed to coexist with the existing LG TV control functionality. Both systems can be imported and used independently:

```python
# Use TV control functionality
from aiopylgtv import WebOsClient

# Use medical records functionality  
from aiopylgtv.medical_records import HealthRecordAPI
```

## Future Enhancements

Potential areas for expansion:
- Web interface
- API rate limiting
- Audit logging
- Data export/import
- Integration with external systems
- Mobile application support
- Real-time notifications
- Advanced reporting and analytics