from odoo import models, fields, api, _

class LibraryBook(models.Model):
    _name = 'school.library.book'
    _description = 'Library Book Catalog'

    name = fields.Char(string='Book Title', required=True)
    code = fields.Char(string='Book Code / Call No', readonly=True, copy=False, default='New')
    isbn = fields.Char(string='ISBN No')
    author = fields.Char(string='Author(s)', required=True)
    publisher = fields.Char(string='Publisher')
    edition = fields.Char(string='Edition / Year')
    category = fields.Selection([
        ('textbook', 'Textbook'),
        ('reference', 'Reference Book'),
        ('fiction', 'Fiction'),
        ('nonfiction', 'Non-Fiction'),
        ('journal', 'Journal / Magazine')
    ], string='Category', default='textbook', required=True)
    total_copies = fields.Integer(string='Total Copies', default=1, required=True)
    available_copies = fields.Integer(string='Available Copies', compute='_compute_available_copies', store=True)
    issue_ids = fields.One2many('school.library.issue', 'book_id', string='Issue Records')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', 'New') == 'New':
                vals['code'] = self.env['ir.sequence'].next_by_code('school.library.book') or 'BK/00001'
        return super(LibraryBook, self).create(vals_list)

    @api.depends('total_copies', 'issue_ids.state')
    def _compute_available_copies(self):
        for rec in self:
            issued = len(rec.issue_ids.filtered(lambda i: i.state == 'issued'))
            rec.available_copies = max(rec.total_copies - issued, 0)


class LibraryIssue(models.Model):
    _name = 'school.library.issue'
    _description = 'Library Book Issue Record'

    name = fields.Char(string='Issue Ref', readonly=True, copy=False, default='New')
    book_id = fields.Many2one('school.library.book', string='Book Title', required=True)
    student_id = fields.Many2one('school.student', string='Student', required=True)
    class_id = fields.Many2one('school.class', related='student_id.class_id', string='Class / Section', store=True)
    date_issue = fields.Date(string='Issue Date', default=fields.Date.today, required=True)
    date_due = fields.Date(string='Due Date', required=True)
    date_return = fields.Date(string='Return Date')
    
    state = fields.Selection([
        ('issued', 'Issued'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    ], string='Status', default='issued', required=True)
    
    fine_amount = fields.Float(string='Late Fine Amount', default=0.0)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('school.library.issue') or 'ISS/0001'
        return super(LibraryIssue, self).create(vals_list)

    def action_return_book(self):
        self.ensure_one()
        self.write({
            'date_return': fields.Date.today(),
            'state': 'returned'
        })
