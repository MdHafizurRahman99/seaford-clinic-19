from odoo import fields, models

from .weekly_availability import USER_WEEKLY_AVAILABILITY_FIELDS


class ResUsers(models.Model):
    _inherit = 'res.users'

    weekly_availability_line_ids = fields.One2many(
        related='employee_id.weekly_availability_line_ids',
        readonly=False,
        related_sudo=False,
        string='Weekly Availability',
    )

    def _get_employee_fields_to_sync(self):
        return super()._get_employee_fields_to_sync() + USER_WEEKLY_AVAILABILITY_FIELDS

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + USER_WEEKLY_AVAILABILITY_FIELDS

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + USER_WEEKLY_AVAILABILITY_FIELDS
