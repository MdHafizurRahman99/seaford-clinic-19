from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PlanningSlot(models.Model):
    _inherit = 'planning.slot'

    ems_publish_state = fields.Selection([
        ('unpublished', 'Unpublished'), ('published', 'Published'), ('updated', 'Updated'),
    ], default='unpublished', required=True, index=True)
    ems_published_at = fields.Datetime()
    ems_published_by = fields.Many2one('res.users', ondelete='set null')
    ems_requires_confirmation = fields.Boolean(default=False)
    ems_confirmation_status = fields.Selection([
        ('not_required', 'Not Required'), ('pending', 'Pending'),
        ('accepted', 'Accepted'), ('declined', 'Declined'),
    ], default='not_required', required=True, index=True)
    ems_confirmation_note = fields.Text()
    ems_confirmation_responded_at = fields.Datetime()
    ems_confirmation_responded_by = fields.Many2one('res.users', ondelete='set null')
    ems_was_open_shift_claim = fields.Boolean(default=False)
    ems_claimed_at = fields.Datetime()
    ems_claimed_by = fields.Many2one('res.users', ondelete='set null')
    ems_notification_mode = fields.Char()
    ems_notification_status = fields.Selection([
        ('not_requested', 'Not Requested'), ('pending', 'Pending'),
        ('delivered', 'Delivered'), ('failed', 'Failed'), ('unavailable', 'Unavailable'),
    ], default='not_requested', required=True)
    ems_notification_sent_at = fields.Datetime()
    ems_reminder_sent_at = fields.Datetime()
    ems_notification_error = fields.Text()
    ems_work_location_id = fields.Many2one(
        'hr.work.location',
        string='Scheduled Work Location',
        ondelete='restrict',
        check_company=True,
        index=True,
        help='Physical work location selected for this shift. It remains available on open shifts.',
    )

    def write(self, vals):
        schedule_fields = {'start_datetime', 'end_datetime', 'resource_id', 'employee_id', 'role_id', 'company_id', 'name', 'ems_work_location_id'}
        mark_updated = not self.env.context.get('skip_ems_publish_state') and bool(schedule_fields.intersection(vals))
        result = super().write(vals)
        if mark_updated:
            published = self.filtered(lambda slot: slot.ems_publish_state == 'published')
            if published:
                published.with_context(skip_ems_publish_state=True).write({'ems_publish_state': 'updated'})
        return result

    @api.model_create_multi
    def create(self, vals_list):
        slots = super().create(vals_list)
        for slot, vals in zip(slots, vals_list):
            if not vals.get('ems_work_location_id') and slot.employee_id.work_location_id:
                slot.with_context(skip_ems_publish_state=True).ems_work_location_id = slot.employee_id.work_location_id
        return slots

    @api.constrains('company_id', 'ems_work_location_id')
    def _check_ems_work_location_company(self):
        for slot in self:
            if slot.ems_work_location_id and slot.ems_work_location_id.company_id != slot.company_id:
                raise ValidationError(_('The scheduled work location must belong to the shift company.'))


class EmsScheduleTemplate(models.Model):
    _name = 'ems.schedule.template'
    _description = 'EMS Schedule Template'
    _order = 'name, id'

    name = fields.Char(required=True)
    description = fields.Text()
    company_id = fields.Many2one('res.company', required=True, index=True, default=lambda self: self.env.company)
    item_ids = fields.One2many('ems.schedule.template.item', 'template_id')
    last_applied_at = fields.Datetime()
    last_applied_by = fields.Many2one('res.users', ondelete='set null')
    active = fields.Boolean(default=True)


class EmsScheduleTemplateItem(models.Model):
    _name = 'ems.schedule.template.item'
    _description = 'EMS Schedule Template Item'
    _order = 'day_offset, start_time, id'

    template_id = fields.Many2one('ems.schedule.template', required=True, ondelete='cascade', index=True)
    company_id = fields.Many2one(related='template_id.company_id', store=True, index=True)
    day_offset = fields.Integer(required=True)
    employee_id = fields.Many2one('hr.employee', ondelete='set null')
    role_id = fields.Many2one('planning.role', required=True, ondelete='restrict')
    work_location_id = fields.Many2one('hr.work.location', ondelete='restrict', check_company=True)
    start_time = fields.Float(required=True)
    end_time = fields.Float(required=True)
    title = fields.Char()
    note = fields.Text()

    @api.constrains('day_offset', 'start_time', 'end_time')
    def _check_values(self):
        for item in self:
            if item.day_offset < 0 or item.day_offset > 6:
                raise ValidationError(_('Template day offset must be between 0 and 6.'))
            if not 0 <= item.start_time < item.end_time <= 24:
                raise ValidationError(_('Template start and end times are invalid.'))


