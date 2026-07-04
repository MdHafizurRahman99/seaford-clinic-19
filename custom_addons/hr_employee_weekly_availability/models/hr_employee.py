from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    weekly_availability_line_ids = fields.One2many(
        'hr.employee.weekly.availability',
        'employee_id',
        string='Weekly Availability',
    )
