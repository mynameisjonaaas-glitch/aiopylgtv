"""
Database management for the medical health record system.
Uses SQLite for data persistence with a simple ORM-like interface.
"""

import sqlite3
import json
import logging
from datetime import datetime, date
from typing import List, Optional, Dict, Any, Union
from pathlib import Path

from .models import Patient, Doctor, MedicalRecord, Appointment, User, Gender, AppointmentStatus, BloodType

logger = logging.getLogger(__name__)


class HealthRecordDB:
    """Database manager for the medical health record system."""
    
    def __init__(self, db_path: str = "health_records.db"):
        """Initialize the database connection and create tables if they don't exist."""
        self.db_path = Path(db_path)
        self.connection = None
        self.connect()
        self.create_tables()
        
    def connect(self):
        """Connect to the SQLite database."""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            logger.info(f"Connected to database: {self.db_path}")
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise
    
    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
    def create_tables(self):
        """Create all necessary tables for the health record system."""
        cursor = self.connection.cursor()
        
        # Patients table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                patient_id TEXT PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                date_of_birth DATE,
                gender TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                emergency_contact_name TEXT,
                emergency_contact_phone TEXT,
                blood_type TEXT,
                allergies TEXT,
                medical_conditions TEXT,
                medications TEXT,
                insurance_provider TEXT,
                insurance_policy_number TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Doctors table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS doctors (
                doctor_id TEXT PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                specialization TEXT,
                license_number TEXT,
                phone TEXT,
                email TEXT,
                department TEXT,
                years_of_experience INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Medical records table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medical_records (
                record_id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                doctor_id TEXT NOT NULL,
                visit_date TIMESTAMP,
                chief_complaint TEXT,
                diagnosis TEXT,
                treatment_plan TEXT,
                prescriptions TEXT,
                vital_signs TEXT,
                lab_results TEXT,
                notes TEXT,
                follow_up_required BOOLEAN,
                follow_up_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients (patient_id),
                FOREIGN KEY (doctor_id) REFERENCES doctors (doctor_id)
            )
        """)
        
        # Appointments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                appointment_id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                doctor_id TEXT NOT NULL,
                appointment_date TIMESTAMP,
                duration_minutes INTEGER,
                status TEXT,
                reason TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients (patient_id),
                FOREIGN KEY (doctor_id) REFERENCES doctors (doctor_id)
            )
        """)
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT,
                password_hash TEXT NOT NULL,
                role TEXT,
                is_active BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """)
        
        self.connection.commit()
        logger.info("Database tables created successfully")
    
    def _serialize_list(self, data: List[str]) -> str:
        """Serialize a list to JSON string."""
        return json.dumps(data) if data else "[]"
    
    def _deserialize_list(self, data: str) -> List[str]:
        """Deserialize JSON string to list."""
        return json.loads(data) if data else []
    
    def _serialize_dict(self, data: Dict[str, Any]) -> str:
        """Serialize a dictionary to JSON string."""
        return json.dumps(data) if data else "{}"
    
    def _deserialize_dict(self, data: str) -> Dict[str, Any]:
        """Deserialize JSON string to dictionary."""
        return json.loads(data) if data else {}
    
    # Patient operations
    def create_patient(self, patient: Patient) -> bool:
        """Create a new patient record."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO patients (
                    patient_id, first_name, last_name, date_of_birth, gender,
                    phone, email, address, emergency_contact_name, emergency_contact_phone,
                    blood_type, allergies, medical_conditions, medications,
                    insurance_provider, insurance_policy_number, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                patient.patient_id, patient.first_name, patient.last_name,
                patient.date_of_birth, patient.gender.value,
                patient.phone, patient.email, patient.address,
                patient.emergency_contact_name, patient.emergency_contact_phone,
                patient.blood_type.value, self._serialize_list(patient.allergies),
                self._serialize_list(patient.medical_conditions),
                self._serialize_list(patient.medications),
                patient.insurance_provider, patient.insurance_policy_number,
                patient.created_at, patient.updated_at
            ))
            self.connection.commit()
            logger.info(f"Created patient: {patient.full_name}")
            return True
        except Exception as e:
            logger.error(f"Error creating patient: {e}")
            return False
    
    def get_patient(self, patient_id: str) -> Optional[Patient]:
        """Retrieve a patient by ID."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM patients WHERE patient_id = ?", (patient_id,))
            row = cursor.fetchone()
            
            if row:
                return Patient(
                    patient_id=row["patient_id"],
                    first_name=row["first_name"],
                    last_name=row["last_name"],
                    date_of_birth=datetime.fromisoformat(row["date_of_birth"]).date() if row["date_of_birth"] else None,
                    gender=Gender(row["gender"]) if row["gender"] else Gender.PREFER_NOT_TO_SAY,
                    phone=row["phone"] or "",
                    email=row["email"] or "",
                    address=row["address"] or "",
                    emergency_contact_name=row["emergency_contact_name"] or "",
                    emergency_contact_phone=row["emergency_contact_phone"] or "",
                    blood_type=BloodType(row["blood_type"]) if row["blood_type"] else BloodType.UNKNOWN,
                    allergies=self._deserialize_list(row["allergies"]),
                    medical_conditions=self._deserialize_list(row["medical_conditions"]),
                    medications=self._deserialize_list(row["medications"]),
                    insurance_provider=row["insurance_provider"] or "",
                    insurance_policy_number=row["insurance_policy_number"] or "",
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else datetime.now()
                )
            return None
        except Exception as e:
            logger.error(f"Error retrieving patient: {e}")
            return None
    
    def update_patient(self, patient: Patient) -> bool:
        """Update an existing patient record."""
        try:
            patient.updated_at = datetime.now()
            cursor = self.connection.cursor()
            cursor.execute("""
                UPDATE patients SET
                    first_name = ?, last_name = ?, date_of_birth = ?, gender = ?,
                    phone = ?, email = ?, address = ?, emergency_contact_name = ?,
                    emergency_contact_phone = ?, blood_type = ?, allergies = ?,
                    medical_conditions = ?, medications = ?, insurance_provider = ?,
                    insurance_policy_number = ?, updated_at = ?
                WHERE patient_id = ?
            """, (
                patient.first_name, patient.last_name, patient.date_of_birth, patient.gender.value,
                patient.phone, patient.email, patient.address, patient.emergency_contact_name,
                patient.emergency_contact_phone, patient.blood_type.value,
                self._serialize_list(patient.allergies), self._serialize_list(patient.medical_conditions),
                self._serialize_list(patient.medications), patient.insurance_provider,
                patient.insurance_policy_number, patient.updated_at, patient.patient_id
            ))
            self.connection.commit()
            logger.info(f"Updated patient: {patient.full_name}")
            return True
        except Exception as e:
            logger.error(f"Error updating patient: {e}")
            return False
    
    def delete_patient(self, patient_id: str) -> bool:
        """Delete a patient record."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM patients WHERE patient_id = ?", (patient_id,))
            self.connection.commit()
            logger.info(f"Deleted patient: {patient_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting patient: {e}")
            return False
    
    def list_patients(self, limit: int = 100, offset: int = 0) -> List[Patient]:
        """List all patients with pagination."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM patients ORDER BY last_name, first_name LIMIT ? OFFSET ?", (limit, offset))
            rows = cursor.fetchall()
            
            patients = []
            for row in rows:
                patient = Patient(
                    patient_id=row["patient_id"],
                    first_name=row["first_name"],
                    last_name=row["last_name"],
                    date_of_birth=datetime.fromisoformat(row["date_of_birth"]).date() if row["date_of_birth"] else None,
                    gender=Gender(row["gender"]) if row["gender"] else Gender.PREFER_NOT_TO_SAY,
                    phone=row["phone"] or "",
                    email=row["email"] or "",
                    address=row["address"] or "",
                    emergency_contact_name=row["emergency_contact_name"] or "",
                    emergency_contact_phone=row["emergency_contact_phone"] or "",
                    blood_type=BloodType(row["blood_type"]) if row["blood_type"] else BloodType.UNKNOWN,
                    allergies=self._deserialize_list(row["allergies"]),
                    medical_conditions=self._deserialize_list(row["medical_conditions"]),
                    medications=self._deserialize_list(row["medications"]),
                    insurance_provider=row["insurance_provider"] or "",
                    insurance_policy_number=row["insurance_policy_number"] or "",
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else datetime.now()
                )
                patients.append(patient)
            
            return patients
        except Exception as e:
            logger.error(f"Error listing patients: {e}")
            return []
    
    # Similar methods for doctors, medical records, and appointments would follow the same pattern
    # For brevity, I'll include a few key methods for each model type
    
    def create_doctor(self, doctor: Doctor) -> bool:
        """Create a new doctor record."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO doctors (
                    doctor_id, first_name, last_name, specialization, license_number,
                    phone, email, department, years_of_experience, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                doctor.doctor_id, doctor.first_name, doctor.last_name,
                doctor.specialization, doctor.license_number, doctor.phone,
                doctor.email, doctor.department, doctor.years_of_experience,
                doctor.created_at
            ))
            self.connection.commit()
            logger.info(f"Created doctor: {doctor.full_name}")
            return True
        except Exception as e:
            logger.error(f"Error creating doctor: {e}")
            return False
    
    def create_medical_record(self, record: MedicalRecord) -> bool:
        """Create a new medical record."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO medical_records (
                    record_id, patient_id, doctor_id, visit_date, chief_complaint,
                    diagnosis, treatment_plan, prescriptions, vital_signs, lab_results,
                    notes, follow_up_required, follow_up_date, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.record_id, record.patient_id, record.doctor_id, record.visit_date,
                record.chief_complaint, record.diagnosis, record.treatment_plan,
                self._serialize_list(record.prescriptions), self._serialize_dict(record.vital_signs),
                self._serialize_dict(record.lab_results), record.notes, record.follow_up_required,
                record.follow_up_date, record.created_at, record.updated_at
            ))
            self.connection.commit()
            logger.info(f"Created medical record: {record.record_id}")
            return True
        except Exception as e:
            logger.error(f"Error creating medical record: {e}")
            return False
    
    def create_appointment(self, appointment: Appointment) -> bool:
        """Create a new appointment."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO appointments (
                    appointment_id, patient_id, doctor_id, appointment_date,
                    duration_minutes, status, reason, notes, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                appointment.appointment_id, appointment.patient_id, appointment.doctor_id,
                appointment.appointment_date, appointment.duration_minutes, appointment.status.value,
                appointment.reason, appointment.notes, appointment.created_at, appointment.updated_at
            ))
            self.connection.commit()
            logger.info(f"Created appointment: {appointment.appointment_id}")
            return True
        except Exception as e:
            logger.error(f"Error creating appointment: {e}")
            return False