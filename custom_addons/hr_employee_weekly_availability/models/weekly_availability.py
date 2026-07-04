from collections import defaultdict

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

WEEKDAY_SELECTION = [
    ('0', 'Monday'),
    ('1', 'Tuesday'),
    ('2', 'Wednesday'),
    ('3', 'Thursday'),
    ('4', 'Friday'),
    ('5', 'Saturday'),
    ('6', 'Sunday'),
]

AVAILABILITY_TYPE_SELECTION = [
    ('available', 'Available'),
    ('unavailable', 'Unavailable'),
]

USER_WEEKLY_AVAILABILITY_FIELDS = ['weekly_availability_line_ids']


class HrEmployeeWeeklyAvailability(models.Model):
    _name = 'hr.employee.weekly.availability'
    _description = 'Employee Weekly Availability'
    _order = 'day_of_week, sequence, start_time, end_time, id'
    _rec_name = 'summary'

    employee_id = fields.Many2one(
        'hr.employee',
        required=True,
        ondelete='cascade',
        default=lambda self: self.env.user.employee_id,
    )
    sequence = fields.Integer(default=10)
    day_of_week = fields.Selection(WEEKDAY_SELECTION, required=True, default='0', string='Weekday')
    availability_type = fields.Selection(
        AVAILABILITY_TYPE_SELECTION,
        required=True,
        default='available',
        string='Entry Type',
    )
    is_full_day = fields.Boolean(string='Full Day')
    start_time = fields.Float(string='From')
    end_time = fields.Float(string='To')
    time_range_display = fields.Char(compute='_compute_labels', store=True, string='Time Range')
    summary = fields.Char(compute='_compute_labels', store=True)

    @staticmethod
    def _format_float_time(value):
        total_minutes = round(value * 60)
        hours, minutes = divmod(total_minutes, 60)
        return f'{hours:02d}:{minutes:02d}'

    @api.depends('day_of_week', 'availability_type', 'is_full_day', 'start_time', 'end_time')
    def _compute_labels(self):
        weekday_labels = dict(WEEKDAY_SELECTION)
        type_labels = dict(AVAILABILITY_TYPE_SELECTION)
        for line in self:
            day_label = weekday_labels.get(line.day_of_week, '')
            type_label = type_labels.get(line.availability_type, '')
            if line.is_full_day:
                time_label = _('Full day')
            else:
                time_label = _('%(start)s to %(end)s',
                    start=line._format_float_time(line.start_time),
                    end=line._format_float_time(line.end_time),
                )
            line.time_range_display = time_label
            line.summary = _('%(day)s | %(entry_type)s | %(time)s',
                day=day_label,
                entry_type=type_label,
                time=time_label,
            )

    @api.constrains('is_full_day', 'start_time', 'end_time')
    def _check_time_values(self):
        for line in self:
            if line.is_full_day:
                continue
            if not 0 <= line.start_time < 24:
                raise ValidationError(_('The start time must be between 00:00 and 23:59.'))
            if not 0 < line.end_time <= 24:
                raise ValidationError(_('The end time must be between 00:01 and 24:00.'))
            if line.start_time >= line.end_time:
                raise ValidationError(_('The end time must be later than the start time.'))

    @api.constrains('employee_id', 'day_of_week', 'availability_type', 'is_full_day', 'start_time', 'end_time')
    def _check_schedule_conflicts(self):
        line_ids_by_employee = defaultdict(set)
        for line in self:
            if line.employee_id:
                line_ids_by_employee[line.employee_id.id].add(line.id)

        for employee_id in line_ids_by_employee:
            employee = self.env['hr.employee'].browse(employee_id)
            grouped_lines = defaultdict(lambda: self.env['hr.employee.weekly.availability'])
            for line in employee.weekly_availability_line_ids:
                grouped_lines[(line.day_of_week, line.availability_type)] |= line

            for (day_of_week, availability_type), lines in grouped_lines.items():
                day_label = dict(WEEKDAY_SELECTION)[day_of_week]
                type_label = dict(AVAILABILITY_TYPE_SELECTION)[availability_type]
                full_day_lines = lines.filtered('is_full_day')
                timed_lines = lines - full_day_lines

                if len(full_day_lines) > 1:
                    raise ValidationError(_(
                        'You can only have one full-day %(entry_type)s entry on %(day)s.',
                        entry_type=type_label.lower(),
                        day=day_label,
                    ))
                if full_day_lines and timed_lines:
                    raise ValidationError(_(
                        'You cannot mix a full-day %(entry_type)s entry with timed %(entry_type)s entries on %(day)s.',
                        entry_type=type_label.lower(),
                        day=day_label,
                    ))

                previous_line = False
                for line in timed_lines.sorted(lambda record: (record.start_time, record.end_time, record.id)):
                    if previous_line and line.start_time < previous_line.end_time:
                        raise ValidationError(_(
                            'Timed %(entry_type)s entries overlap on %(day)s.',
                            entry_type=type_label.lower(),
                            day=day_label,
                        ))
                    previous_line = line

            for day_of_week, day_label in WEEKDAY_SELECTION:
                day_lines = employee.weekly_availability_line_ids.filtered(lambda line: line.day_of_week == day_of_week)
                has_available_full_day = bool(day_lines.filtered(
                    lambda line: line.availability_type == 'available' and line.is_full_day
                ))
                has_unavailable_full_day = bool(day_lines.filtered(
                    lambda line: line.availability_type == 'unavailable' and line.is_full_day
                ))
                if has_available_full_day and has_unavailable_full_day:
                    raise ValidationError(_(
                        'You cannot mark %(day)s as both full-day available and full-day unavailable.',
                        day=day_label,
                    ))
