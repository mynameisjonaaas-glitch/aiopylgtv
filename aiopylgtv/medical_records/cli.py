"""
Command line interface for the medical health record system.
"""

import argparse
import getpass
import json
import sys
from datetime import datetime, date
from typing import Dict, Any

from .api import HealthRecordAPI
from .models import Gender, BloodType, AppointmentStatus


class MedicalRecordsCLI:
    """Command line interface for medical records management."""
    
    def __init__(self):
        """Initialize the CLI."""
        self.api = HealthRecordAPI()
        self.token = None
    
    def __del__(self):
        """Cleanup on exit."""
        if hasattr(self, 'api'):
            self.api.close()
    
    def login_prompt(self):
        """Prompt user for login credentials."""
        print("=== Medical Health Record System ===")
        print("Please log in to continue:")
        
        username = input("Username: ")
        password = getpass.getpass("Password: ")
        
        self.token = self.api.login(username, password)
        if self.token:
            print(f"Welcome, {username}!")
            return True
        else:
            print("Invalid credentials. Please try again.")
            return False
    
    def register_user(self, args):
        """Register a new user."""
        print("=== User Registration ===")
        username = input("Username: ")
        email = input("Email: ")
        password = getpass.getpass("Password: ")
        confirm_password = getpass.getpass("Confirm Password: ")
        
        if password != confirm_password:
            print("Passwords do not match!")
            return
        
        role = input("Role (user/doctor/admin) [user]: ").strip() or "user"
        if role not in ["user", "doctor", "admin"]:
            print("Invalid role. Must be user, doctor, or admin.")
            return
        
        if self.api.register_user(username, email, password, role):
            print(f"User {username} registered successfully!")
        else:
            print("Registration failed. Username may already exist.")
    
    def create_patient(self, args):
        """Create a new patient."""
        if not self.token:
            print("Please log in first.")
            return
        
        print("=== Create New Patient ===")
        
        patient_data = {}
        patient_data['first_name'] = input("First Name: ")
        patient_data['last_name'] = input("Last Name: ")
        
        dob_str = input("Date of Birth (YYYY-MM-DD): ")
        if dob_str:
            try:
                patient_data['date_of_birth'] = dob_str
            except ValueError:
                print("Invalid date format. Use YYYY-MM-DD.")
                return
        
        gender_options = [g.value for g in Gender]
        print(f"Gender options: {', '.join(gender_options)}")
        gender = input("Gender: ").lower()
        if gender in [g.value for g in Gender]:
            patient_data['gender'] = gender
        
        patient_data['phone'] = input("Phone: ")
        patient_data['email'] = input("Email: ")
        patient_data['address'] = input("Address: ")
        patient_data['emergency_contact_name'] = input("Emergency Contact Name: ")
        patient_data['emergency_contact_phone'] = input("Emergency Contact Phone: ")
        
        blood_type_options = [bt.value for bt in BloodType]
        print(f"Blood Type options: {', '.join(blood_type_options)}")
        blood_type = input("Blood Type: ")
        if blood_type in [bt.value for bt in BloodType]:
            patient_data['blood_type'] = blood_type
        
        allergies_str = input("Allergies (comma-separated): ")
        if allergies_str:
            patient_data['allergies'] = [a.strip() for a in allergies_str.split(',')]
        
        conditions_str = input("Medical Conditions (comma-separated): ")
        if conditions_str:
            patient_data['medical_conditions'] = [c.strip() for c in conditions_str.split(',')]
        
        medications_str = input("Current Medications (comma-separated): ")
        if medications_str:
            patient_data['medications'] = [m.strip() for m in medications_str.split(',')]
        
        patient_data['insurance_provider'] = input("Insurance Provider: ")
        patient_data['insurance_policy_number'] = input("Insurance Policy Number: ")
        
        patient_id = self.api.create_patient(self.token, patient_data)
        if patient_id:
            print(f"Patient created successfully! ID: {patient_id}")
        else:
            print("Failed to create patient.")
    
    def list_patients(self, args):
        """List all patients."""
        if not self.token:
            print("Please log in first.")
            return
        
        patients = self.api.list_patients(self.token, limit=args.limit if args else 100)
        if not patients:
            print("No patients found.")
            return
        
        print("\n=== Patient List ===")
        print(f"{'ID':<36} {'Name':<30} {'Age':<5} {'Phone':<15} {'Email':<30}")
        print("-" * 120)
        
        for patient in patients:
            age_str = str(patient['age']) if patient['age'] else 'N/A'
            print(f"{patient['patient_id']:<36} {patient['full_name']:<30} "
                  f"{age_str:<5} {patient['phone']:<15} {patient['email']:<30}")
    
    def get_patient(self, args):
        """Get detailed patient information."""
        if not self.token:
            print("Please log in first.")
            return
        
        patient_id = args.patient_id if args else input("Patient ID: ")
        patient = self.api.get_patient(self.token, patient_id)
        
        if not patient:
            print("Patient not found.")
            return
        
        print("\n=== Patient Details ===")
        print(f"ID: {patient['patient_id']}")
        print(f"Name: {patient['full_name']}")
        print(f"Date of Birth: {patient['date_of_birth']}")
        print(f"Age: {patient['age']}")
        print(f"Gender: {patient['gender']}")
        print(f"Phone: {patient['phone']}")
        print(f"Email: {patient['email']}")
        print(f"Address: {patient['address']}")
        print(f"Emergency Contact: {patient['emergency_contact_name']} ({patient['emergency_contact_phone']})")
        print(f"Blood Type: {patient['blood_type']}")
        print(f"Allergies: {', '.join(patient['allergies']) if patient['allergies'] else 'None'}")
        print(f"Medical Conditions: {', '.join(patient['medical_conditions']) if patient['medical_conditions'] else 'None'}")
        print(f"Medications: {', '.join(patient['medications']) if patient['medications'] else 'None'}")
        print(f"Insurance: {patient['insurance_provider']} ({patient['insurance_policy_number']})")
        print(f"Created: {patient['created_at']}")
        print(f"Updated: {patient['updated_at']}")
    
    def interactive_mode(self):
        """Run in interactive mode."""
        while True:
            if not self.token:
                if not self.login_prompt():
                    continue
            
            print("\n=== Main Menu ===")
            print("1. Create Patient")
            print("2. List Patients")
            print("3. Get Patient Details")
            print("4. Register New User")
            print("5. Logout")
            print("6. Exit")
            
            choice = input("\nSelect an option (1-6): ").strip()
            
            if choice == '1':
                self.create_patient(None)
            elif choice == '2':
                self.list_patients(None)
            elif choice == '3':
                self.get_patient(None)
            elif choice == '4':
                self.register_user(None)
            elif choice == '5':
                self.token = None
                print("Logged out successfully.")
            elif choice == '6':
                print("Goodbye!")
                break
            else:
                print("Invalid option. Please try again.")


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Medical Health Record System CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Interactive mode
    parser.add_argument('--interactive', '-i', action='store_true', 
                       help='Run in interactive mode')
    
    # Register user command
    register_parser = subparsers.add_parser('register', help='Register a new user')
    
    # Patient commands
    patient_parser = subparsers.add_parser('patient', help='Patient management commands')
    patient_subparsers = patient_parser.add_subparsers(dest='patient_command')
    
    create_patient_parser = patient_subparsers.add_parser('create', help='Create a new patient')
    
    list_patients_parser = patient_subparsers.add_parser('list', help='List all patients')
    list_patients_parser.add_argument('--limit', type=int, default=100, 
                                    help='Maximum number of patients to list')
    
    get_patient_parser = patient_subparsers.add_parser('get', help='Get patient details')
    get_patient_parser.add_argument('patient_id', help='Patient ID')
    
    args = parser.parse_args()
    
    cli = MedicalRecordsCLI()
    
    try:
        if args.interactive or not args.command:
            cli.interactive_mode()
        elif args.command == 'register':
            cli.register_user(args)
        elif args.command == 'patient':
            if args.patient_command == 'create':
                cli.create_patient(args)
            elif args.patient_command == 'list':
                cli.list_patients(args)
            elif args.patient_command == 'get':
                cli.get_patient(args)
            else:
                patient_parser.print_help()
        else:
            parser.print_help()
    except KeyboardInterrupt:
        print("\n\nOperation interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()