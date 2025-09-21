"""
Medical Health Record System

A comprehensive system for managing patient medical records, appointments,
and healthcare data.
"""

from .models import Patient, MedicalRecord, Appointment, Doctor
from .database import HealthRecordDB
from .api import HealthRecordAPI
from .auth import AuthManager

__all__ = [
    "Patient",
    "MedicalRecord", 
    "Appointment",
    "Doctor",
    "HealthRecordDB",
    "HealthRecordAPI",
    "AuthManager",
]

__version__ = "1.0.0"