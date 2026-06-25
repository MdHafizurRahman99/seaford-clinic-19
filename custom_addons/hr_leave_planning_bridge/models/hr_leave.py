# -*- coding: utf-8 -*-

from odoo import fields, models


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    planning_slot_id = fields.Many2one(
        'planning.slot',
        string='Planning Slot',
        copy=False,
        help='Planning shift linked to this leave request.',
    )
    planning_slot_title = fields.Char(
        string='Planning Slot Title',
        copy=False,
        help='Snapshot of the planning slot title at the time the leave request was submitted.',
    )
    planning_role_name = fields.Char(
        string='Planning Role',
        copy=False,
        help='Snapshot of the planning role at the time the leave request was submitted.',
    )
    planning_company_name = fields.Char(
        string='Planning Company',
        copy=False,
        help='Snapshot of the planning company at the time the leave request was submitted.',
    )
    planning_start_datetime = fields.Datetime(
        string='Planning Start',
        copy=False,
        help='Snapshot of the planned shift start datetime in UTC.',
    )
    planning_end_datetime = fields.Datetime(
        string='Planning End',
        copy=False,
        help='Snapshot of the planned shift end datetime in UTC.',
    )
