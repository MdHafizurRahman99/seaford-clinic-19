from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    weekly_availability_line_ids = fields.One2many(
        related='employee_id.weekly_availability_line_ids',
        readonly=False,
        related_sudo=False,
        string='Weekly Availability',
    )

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ['weekly_availability_line_ids']

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + ['weekly_availability_line_ids']
