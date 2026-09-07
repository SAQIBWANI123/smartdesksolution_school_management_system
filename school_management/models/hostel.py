from odoo import models, fields, api

class HostelBuilding(models.Model):
    _name = 'school.hostel.building'
    _description = 'Hostel Building / Block'

    name = fields.Char(string='Building / Block Name', required=True) # e.g. Boys Hostel - Block A
    code = fields.Char(string='Code', required=True)
    type = fields.Selection([
        ('boys', 'Boys Hostel'),
        ('girls', 'Girls Hostel'),
        ('staff', 'Staff Quarters')
    ], string='Hostel Type', default='boys', required=True)
    warden_name = fields.Char(string='Warden Name')
    warden_phone = fields.Char(string='Warden Contact')
    room_ids = fields.One2many('school.hostel.room', 'building_id', string='Rooms')


class HostelRoom(models.Model):
    _name = 'school.hostel.room'
    _description = 'Hostel Room'

    name = fields.Char(string='Room Number', required=True)
    building_id = fields.Many2one('school.hostel.building', string='Hostel Building', required=True, ondelete='cascade')
    capacity = fields.Integer(string='Bed Capacity', default=2)
    monthly_rent = fields.Float(string='Monthly Rent', required=True, default=0.0)
    allocation_ids = fields.One2many('school.hostel.allocation', 'room_id', string='Allocated Students')
    occupied_count = fields.Integer(string='Occupied Beds', compute='_compute_occupied', store=True)

    @api.depends('allocation_ids.state')
    def _compute_occupied(self):
        for rec in self:
            rec.occupied_count = len(rec.allocation_ids.filtered(lambda a: a.state == 'active'))


class HostelAllocation(models.Model):
    _name = 'school.hostel.allocation'
    _description = 'Hostel Bed Allocation'

    student_id = fields.Many2one('school.student', string='Student', required=True)
    room_id = fields.Many2one('school.hostel.room', string='Hostel Room', required=True)
    date_allocated = fields.Date(string='Allocation Date', default=fields.Date.today)
    state = fields.Selection([
        ('active', 'Active'),
        ('vacated', 'Vacated')
    ], string='Status', default='active')
