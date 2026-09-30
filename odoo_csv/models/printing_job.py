from odoo import models, fields


class PrintingJob(models.Model):
    _name = 'printing.job'
    _description = 'Printing Job'

    job_id = fields.Char(
        string='Job ID',
        required=True
        
    )

    job_name = fields.Char(
        string='Job Name'
        
    )

    job_comment = fields.Text(
        string='Job Comment'
        
    )

    owner_name = fields.Char(
        string='Owner Name'
        
    )

    hostname = fields.Char(
        string='Hostname'
    )

    document_pages = fields.Integer(
        string='Document Pages'
       
    )

    original_size = fields.Char(
        string='Original Size'
       
    )

    final_status = fields.Char(
        string='Final Status'
        
    )

    error = fields.Text(
        string='Error'
    )

    job_type = fields.Char(
        string='Job Type'
    )

    job_category = fields.Char(
        string='Job Category'
    )

    print_mode = fields.Char(
        string='Print Mode'
    )

    print_duration = fields.Float(
        string='Print Duration'
    )

    print_speed = fields.Float(
        string='Print Speed'
    )

    printed_pages = fields.Integer(
        string='Printed Pages'
    )

    printed_copies = fields.Integer(
        string='Printed Copies'
    )

    total_pages = fields.Integer(
        string='Total Pages'
    )

    paper_name = fields.Char(
        string='Paper Name'
    )

    paper_type = fields.Char(
        string='Paper Type'
    )

    total_ink_usage = fields.Float(
        string='Total Ink Usage'
    )

    cyan_ink_usage = fields.Float(
        string='Cyan Ink Usage'
    )

    magenta_ink_usage = fields.Float(
        string='Magenta Ink Usage'
    )

    yellow_ink_usage = fields.Float(
        string='Yellow Ink Usage'
    )

    black_ink_usage = fields.Float(
        string='Black Ink Usage'
    )

    stop_count = fields.Integer(
        string='Stop Count'
    )