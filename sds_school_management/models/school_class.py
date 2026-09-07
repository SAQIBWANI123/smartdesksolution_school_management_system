from odoo import models, fields, api

class SchoolClass(models.Model):
    _name = 'school.class'
    _description = 'Class / Section'

    name = fields.Char(string='Class Name', compute='_compute_name', store=True)
    grade_id = fields.Many2one('school.grade', string='Grade Level', required=True)
    section = fields.Char(string='Section', required=True, default='A')
    academic_year_id = fields.Many2one('school.academic.year', string='Academic Year', required=True)
    class_teacher_id = fields.Many2one('school.teacher', string='Class Teacher')
    room_number = fields.Char(string='Room / Hall Number')
    capacity = fields.Integer(string='Class Capacity', default=30)
    student_ids = fields.One2many('school.student', 'class_id', string='Enrolled Students')
    student_count = fields.Integer(string='Total Students', compute='_compute_student_count', store=True)
    subject_allocation_ids = fields.One2many('school.subject.allocation', 'class_id', string='Subject Allocations')

    @api.depends('grade_id.name', 'section', 'academic_year_id.name')
    def _compute_name(self):
        for rec in self:
            if rec.grade_id and rec.section:
                year = f" ({rec.academic_year_id.name})" if rec.academic_year_id else ""
                rec.name = f"{rec.grade_id.name} - {rec.section}{year}"
            else:
                rec.name = "New Class"

    @api.depends('student_ids')
    def _compute_student_count(self):
        for rec in self:
            rec.student_count = len(rec.student_ids)
