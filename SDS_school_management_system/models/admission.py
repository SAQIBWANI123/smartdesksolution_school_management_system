from odoo import api, fields, models


class SchoolAdmission(models.Model):
    _name = 'school.admission'
    _description = 'School Admission Application'
    _order = 'create_date desc'

    name = fields.Char(string='Application Number', readonly=True, copy=False, default='New')
    student_name = fields.Char(required=True)
    date_of_birth = fields.Date(required=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Other')], required=True)
    grade_id = fields.Many2one('school.grade', string='Grade Applying For', required=True)
    academic_year_id = fields.Many2one('school.academic.year', string='Academic Year')
    guardian_name = fields.Char(required=True)
    guardian_relation = fields.Char(string='Relationship')
    guardian_email = fields.Char(required=True)
    guardian_phone = fields.Char(required=True)
    address = fields.Text()
    document_ids = fields.Many2many('ir.attachment', string='Documents')
    notes = fields.Text()
    state = fields.Selection([
        ('new', 'New'), ('review', 'Under Review'), ('approved', 'Approved'), ('rejected', 'Rejected'),
    ], default='new', required=True)
    student_id = fields.Many2one('school.student', readonly=True, copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('school.admission') or 'ADM/0001'
        return super().create(vals_list)

    def action_review(self):
        self.write({'state': 'review'})

    def action_approve(self):
        for admission in self:
            if not admission.student_id:
                parent = self.env['school.parent'].search([('email', '=', admission.guardian_email)], limit=1)
                if not parent:
                    parent = self.env['school.parent'].create({
                        'name': admission.guardian_name, 'email': admission.guardian_email,
                        'phone': admission.guardian_phone,
                    })
                student = self.env['school.student'].create({
                    'name': admission.student_name, 'date_of_birth': admission.date_of_birth,
                    'gender': admission.gender, 'grade_id': admission.grade_id.id,
                    'academic_year_id': admission.academic_year_id.id,
                    'email': admission.guardian_email, 'phone': admission.guardian_phone,
                    'street': admission.address, 'parent_ids': [(6, 0, [parent.id])],
                    'primary_parent_id': parent.id, 'state': 'enrolled',
                })
                admission.student_id = student
            admission.state = 'approved'

    def action_reject(self):
        self.write({'state': 'rejected'})