class EmsScheduleArea(models.Model):
    _name = 'ems.schedule.area'
    _description = 'EMS Scheduling Area'
    _order = 'sequence, name, id'

    name = fields.Char(required=True)
    company_id = fields.Many2one('res.company', required=True, index=True, default=lambda self: self.env.company)
    role_id = fields.Many2one('planning.role', required=True, ondelete='restrict', index=True)
    color = fields.Char(default='#176b5b', required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    coverage_requirement_ids = fields.One2many('ems.schedule.coverage', 'area_id')

    _sql_constraints = [('company_role_unique', 'unique(company_id, role_id)', 'Each Odoo role can only map to one area per company.')]

    @api.constrains('company_id', 'role_id')
    def _check_role_company(self):
        for area in self:
            role_company = getattr(area.role_id, 'company_id', False)
            if role_company and role_company != area.company_id:
                raise ValidationError(_('The planning role must belong to the selected company.'))


class EmsScheduleCoverage(models.Model):
    _name = 'ems.schedule.coverage'
    _description = 'EMS Schedule Coverage Requirement'
    _order = 'weekday, id'

    area_id = fields.Many2one('ems.schedule.area', required=True, ondelete='cascade', index=True)
    company_id = fields.Many2one(related='area_id.company_id', store=True, index=True)
    weekday = fields.Selection([(str(i), day) for i, day in enumerate(['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'])], required=True)
    minimum_people = fields.Integer(default=0, required=True)

    _sql_constraints = [('area_weekday_unique', 'unique(area_id, weekday)', 'Coverage can only be defined once per area and weekday.')]

    @api.constrains('minimum_people')
    def _check_minimum_people(self):
        if any(line.minimum_people < 0 for line in self):
            raise ValidationError(_('Minimum people cannot be negative.'))


class EmsScheduleDayMeta(models.Model):
    _name = 'ems.schedule.day.meta'
    _description = 'EMS Schedule Day Details'
    _order = 'schedule_date, company_id, area_id, id'

    company_id = fields.Many2one('res.company', required=True, index=True, default=lambda self: self.env.company)
    area_id = fields.Many2one('ems.schedule.area', ondelete='cascade', index=True)
    schedule_date = fields.Date(required=True, index=True)
    holiday_name = fields.Char()
    note = fields.Text()
    has_blocked_time = fields.Boolean(default=False)
    blocked_start = fields.Float()
    blocked_end = fields.Float()

    @api.constrains('area_id', 'company_id', 'blocked_start', 'blocked_end')
    def _check_values(self):
        for item in self:
            if item.area_id and item.area_id.company_id != item.company_id:
                raise ValidationError(_('The area must belong to the selected company.'))
            if item.has_blocked_time and not 0 <= item.blocked_start < item.blocked_end <= 24:
                raise ValidationError(_('Blocked start and end times are invalid.'))
            duplicate = self.search_count([
                ('id', '!=', item.id), ('company_id', '=', item.company_id.id),
                ('area_id', '=', item.area_id.id or False), ('schedule_date', '=', item.schedule_date),
            ])
            if duplicate:
                raise ValidationError(_('Day details already exist for this date, company, and area.'))


class EmsScheduleShiftBreak(models.Model):
    _name = 'ems.schedule.shift.break'
    _description = 'EMS Planned Shift Break'
    _order = 'slot_id, start_time, id'

    slot_id = fields.Many2one('planning.slot', required=True, ondelete='cascade', index=True)
    company_id = fields.Many2one(related='slot_id.company_id', store=True, index=True)
    start_time = fields.Float(required=True)
    duration_minutes = fields.Integer(required=True)
    is_paid = fields.Boolean(default=False)
    note = fields.Char()

    @api.constrains('slot_id', 'start_time', 'duration_minutes')
    def _check_values(self):
        for item in self:
            if not 0 <= item.start_time < 24 or not 5 <= item.duration_minutes <= 240:
                raise ValidationError(_('Break time or duration is invalid.'))
            if not item.slot_id.start_datetime or not item.slot_id.end_datetime:
                continue
            slot_start = fields.Datetime.context_timestamp(item, item.slot_id.start_datetime)
            slot_end = fields.Datetime.context_timestamp(item, item.slot_id.end_datetime)
            slot_start_minute = slot_start.hour * 60 + slot_start.minute
            slot_end_minute = slot_end.hour * 60 + slot_end.minute + (1440 if slot_end.date() > slot_start.date() else 0)
            break_start = round(item.start_time * 60)
            if slot_end_minute > 1440 and break_start < slot_start_minute:
                break_start += 1440
            break_end = break_start + item.duration_minutes
            if break_start < slot_start_minute or break_end > slot_end_minute:
                raise ValidationError(_('The break must fit completely inside the planning shift.'))
            siblings = self.search([('slot_id', '=', item.slot_id.id), ('id', '!=', item.id)])
            for sibling in siblings:
                sibling_start = round(sibling.start_time * 60)
                if slot_end_minute > 1440 and sibling_start < slot_start_minute:
                    sibling_start += 1440
                if break_start < sibling_start + sibling.duration_minutes and break_end > sibling_start:
                    raise ValidationError(_('Planned breaks cannot overlap.'))


class EmsScheduleComplianceRule(models.Model):
    _name = 'ems.schedule.compliance.rule'
    _description = 'EMS Schedule Compliance Rule'

    company_id = fields.Many2one('res.company', required=True, index=True, default=lambda self: self.env.company)
    break_required_after_minutes = fields.Integer(default=300, required=True)
    minimum_break_minutes = fields.Integer(default=30, required=True)
    maximum_shift_minutes = fields.Integer(default=720, required=True)
    minimum_rest_minutes = fields.Integer(default=600, required=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [('company_unique', 'unique(company_id)', 'Only one compliance rule is allowed per company.')]

    @api.constrains('break_required_after_minutes', 'minimum_break_minutes', 'maximum_shift_minutes', 'minimum_rest_minutes')
    def _check_minutes(self):
        for rule in self:
            if min(rule.break_required_after_minutes, rule.minimum_break_minutes, rule.maximum_shift_minutes, rule.minimum_rest_minutes) < 0:
                raise ValidationError(_('Compliance minute values cannot be negative.'))


class EmsScheduleCostRate(models.Model):
    _name = 'ems.schedule.cost.rate'
    _description = 'EMS Schedule Cost Rate'
    _order = 'effective_from desc, id desc'

    company_id = fields.Many2one('res.company', required=True, index=True, default=lambda self: self.env.company)
    employee_id = fields.Many2one('hr.employee', required=True, ondelete='cascade', index=True)
    hourly_rate = fields.Monetary(required=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', required=True, default=lambda self: self.env.company.currency_id)
    effective_from = fields.Date(required=True, index=True)
    effective_to = fields.Date()
    source = fields.Selection([('manager_confirmed', 'Manager Confirmed')], default='manager_confirmed', required=True)

    _sql_constraints = [('employee_company_start_unique', 'unique(company_id, employee_id, effective_from)', 'A rate already starts on this date for the employee and company.')]

    @api.constrains('company_id', 'employee_id', 'hourly_rate', 'effective_from', 'effective_to')
    def _check_values(self):
        for item in self:
            if item.hourly_rate < 0:
                raise ValidationError(_('Hourly rate cannot be negative.'))
            if item.effective_to and item.effective_to < item.effective_from:
                raise ValidationError(_('Effective end must not precede effective start.'))


class EmsScheduleWeekBudget(models.Model):
    _name = 'ems.schedule.week.budget'
    _description = 'EMS Weekly Schedule Budget'
    _order = 'week_start desc, company_id, id'

    company_id = fields.Many2one('res.company', required=True, index=True, default=lambda self: self.env.company)
    week_start = fields.Date(required=True, index=True)
    amount = fields.Monetary(required=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', required=True, default=lambda self: self.env.company.currency_id)

    _sql_constraints = [('company_week_unique', 'unique(company_id, week_start)', 'A company can only have one budget per week.')]

    @api.constrains('week_start', 'amount')
    def _check_values(self):
        for budget in self:
            if budget.amount < 0:
                raise ValidationError(_('Schedule budget cannot be negative.'))
            if budget.week_start and budget.week_start.weekday() != 0:
                raise ValidationError(_('Schedule budget week start must be a Monday.'))


class EmsScheduleUndoBatch(models.Model):
    _name = 'ems.schedule.undo.batch'
    _description = 'EMS Schedule Undo Batch'
    _order = 'create_date desc, id desc'

    token = fields.Char(required=True, index=True, copy=False)
    name = fields.Char(required=True)
    company_id = fields.Many2one('res.company', index=True, default=lambda self: self.env.company)
    actor_name = fields.Char()
    operation_count = fields.Integer(required=True, default=0)
    payload_json = fields.Text(required=True, copy=False)
    expires_at = fields.Datetime(required=True, index=True)
    consumed_at = fields.Datetime(index=True, copy=False)

    _sql_constraints = [('token_unique', 'unique(token)', 'The schedule undo token must be unique.')]

    @api.constrains('operation_count')
    def _check_operation_count(self):
        for batch in self:
            if batch.operation_count < 1:
                raise ValidationError(_('An undo batch must contain at least one operation.'))
