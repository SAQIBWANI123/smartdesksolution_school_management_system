from odoo import models, fields


class ClinicAppointment(models.Model):
    _name = 'clinic.appointment'
    _description = 'Clinic Appointment'

    name = fields.Char(string='Reference', copy=False, readonly=True, default='New')
    appointment_date = fields.Datetime(string='Appointment Date', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft')
    notes = fields.Text(string='Notes')

    patient_id = fields.Many2one(
        "clinic.patient",
        string="Patient",
        required=True
    )
    doctor_id = fields.Many2one(
        "clinic.doctor",
        string="Doctor",
        required=True
    )
