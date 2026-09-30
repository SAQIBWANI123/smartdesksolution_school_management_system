from odoo import fields, models


class ExampleModel(models.Model):
    _name = "example.model"
    _description = "Example Model"

    name = fields.Char(string="Name", required=True)
    user_id = fields.Many2one("res.users", string="User")
