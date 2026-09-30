{
    "name": "Clinic Management",
    "version": "19.0.1.0.0",
    "summary": "Manage patients, doctors, and appointments",
    "depends": ["base", "contacts", "mail"],
    "data": [
    "security/clinic_security.xml",
    "security/ir.model.access.csv",

    "views/clinic_patient_view.xml",
    "views/clinic_doctor_view.xml",
    "views/clinic_appointment_view.xml",
],
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}
