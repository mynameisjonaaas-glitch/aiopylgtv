"""
API layer for the medical health record system.
Provides a high-level interface for managing health records.
"""

import logging
from datetime import datetime, date
from typing import List, Optional, Dict, Any

from .models import Patient, Doctor, MedicalRecord, Appointment, User, Gender, BloodType, AppointmentStatus
from .database import HealthRecordDB
from .auth import AuthManager

logger = logging.getLogger(__name__)


class HealthRecordAPI:
    """High-level API for the medical health record system."""
    
    def __init__(self, db_path: str = "health_records.db", secret_key: str = None):
        """Initialize the API with database and authentication."""
        self.db = HealthRecordDB(db_path)
        self.auth = AuthManager(secret_key)
        logger.info("Health Record API initialized")
    
    def close(self):
        """Close database connections."""
        self.db.close()
    
    # Authentication methods
    def register_user(self, username: str, email: str, password: str, role: str = "user") -> bool:
        """Register a new user."""
        try:
            # Check if username already exists
            cursor = self.db.connection.cursor()
            cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                logger.warning(f"Username {username} already exists")
                return False
            
            # Create new user
            user = User(
                username=username,
                email=email,
                password_hash=self.auth.hash_password(password),
                role=role
            )
            
            cursor.execute("""
                INSERT INTO users (user_id, username, email, password_hash, role, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user.user_id, user.username, user.email, user.password_hash, 
                  user.role, user.is_active, user.created_at))
            
            self.db.connection.commit()
            logger.info(f"User registered: {username}")
            return True
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            return False
    
    def login(self, username: str, password: str) -> Optional[str]:
        """Authenticate user and return JWT token."""
        try:
            cursor = self.db.connection.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND is_active = 1", (username,))
            row = cursor.fetchone()
            
            if not row:
                logger.warning(f"User not found or inactive: {username}")
                return None
            
            if not self.auth.verify_password(password, row["password_hash"]):
                logger.warning(f"Invalid password for user: {username}")
                return None
            
            # Update last login
            cursor.execute("UPDATE users SET last_login = ? WHERE username = ?", 
                          (datetime.now(), username))
            self.db.connection.commit()
            
            user = User(
                user_id=row["user_id"],
                username=row["username"],
                email=row["email"] or "",
                password_hash=row["password_hash"],
                role=row["role"],
                is_active=bool(row["is_active"]),
                created_at=datetime.fromisoformat(row["created_at"]),
                last_login=datetime.now()
            )
            
            token = self.auth.create_token(user)
            logger.info(f"User logged in: {username}")
            return token
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return None
    
    # Patient management methods
    def create_patient(self, token: str, patient_data: Dict[str, Any]) -> Optional[str]:
        """Create a new patient (requires doctor or admin role)."""
        auth_payload = self.auth.require_auth(token, 'doctor')
        if not auth_payload:
            return None
        
        try:
            patient = Patient(
                first_name=patient_data.get('first_name', ''),
                last_name=patient_data.get('last_name', ''),
                date_of_birth=datetime.fromisoformat(patient_data['date_of_birth']).date() 
                              if patient_data.get('date_of_birth') else None,
                gender=Gender(patient_data.get('gender', 'prefer_not_to_say')),
                phone=patient_data.get('phone', ''),
                email=patient_data.get('email', ''),
                address=patient_data.get('address', ''),
                emergency_contact_name=patient_data.get('emergency_contact_name', ''),
                emergency_contact_phone=patient_data.get('emergency_contact_phone', ''),
                blood_type=BloodType(patient_data.get('blood_type', 'unknown')),
                allergies=patient_data.get('allergies', []),
                medical_conditions=patient_data.get('medical_conditions', []),
                medications=patient_data.get('medications', []),
                insurance_provider=patient_data.get('insurance_provider', ''),
                insurance_policy_number=patient_data.get('insurance_policy_number', '')
            )
            
            if self.db.create_patient(patient):
                logger.info(f"Patient created by {auth_payload['username']}: {patient.full_name}")
                return patient.patient_id
            return None
        except Exception as e:
            logger.error(f"Error creating patient: {e}")
            return None
    
    def get_patient(self, token: str, patient_id: str) -> Optional[Dict[str, Any]]:
        """Get patient information (requires authentication)."""
        auth_payload = self.auth.require_auth(token)
        if not auth_payload:
            return None
        
        patient = self.db.get_patient(patient_id)
        if not patient:
            return None
        
        return {
            'patient_id': patient.patient_id,
            'full_name': patient.full_name,
            'first_name': patient.first_name,
            'last_name': patient.last_name,
            'date_of_birth': patient.date_of_birth.isoformat() if patient.date_of_birth else None,
            'age': patient.age,
            'gender': patient.gender.value,
            'phone': patient.phone,
            'email': patient.email,
            'address': patient.address,
            'emergency_contact_name': patient.emergency_contact_name,
            'emergency_contact_phone': patient.emergency_contact_phone,
            'blood_type': patient.blood_type.value,
            'allergies': patient.allergies,
            'medical_conditions': patient.medical_conditions,
            'medications': patient.medications,
            'insurance_provider': patient.insurance_provider,
            'insurance_policy_number': patient.insurance_policy_number,
            'created_at': patient.created_at.isoformat(),
            'updated_at': patient.updated_at.isoformat()
        }
    
    def list_patients(self, token: str, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List all patients (requires authentication)."""
        auth_payload = self.auth.require_auth(token)
        if not auth_payload:
            return []
        
        patients = self.db.list_patients(limit, offset)
        return [
            {
                'patient_id': p.patient_id,
                'full_name': p.full_name,
                'age': p.age,
                'phone': p.phone,
                'email': p.email,
                'created_at': p.created_at.isoformat()
            }
            for p in patients
        ]
    
    def create_doctor(self, token: str, doctor_data: Dict[str, Any]) -> Optional[str]:
        """Create a new doctor (requires admin role)."""
        auth_payload = self.auth.require_auth(token, 'admin')
        if not auth_payload:
            return None
        
        try:
            doctor = Doctor(
                first_name=doctor_data.get('first_name', ''),
                last_name=doctor_data.get('last_name', ''),
                specialization=doctor_data.get('specialization', ''),
                license_number=doctor_data.get('license_number', ''),
                phone=doctor_data.get('phone', ''),
                email=doctor_data.get('email', ''),
                department=doctor_data.get('department', ''),
                years_of_experience=doctor_data.get('years_of_experience', 0)
            )
            
            if self.db.create_doctor(doctor):
                logger.info(f"Doctor created by {auth_payload['username']}: {doctor.full_name}")
                return doctor.doctor_id
            return None
        except Exception as e:
            logger.error(f"Error creating doctor: {e}")
            return None
    
    def create_medical_record(self, token: str, record_data: Dict[str, Any]) -> Optional[str]:
        """Create a new medical record (requires doctor role)."""
        auth_payload = self.auth.require_auth(token, 'doctor')
        if not auth_payload:
            return None
        
        try:
            record = MedicalRecord(
                patient_id=record_data['patient_id'],
                doctor_id=record_data['doctor_id'],
                visit_date=datetime.fromisoformat(record_data.get('visit_date', datetime.now().isoformat())),
                chief_complaint=record_data.get('chief_complaint', ''),
                diagnosis=record_data.get('diagnosis', ''),
                treatment_plan=record_data.get('treatment_plan', ''),
                prescriptions=record_data.get('prescriptions', []),
                vital_signs=record_data.get('vital_signs', {}),
                lab_results=record_data.get('lab_results', {}),
                notes=record_data.get('notes', ''),
                follow_up_required=record_data.get('follow_up_required', False),
                follow_up_date=datetime.fromisoformat(record_data['follow_up_date']) 
                              if record_data.get('follow_up_date') else None
            )
            
            if self.db.create_medical_record(record):
                logger.info(f"Medical record created by {auth_payload['username']}: {record.record_id}")
                return record.record_id
            return None
        except Exception as e:
            logger.error(f"Error creating medical record: {e}")
            return None
    
    def create_appointment(self, token: str, appointment_data: Dict[str, Any]) -> Optional[str]:
        """Create a new appointment (requires authentication)."""
        auth_payload = self.auth.require_auth(token)
        if not auth_payload:
            return None
        
        try:
            appointment = Appointment(
                patient_id=appointment_data['patient_id'],
                doctor_id=appointment_data['doctor_id'],
                appointment_date=datetime.fromisoformat(appointment_data['appointment_date']),
                duration_minutes=appointment_data.get('duration_minutes', 30),
                status=AppointmentStatus(appointment_data.get('status', 'scheduled')),
                reason=appointment_data.get('reason', ''),
                notes=appointment_data.get('notes', '')
            )
            
            if self.db.create_appointment(appointment):
                logger.info(f"Appointment created by {auth_payload['username']}: {appointment.appointment_id}")
                return appointment.appointment_id
            return None
        except Exception as e:
            logger.error(f"Error creating appointment: {e}")
            return None