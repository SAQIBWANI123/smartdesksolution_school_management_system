from odoo import models, fields, api, _

class FeeHead(models.Model):
    _name = 'school.fee.head'
    _description = 'Fee Head / Type'

    name = fields.Char(string='Fee Head Name', required=True)
    code = fields.Char(string='Code', required=True)
    description = fields.Text(string='Description')


class FeeStructure(models.Model):
    _name = 'school.fee.structure'
    _description = 'Fee Structure'

    name = fields.Char(string='Structure Name', required=True)
    grade_id = fields.Many2one('school.grade', string='Grade Level', required=True)
    academic_year_id = fields.Many2one('school.academic.year', string='Academic Year', required=True)
    line_ids = fields.One2many('school.fee.structure.line', 'structure_id', string='Fee Head Lines')
    total_amount = fields.Float(string='Total Fee', compute='_compute_total_amount', store=True)

    @api.depends('line_ids.amount')
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount = sum(line.amount for line in rec.line_ids)


class FeeStructureLine(models.Model):
    _name = 'school.fee.structure.line'
    _description = 'Fee Structure Line'

    structure_id = fields.Many2one('school.fee.structure', string='Fee Structure', ondelete='cascade')
    fee_head_id = fields.Many2one('school.fee.head', string='Fee Head', required=True)
    amount = fields.Float(string='Amount', required=True, default=0.0)


class StudentFee(models.Model):
    _name = 'school.student.fee'
    _description = 'Student Fee Invoice / Statement'

    name = fields.Char(string='Invoice No', readonly=True, copy=False, default='New')
    student_id = fields.Many2one('school.student', string='Student', required=True)
    class_id = fields.Many2one('school.class', related='student_id.class_id', string='Class / Section', store=True)
    academic_year_id = fields.Many2one('school.academic.year', string='Academic Year', required=True)
    date_invoice = fields.Date(string='Invoice Date', default=fields.Date.today, required=True)
    date_due = fields.Date(string='Due Date', required=True)
    
    line_ids = fields.One2many('school.student.fee.line', 'fee_id', string='Fee Breakdown')
    
    amount_total = fields.Float(string='Total Amount', compute='_compute_amounts', store=True)
    amount_paid = fields.Float(string='Amount Paid', default=0.0)
    amount_due = fields.Float(string='Amount Due', compute='_compute_amounts', store=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted / Invoiced'),
        ('paid', 'Fully Paid'),
        ('partially_paid', 'Partially Paid'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('school.student.fee') or 'FEE/0001'
        return super(StudentFee, self).create(vals_list)

    @api.depends('line_ids.amount', 'amount_paid')
    def _compute_amounts(self):
        for rec in self:
            tot = sum(l.amount for l in rec.line_ids)
            rec.amount_total = tot
            rec.amount_due = max(tot - rec.amount_paid, 0.0)
            if rec.state in ['posted', 'paid', 'partially_paid']:
                if rec.amount_due == 0 and tot > 0:
                    rec.state = 'paid'
                elif rec.amount_paid > 0 and rec.amount_due > 0:
                    rec.state = 'partially_paid'

    def action_post(self):
        self.write({'state': 'posted'})

    def action_register_payment(self):
        self.ensure_one()
        self.write({
            'amount_paid': self.amount_total,
            'state': 'paid'
        })


class StudentFeeLine(models.Model):
    _name = 'school.student.fee.line'
    _description = 'Student Fee Line Item'

    fee_id = fields.Many2one('school.student.fee', string='Student Fee Invoice', ondelete='cascade')
    fee_head_id = fields.Many2one('school.fee.head', string='Fee Head', required=True)
    amount = fields.Float(string='Amount', required=True, default=0.0)
    remarks = fields.Char(string='Remarks')
