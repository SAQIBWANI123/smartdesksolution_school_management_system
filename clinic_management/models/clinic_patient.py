from odoo import models, fields


class ClinicPatient(models.Model):
    _name = "clinic.patient"
    _description = "Clinic Patient"

    patient_id = fields.Char(string="Patient ID", copy=False, readonly=True, default="New")
    name = fields.Char(string="Name", required=True)
    age = fields.Integer(string="Age")
    phone_number = fields.Char(string="Phone Number")
    address = fields.Text(string="Address")

    # Relationships
    appointment_ids = fields.One2many(
        "clinic.appointment",
        "patient_id",
        string="Appointments"
    )
