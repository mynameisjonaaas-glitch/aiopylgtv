#!/usr/bin/env python3
"""
Example usage of the medical health record system.
"""

import os
from datetime import datetime, date
from aiopylgtv.medical_records import HealthRecordAPI, Patient, Doctor


def main():
    """Demonstrate the medical record system functionality."""
    print("=== Medical Health Record System Example ===")
    
    # Initialize API with test database
    db_path = "example_health_records.db"
    api = HealthRecordAPI(db_path)
    
    try:
        print("\n1. Registering users...")
        
        # Register an admin user
        admin_registered = api.register_user("admin", "admin@hospital.com", "admin123", "admin")
        print(f"Admin registration: {'Success' if admin_registered else 'Failed'}")
        
        # Register a doctor
        doctor_registered = api.register_user("dr_smith", "dr.smith@hospital.com", "doctor123", "doctor")
        print(f"Doctor registration: {'Success' if doctor_registered else 'Failed'}")
        
        # Register a regular user
        user_registered = api.register_user("nurse_jane", "nurse.jane@hospital.com", "nurse123", "user")
        print(f"User registration: {'Success' if user_registered else 'Failed'}")
        
        print("\n2. Logging in...")
        
        # Login as admin
        admin_token = api.login("admin", "admin123")
        print(f"Admin login: {'Success' if admin_token else 'Failed'}")
        
        # Login as doctor
        doctor_token = api.login("dr_smith", "doctor123")
        print(f"Doctor login: {'Success' if doctor_token else 'Failed'}")
        
        if not admin_token or not doctor_token:
            print("Login failed, cannot continue with example.")
            return
        
        print("\n3. Creating a doctor record...")
        
        doctor_data = {
            'first_name': 'John',
            'last_name': 'Smith',
            'specialization': 'Internal Medicine',
            'license_number': 'MD123456',
            'phone': '555-1234',
            'email': 'dr.john.smith@hospital.com',
            'department': 'Internal Medicine',
            'years_of_experience': 15
        }
        
        doctor_id = api.create_doctor(admin_token, doctor_data)
        print(f"Doctor created: {'Success' if doctor_id else 'Failed'}")
        if doctor_id:
            print(f"Doctor ID: {doctor_id}")
        
        print("\n4. Creating patient records...")
        
        # Create first patient
        patient1_data = {
            'first_name': 'Alice',
            'last_name': 'Johnson',
            'date_of_birth': '1985-03-15',
            'gender': 'female',
            'phone': '555-0001',
            'email': 'alice.johnson@email.com',
            'address': '123 Main St, City, State 12345',
            'emergency_contact_name': 'Bob Johnson',
            'emergency_contact_phone': '555-0002',
            'blood_type': 'A+',
            'allergies': ['penicillin', 'shellfish'],
            'medical_conditions': ['hypertension'],
            'medications': ['lisinopril 10mg'],
            'insurance_provider': 'Health Insurance Co.',
            'insurance_policy_number': 'HIC123456789'
        }
        
        patient1_id = api.create_patient(doctor_token, patient1_data)
        print(f"Patient 1 created: {'Success' if patient1_id else 'Failed'}")
        if patient1_id:
            print(f"Patient 1 ID: {patient1_id}")
        
        # Create second patient
        patient2_data = {
            'first_name': 'Robert',
            'last_name': 'Davis',
            'date_of_birth': '1972-08-22',
            'gender': 'male',
            'phone': '555-0003',
            'email': 'robert.davis@email.com',
            'address': '456 Oak Ave, City, State 12345',
            'emergency_contact_name': 'Mary Davis',
            'emergency_contact_phone': '555-0004',
            'blood_type': 'O-',
            'allergies': ['latex'],
            'medical_conditions': ['diabetes type 2'],
            'medications': ['metformin 500mg', 'insulin'],
            'insurance_provider': 'Medical Care Inc.',
            'insurance_policy_number': 'MCI987654321'
        }
        
        patient2_id = api.create_patient(doctor_token, patient2_data)
        print(f"Patient 2 created: {'Success' if patient2_id else 'Failed'}")
        if patient2_id:
            print(f"Patient 2 ID: {patient2_id}")
        
        print("\n5. Listing all patients...")
        
        patients = api.list_patients(doctor_token, limit=10)
        print(f"Found {len(patients)} patients:")
        
        for i, patient in enumerate(patients, 1):
            print(f"  {i}. {patient['full_name']} (Age: {patient['age']}, Phone: {patient['phone']})")
        
        print("\n6. Getting detailed patient information...")
        
        if patient1_id:
            patient_details = api.get_patient(doctor_token, patient1_id)
            if patient_details:
                print(f"Patient Details for {patient_details['full_name']}:")
                print(f"  Age: {patient_details['age']}")
                print(f"  Phone: {patient_details['phone']}")
                print(f"  Email: {patient_details['email']}")
                print(f"  Blood Type: {patient_details['blood_type']}")
                print(f"  Allergies: {', '.join(patient_details['allergies']) if patient_details['allergies'] else 'None'}")
                print(f"  Medical Conditions: {', '.join(patient_details['medical_conditions']) if patient_details['medical_conditions'] else 'None'}")
                print(f"  Medications: {', '.join(patient_details['medications']) if patient_details['medications'] else 'None'}")
        
        print("\n7. Creating medical records...")
        
        if patient1_id and doctor_id:
            medical_record_data = {
                'patient_id': patient1_id,
                'doctor_id': doctor_id,
                'visit_date': datetime.now().isoformat(),
                'chief_complaint': 'Annual checkup',
                'diagnosis': 'Hypertension, well controlled',
                'treatment_plan': 'Continue current medication, lifestyle modifications',
                'prescriptions': ['lisinopril 10mg daily', 'vitamin D3 1000 IU daily'],
                'vital_signs': {
                    'blood_pressure': '130/85',
                    'heart_rate': '72',
                    'temperature': '98.6',
                    'weight': '150',
                    'height': '65'
                },
                'lab_results': {
                    'cholesterol_total': '185',
                    'hdl': '45',
                    'ldl': '115',
                    'glucose': '95'
                },
                'notes': 'Patient feeling well, no new complaints. Continue current treatment plan.',
                'follow_up_required': True,
                'follow_up_date': '2024-04-01T10:00:00'
            }
            
            record_id = api.create_medical_record(doctor_token, medical_record_data)
            print(f"Medical record created: {'Success' if record_id else 'Failed'}")
            if record_id:
                print(f"Medical record ID: {record_id}")
        
        print("\n8. Creating appointments...")
        
        if patient1_id and doctor_id:
            appointment_data = {
                'patient_id': patient1_id,
                'doctor_id': doctor_id,
                'appointment_date': '2024-04-01T10:00:00',
                'duration_minutes': 30,
                'status': 'scheduled',
                'reason': 'Follow-up visit',
                'notes': 'Check blood pressure and lab results'
            }
            
            appointment_id = api.create_appointment(doctor_token, appointment_data)
            print(f"Appointment created: {'Success' if appointment_id else 'Failed'}")
            if appointment_id:
                print(f"Appointment ID: {appointment_id}")
        
        print("\n=== Example completed successfully! ===")
        print(f"Database created at: {os.path.abspath(db_path)}")
        print("You can now use the CLI tool to interact with this database:")
        print(f"  medical-records --interactive")
        
    except Exception as e:
        print(f"Error during example execution: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        api.close()


if __name__ == '__main__':
    main()