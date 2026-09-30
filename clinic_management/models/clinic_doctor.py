from odoo import models, fields


class ClinicDoctor(models.Model):
    _name = 'clinic.doctor'
    _description = 'Clinic Doctor'

    name = fields.Char(string='Name', required=True)
    specialization = fields.Char(string='Specialization', required=True)
    phone_number = fields.Char(string='Phone Number', required=True)

    # Relationships
    appointment_ids = fields.One2many(
        "clinic.appointment",
        "doctor_id",
        string="Appointments"
    )
