from odoo import models, fields

class SchoolGrade(models.Model):
    _name = 'school.grade'
    _description = 'Grade / Standard'
    _order = 'sequence, name'

    name = fields.Char(string='Grade Name', required=True) # e.g. Grade 10, Kindergarten
    code = fields.Char(string='Grade Code', required=True) # e.g. G10, KG
    sequence = fields.Integer(string='Sequence', default=10)
    description = fields.Text(string='Description')
    subject_ids = fields.Many2many('school.subject', string='Curriculum Subjects')
    class_ids = fields.One2many('school.class', 'grade_id', string='Classes / Sections')
