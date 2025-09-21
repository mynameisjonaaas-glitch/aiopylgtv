"""
Tests for the medical health record system.
"""

import unittest
import tempfile
import os
from datetime import datetime, date

from aiopylgtv.medical_records.models import Patient, Doctor, Gender, BloodType
from aiopylgtv.medical_records.database import HealthRecordDB
from aiopylgtv.medical_records.api import HealthRecordAPI
from aiopylgtv.medical_records.auth import AuthManager


class TestMedicalRecordsModels(unittest.TestCase):
    """Test the data models."""
    
    def test_patient_creation(self):
        """Test patient model creation."""
        patient = Patient(
            first_name="John",
            last_name="Doe",
            date_of_birth=date(1990, 1, 1),
            gender=Gender.MALE,
            phone="555-0123",
            email="john.doe@example.com"
        )
        
        self.assertEqual(patient.full_name, "John Doe")
        self.assertIsNotNone(patient.patient_id)
        self.assertIsInstance(patient.age, int)
        self.assertGreater(patient.age, 30)
    
    def test_doctor_creation(self):
        """Test doctor model creation."""
        doctor = Doctor(
            first_name="Jane",
            last_name="Smith",
            specialization="Cardiology",
            license_number="MD123456"
        )
        
        self.assertEqual(doctor.full_name, "Dr. Jane Smith")
        self.assertIsNotNone(doctor.doctor_id)


class TestHealthRecordDB(unittest.TestCase):
    """Test the database functionality."""
    
    def setUp(self):
        """Set up test database."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.temp_db.close()
        self.db = HealthRecordDB(self.temp_db.name)
    
    def tearDown(self):
        """Clean up test database."""
        self.db.close()
        os.unlink(self.temp_db.name)
    
    def test_create_and_retrieve_patient(self):
        """Test creating and retrieving a patient."""
        patient = Patient(
            first_name="Alice",
            last_name="Johnson",
            date_of_birth=date(1985, 5, 15),
            gender=Gender.FEMALE,
            phone="555-0456",
            email="alice.johnson@example.com",
            blood_type=BloodType.A_POSITIVE,
            allergies=["penicillin", "shellfish"]
        )
        
        # Create patient
        self.assertTrue(self.db.create_patient(patient))
        
        # Retrieve patient
        retrieved_patient = self.db.get_patient(patient.patient_id)
        self.assertIsNotNone(retrieved_patient)
        self.assertEqual(retrieved_patient.first_name, "Alice")
        self.assertEqual(retrieved_patient.last_name, "Johnson")
        self.assertEqual(retrieved_patient.blood_type, BloodType.A_POSITIVE)
        self.assertIn("penicillin", retrieved_patient.allergies)
    
    def test_create_doctor(self):
        """Test creating a doctor."""
        doctor = Doctor(
            first_name="Robert",
            last_name="Brown",
            specialization="Pediatrics",
            license_number="MD789012",
            years_of_experience=15
        )
        
        self.assertTrue(self.db.create_doctor(doctor))
    
    def test_list_patients(self):
        """Test listing patients."""
        # Create multiple patients
        patients = [
            Patient(first_name="Patient", last_name=f"Test{i}", phone=f"555-{i:04d}")
            for i in range(1, 6)
        ]
        
        for patient in patients:
            self.assertTrue(self.db.create_patient(patient))
        
        # List patients
        retrieved_patients = self.db.list_patients(limit=10)
        self.assertEqual(len(retrieved_patients), 5)


class TestAuthManager(unittest.TestCase):
    """Test the authentication manager."""
    
    def setUp(self):
        """Set up auth manager."""
        self.auth = AuthManager("test_secret_key")
    
    def test_password_hashing(self):
        """Test password hashing and verification."""
        password = "test_password123"
        password_hash = self.auth.hash_password(password)
        
        self.assertIsInstance(password_hash, str)
        self.assertIn(":", password_hash)  # Salt and hash separated by colon
        self.assertTrue(self.auth.verify_password(password, password_hash))
        self.assertFalse(self.auth.verify_password("wrong_password", password_hash))
    
    def test_token_creation_and_verification(self):
        """Test JWT token creation and verification."""
        from aiopylgtv.medical_records.models import User
        
        user = User(
            username="testuser",
            email="test@example.com",
            role="doctor"
        )
        
        token = self.auth.create_token(user)
        self.assertIsInstance(token, str)
        
        payload = self.auth.verify_token(token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload['username'], "testuser")
        self.assertEqual(payload['role'], "doctor")
    
    def test_permission_checking(self):
        """Test permission hierarchy."""
        self.assertTrue(self.auth.has_permission("admin", "user"))
        self.assertTrue(self.auth.has_permission("doctor", "user"))
        self.assertTrue(self.auth.has_permission("admin", "doctor"))
        self.assertFalse(self.auth.has_permission("user", "doctor"))
        self.assertFalse(self.auth.has_permission("doctor", "admin"))


class TestHealthRecordAPI(unittest.TestCase):
    """Test the API functionality."""
    
    def setUp(self):
        """Set up test API."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.temp_db.close()
        self.api = HealthRecordAPI(self.temp_db.name, "test_secret")
    
    def tearDown(self):
        """Clean up test API."""
        self.api.close()
        os.unlink(self.temp_db.name)
    
    def test_user_registration_and_login(self):
        """Test user registration and login."""
        # Register user
        self.assertTrue(self.api.register_user("testdoc", "doc@example.com", "password123", "doctor"))
        
        # Login
        token = self.api.login("testdoc", "password123")
        self.assertIsNotNone(token)
        
        # Test invalid login
        invalid_token = self.api.login("testdoc", "wrongpassword")
        self.assertIsNone(invalid_token)
    
    def test_patient_creation_with_auth(self):
        """Test patient creation with authentication."""
        # Register doctor
        self.assertTrue(self.api.register_user("doctor1", "doctor1@example.com", "docpass", "doctor"))
        token = self.api.login("doctor1", "docpass")
        
        # Create patient
        patient_data = {
            'first_name': 'Test',
            'last_name': 'Patient',
            'date_of_birth': '1990-01-01',
            'gender': 'male',
            'phone': '555-0789',
            'email': 'testpatient@example.com',
            'blood_type': 'O+',
            'allergies': ['dust', 'pollen'],
            'medical_conditions': ['asthma'],
            'medications': ['inhaler']
        }
        
        patient_id = self.api.create_patient(token, patient_data)
        self.assertIsNotNone(patient_id)
        
        # Retrieve patient
        patient = self.api.get_patient(token, patient_id)
        self.assertIsNotNone(patient)
        self.assertEqual(patient['first_name'], 'Test')
        self.assertEqual(patient['last_name'], 'Patient')


if __name__ == '__main__':
    unittest.main()