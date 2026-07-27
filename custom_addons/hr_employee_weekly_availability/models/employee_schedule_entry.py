from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


SCHEDULE_ENTRY_TYPE_SELECTION = [
    ('available', 'Available'),
    ('unavailable', 'Unavailable'),
    ('note', 'Note / Preference'),
]


class HrEmployeeScheduleEntry(models.Model):
    _name = 'hr.employee.schedule.entry'
    _description = 'Employee Schedule Diary Entry'
    _order = 'entry_date, is_full_day desc, start_time, employee_id, id'
    _rec_name = 'summary'

    employee_id = fields.Many2one(
        'hr.employee',
        required=True,
        ondelete='cascade',
        index=True,
        default=lambda self: self.env.user.employee_id,
    )
    entry_date = fields.Date(required=True, index=True)
    entry_type = fields.Selection(
        SCHEDULE_ENTRY_TYPE_SELECTION,
        required=True,
        default='available',
        index=True,
    )
    title = fields.Char(size=120)
    note = fields.Text()
    is_full_day = fields.Boolean(default=True)
    start_time = fields.Float(string='From')
    end_time = fields.Float(string='To')
    time_range_display = fields.Char(compute='_compute_labels', store=True)
    summary = fields.Char(compute='_compute_labels', store=True)
    active = fields.Boolean(default=True)

    @staticmethod
    def _format_float_time(value):
        total_minutes = round(value * 60)
        hours, minutes = divmod(total_minutes, 60)
        return f'{hours:02d}:{minutes:02d}'

    @api.depends('entry_date', 'entry_type', 'title', 'is_full_day', 'start_time', 'end_time')
    def _compute_labels(self):
        type_labels = dict(SCHEDULE_ENTRY_TYPE_SELECTION)
        for entry in self:
            if entry.is_full_day:
                time_label = _('All day')
            else:
                time_label = _(
                    '%(start)s to %(end)s',
                    start=entry._format_float_time(entry.start_time),
                    end=entry._format_float_time(entry.end_time),
                )
            type_label = type_labels.get(entry.entry_type, '')
            entry.time_range_display = time_label
            entry.summary = _(
                '%(date)s | %(entry_type)s | %(title)s | %(time)s',
                date=fields.Date.to_string(entry.entry_date) if entry.entry_date else '',
                entry_type=type_label,
                title=entry.title or type_label,
                time=time_label,
            )

    @api.constrains('is_full_day', 'start_time', 'end_time')
    def _check_time_values(self):
        for entry in self:
            if entry.is_full_day:
                continue
            if not 0 <= entry.start_time < 24:
                raise ValidationError(_('The start time must be between 00:00 and 23:59.'))
            if not 0 < entry.end_time <= 24:
                raise ValidationError(_('The end time must be between 00:01 and 24:00.'))
            if entry.start_time >= entry.end_time:
                raise ValidationError(_('The end time must be later than the start time.'))

    @api.constrains('entry_type', 'title', 'note')
    def _check_note_content(self):
        for entry in self:
            if entry.entry_type == 'note' and not (entry.title or entry.note):
                raise ValidationError(_('A note entry requires a title or details.'))


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    schedule_entry_ids = fields.One2many(
        'hr.employee.schedule.entry',
        'employee_id',
        string='Schedule Diary',
    )


class ResUsers(models.Model):
    _inherit = 'res.users'

    schedule_entry_ids = fields.One2many(
        related='employee_id.schedule_entry_ids',
        readonly=False,
        related_sudo=False,
        string='Schedule Diary',
    )

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ['schedule_entry_ids']

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + ['schedule_entry_ids']
