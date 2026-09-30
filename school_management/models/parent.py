from odoo import models, fields

class SchoolParent(models.Model):
    _name = 'school.parent'
    _description = 'Parent / Guardian'
    _order = 'name'

    name = fields.Char(string='Guardian Name', required=True)
    relation_type = fields.Selection([
        ('father', 'Father'),
        ('mother', 'Mother'),
        ('guardian', 'Legal Guardian'),
    ], string='Relation Type', default='father', required=True)
    occupation = fields.Char(string='Occupation')
    annual_income = fields.Float(string='Annual Income')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    mobile = fields.Char(string='Mobile')
    student_ids = fields.Many2many('school.student', string='Children / Wards')
    emergency_contact = fields.Boolean(string='Is Emergency Contact', default=True)
