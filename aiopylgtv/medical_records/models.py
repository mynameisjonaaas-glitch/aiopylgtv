"""
Data models for the medical health record system.
"""

import uuid
from datetime import datetime, date
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class Gender(Enum):
    """Gender enumeration."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class AppointmentStatus(Enum):
    """Appointment status enumeration."""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class BloodType(Enum):
    """Blood type enumeration."""
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"
    UNKNOWN = "unknown"


@dataclass
class Patient:
    """Patient model for storing patient information."""
    
    patient_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    first_name: str = ""
    last_name: str = ""
    date_of_birth: Optional[date] = None
    gender: Gender = Gender.PREFER_NOT_TO_SAY
    phone: str = ""
    email: str = ""
    address: str = ""
    emergency_contact_name: str = ""
    emergency_contact_phone: str = ""
    blood_type: BloodType = BloodType.UNKNOWN
    allergies: List[str] = field(default_factory=list)
    medical_conditions: List[str] = field(default_factory=list)
    medications: List[str] = field(default_factory=list)
    insurance_provider: str = ""
    insurance_policy_number: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    @property
    def full_name(self) -> str:
        """Get the patient's full name."""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def age(self) -> Optional[int]:
        """Calculate the patient's age."""
        if not self.date_of_birth:
            return None
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )


@dataclass
class Doctor:
    """Doctor model for storing doctor information."""
    
    doctor_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    first_name: str = ""
    last_name: str = ""
    specialization: str = ""
    license_number: str = ""
    phone: str = ""
    email: str = ""
    department: str = ""
    years_of_experience: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def full_name(self) -> str:
        """Get the doctor's full name."""
        return f"Dr. {self.first_name} {self.last_name}".strip()


@dataclass
class MedicalRecord:
    """Medical record model for storing patient medical information."""
    
    record_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str = ""
    doctor_id: str = ""
    visit_date: datetime = field(default_factory=datetime.now)
    chief_complaint: str = ""
    diagnosis: str = ""
    treatment_plan: str = ""
    prescriptions: List[str] = field(default_factory=list)
    vital_signs: Dict[str, Any] = field(default_factory=dict)
    lab_results: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""
    follow_up_required: bool = False
    follow_up_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Appointment:
    """Appointment model for scheduling patient visits."""
    
    appointment_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str = ""
    doctor_id: str = ""
    appointment_date: datetime = field(default_factory=datetime.now)
    duration_minutes: int = 30
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    reason: str = ""
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    @property
    def end_time(self) -> datetime:
        """Calculate the appointment end time."""
        from datetime import timedelta
        return self.appointment_date + timedelta(minutes=self.duration_minutes)


@dataclass
class User:
    """User model for system authentication."""
    
    user_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    username: str = ""
    email: str = ""
    password_hash: str = ""
    role: str = "user"  # user, doctor, admin
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None