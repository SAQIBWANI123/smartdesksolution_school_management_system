from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SchoolAttendance(models.Model):
    _name = 'school.attendance'
    _description = 'Class Attendance Register'
    _order = 'date desc, class_id'

    name = fields.Char(string='Reference', compute='_compute_name', store=True)
    date = fields.Date(string='Attendance Date', default=fields.Date.today, required=True)
    class_id = fields.Many2one('school.class', string='Class / Section', required=True)
    teacher_id = fields.Many2one('school.teacher', string='Teacher / Staff', required=True)
    line_ids = fields.One2many('school.attendance.line', 'attendance_id', string='Student Attendance Records')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Submitted'),
    ], string='Status', default='draft', required=True)

    present_count = fields.Integer(string='Present Count', compute='_compute_counts')
    absent_count = fields.Integer(string='Absent Count', compute='_compute_counts')

    @api.depends('class_id.name', 'date')
    def _compute_name(self):
        for rec in self:
            if rec.class_id and rec.date:
                rec.name = f"Attendance: {rec.class_id.name} ({rec.date})"
            else:
                rec.name = "New Attendance Record"

    @api.depends('line_ids.state')
    def _compute_counts(self):
        for rec in self:
            rec.present_count = len(rec.line_ids.filtered(lambda l: l.state in ['present', 'late']))
            rec.absent_count = len(rec.line_ids.filtered(lambda l: l.state == 'absent'))

    def action_load_students(self):
        self.ensure_one()
        if not self.class_id:
            raise UserError(_("Please select a Class first."))
        self.line_ids.unlink()
        lines = []
        for student in self.class_id.student_ids:
            lines.append((0, 0, {
                'student_id': student.id,
                'state': 'present',
            }))
        self.write({'line_ids': lines})

    def action_submit(self):
        self.write({'state': 'done'})


class SchoolAttendanceLine(models.Model):
    _name = 'school.attendance.line'
    _description = 'Student Attendance Line'

    attendance_id = fields.Many2one('school.attendance', string='Attendance Register', ondelete='cascade')
    student_id = fields.Many2one('school.student', string='Student', required=True)
    roll_number = fields.Char(related='student_id.roll_number', string='Roll No')
    state = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    ], string='Attendance Status', default='present', required=True)
    remarks = fields.Char(string='Remarks')
