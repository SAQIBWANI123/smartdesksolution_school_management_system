from odoo import models, fields, api


class SchoolStudent(models.Model):
    _name = 'school.student'
    _description = 'Student'
    _order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Student Name', required=True, tracking=True)
    student_id_code = fields.Char(string='Registration ID', copy=False, readonly=True, default='New')
    roll_number = fields.Char(string='Roll Number')
    date_of_birth = fields.Date(string='Date of Birth', required=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Gender', default='male', required=True)
    blood_group = fields.Selection([
        ('a+', 'A+'), ('a-', 'A-'),
        ('b+', 'B+'), ('b-', 'B-'),
        ('ab+', 'AB+'), ('ab-', 'AB-'),
        ('o+', 'O+'), ('o-', 'O-')
    ], string='Blood Group')
    admission_date = fields.Date(string='Admission Date', default=fields.Date.today)

    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone / Mobile')
    street = fields.Char(string='Street Address')
    street2 = fields.Char(string='Street Address 2')
    city = fields.Char(string='City')
    state_id = fields.Many2one('res.country.state', string='State')
    zip = fields.Char(string='ZIP Code')
    country_id = fields.Many2one('res.country', string='Country')
    image_1920 = fields.Image(string='Student Photo')

    grade_id = fields.Many2one('school.grade', string='Grade Level', required=True, tracking=True)
    class_id = fields.Many2one('school.class', string='Class / Section',
                               domain="[('grade_id', '=', grade_id)]")
    academic_year_id = fields.Many2one('school.academic.year', string='Academic Year')

    parent_ids = fields.Many2many('school.parent', string='Parents / Guardians')
    primary_parent_id = fields.Many2one('school.parent', string='Primary Guardian')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('enrolled', 'Enrolled'),
        ('promoted', 'Promoted'),
        ('graduated', 'Graduated'),
        ('suspended', 'Suspended'),
    ], string='Status', default='draft', tracking=True)

    medical_notes = fields.Text(string='Medical Notes / Allergies')

    # Computed metrics for smart buttons
    attendance_percentage = fields.Float(
        string='Attendance %', compute='_compute_student_stats')
    total_fee_due = fields.Float(
        string='Fee Balance Due', compute='_compute_student_stats')
    books_borrowed_count = fields.Integer(
        string='Books Borrowed', compute='_compute_student_stats')
    exam_results_count = fields.Integer(
        string='Exam Results', compute='_compute_student_stats')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('student_id_code', 'New') == 'New':
                vals['student_id_code'] = (
                    self.env['ir.sequence'].next_by_code('school.student') or 'STU/0001'
                )
        return super().create(vals_list)

    def action_enroll(self):
        self.write({'state': 'enrolled'})

    def action_promote(self):
        self.write({'state': 'promoted'})

    def action_graduate(self):
        self.write({'state': 'graduated'})

    def action_suspend(self):
        self.write({'state': 'suspended'})

    def action_view_attendance(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Attendance',
            'res_model': 'school.attendance.line',
            'view_mode': 'list',
            'domain': [('student_id', '=', self.id)],
        }

    def action_view_fees(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Fee Statements',
            'res_model': 'school.student.fee',
            'view_mode': 'list,form',
            'domain': [('student_id', '=', self.id)],
            'context': {'default_student_id': self.id},
        }

    def action_view_books(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Books Issued',
            'res_model': 'school.library.issue',
            'view_mode': 'list,form',
            'domain': [('student_id', '=', self.id), ('state', '=', 'issued')],
        }

    def action_view_exam_results(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Exam Results',
            'res_model': 'school.exam.result',
            'view_mode': 'list,form',
            'domain': [('student_id', '=', self.id)],
        }

    def _compute_student_stats(self):
        for student in self:
            # Attendance
            att_lines = self.env['school.attendance.line'].search(
                [('student_id', '=', student.id)])
            if att_lines:
                present = len(att_lines.filtered(
                    lambda l: l.state in ['present', 'late']))
                student.attendance_percentage = (present / len(att_lines)) * 100.0
            else:
                student.attendance_percentage = 100.0

            # Fee Due
            fees = self.env['school.student.fee'].search(
                [('student_id', '=', student.id)])
            student.total_fee_due = sum(f.amount_due for f in fees)

            # Books Borrowed
            issues = self.env['school.library.issue'].search([
                ('student_id', '=', student.id), ('state', '=', 'issued')
            ])
            student.books_borrowed_count = len(issues)

            # Exam Results
            results = self.env['school.exam.result'].search(
                [('student_id', '=', student.id)])
            student.exam_results_count = len(results)
