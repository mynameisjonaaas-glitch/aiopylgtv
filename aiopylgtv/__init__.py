from .lut_tools import (
    create_dolby_vision_config,
    read_cal_file,
    read_cube_file,
    unity_lut_1d,
    unity_lut_3d,
    write_dolby_vision_config,
)
from .webos_client import PyLGTVCmdException, PyLGTVPairException, WebOsClient

# Medical records system (optional import)
try:
    from .medical_records import (
        Patient,
        MedicalRecord,
        Appointment,
        Doctor,
        HealthRecordDB,
        HealthRecordAPI,
        AuthManager,
    )
    _medical_records_available = True
except ImportError:
    _medical_records_available = False

__all__ = [
    "create_dolby_vision_config",
    "read_cal_file",
    "read_cube_file",
    "unity_lut_1d",
    "unity_lut_3d",
    "write_dolby_vision_config",
    "PyLGTVCmdException",
    "PyLGTVPairException",
    "WebOsClient",
]

if _medical_records_available:
    __all__.extend([
        "Patient",
        "MedicalRecord",
        "Appointment",
        "Doctor",
        "HealthRecordDB",
        "HealthRecordAPI",
        "AuthManager",
    ])
