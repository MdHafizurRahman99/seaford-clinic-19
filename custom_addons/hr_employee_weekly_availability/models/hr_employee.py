from odoo import _, api, fields, models


COMPANY_ASSIGNMENT_SCOPE_SELECTION = [
    ('single', 'Single company'),
    ('selected', 'Selected companies'),
    ('all', 'All available companies'),
]


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    company_assignment_scope = fields.Selection(
        COMPANY_ASSIGNMENT_SCOPE_SELECTION,
        string='Company Coverage',
        default='single',
        tracking=True,
        groups='hr.group_hr_user',
    )
    company_assignment_line_ids = fields.One2many(
        'hr.employee.company.assignment',
        'employee_id',
        string='Company Assignments',
        groups='hr.group_hr_user',
    )
    work_company_ids = fields.Many2many(
        'res.company',
        compute='_compute_work_company_ids',
        string='Working Companies',
        groups='hr.group_hr_user',
    )
    company_assignment_summary = fields.Char(
        compute='_compute_company_assignment_summary',
        groups='hr.group_hr_user',
    )
    weekly_availability_line_ids = fields.One2many(
        'hr.employee.weekly.availability',
        'employee_id',
        string='Weekly Availability',
    )

    @api.depends_context('allowed_company_ids', 'uid')
    @api.depends('company_assignment_scope', 'company_id', 'company_assignment_line_ids.company_id')
    def _compute_work_company_ids(self):
        available_companies = self.env.user.company_ids
        for employee in self:
            if employee.company_assignment_scope == 'all':
                employee.work_company_ids = available_companies
            elif employee.company_assignment_scope == 'selected':
                employee.work_company_ids = employee.company_assignment_line_ids.mapped('company_id') or employee.company_id
            else:
                employee.work_company_ids = employee.company_id

    @api.depends_context('allowed_company_ids', 'uid')
    @api.depends('company_assignment_scope', 'company_id', 'company_assignment_line_ids.company_id')
    def _compute_company_assignment_summary(self):
        available_companies = self.env.user.company_ids
        for employee in self:
            companies = employee.work_company_ids
            if employee.company_assignment_scope == 'all':
                employee.company_assignment_summary = _(
                    'All available companies (%s)',
                    len(available_companies),
                )
            elif len(companies) == 1:
                employee.company_assignment_summary = companies.display_name
            elif companies:
                employee.company_assignment_summary = _('%s companies selected', len(companies))
            else:
                employee.company_assignment_summary = _('No companies selected')

    @api.onchange('company_assignment_scope')
    def _onchange_company_assignment_scope(self):
        for employee in self:
            if employee.company_assignment_scope == 'single' or employee.company_assignment_line_ids:
                continue
            employee.company_assignment_line_ids = [fields.Command.create(employee._prepare_primary_company_assignment_vals())]

    @api.model_create_multi
    def create(self, vals_list):
        employees = super().create(vals_list)
        employees._sync_company_assignment_state_from_primary_fields()
        return employees

    def write(self, vals):
        result = super().write(vals)
        if self.env.context.get('skip_company_assignment_sync'):
            return result

        sync_fields = {
            'company_id',
            'address_id',
            'work_location_id',
            'company_assignment_scope',
            'user_id',
        }
        if sync_fields.intersection(vals):
            self._sync_company_assignment_state_from_primary_fields()
        return result

    def _prepare_primary_company_assignment_vals(self):
        self.ensure_one()
        return {
            'company_id': self.company_id.id,
            'address_id': self.address_id.id or False,
            'work_location_id': self.work_location_id.id or False,
            'is_primary': True,
        }

    def _get_primary_company_assignment_line(self):
        self.ensure_one()
        if not self.company_assignment_line_ids:
            return self.env['hr.employee.company.assignment']
        primary_line = self.company_assignment_line_ids.filtered('is_primary')[:1]
        return primary_line or self.company_assignment_line_ids.sorted(
            lambda line: (line.sequence, line.id)
        )[:1]

    def _sync_company_assignment_state_from_primary_fields(self):
        if self.env.context.get('skip_company_assignment_sync'):
            return
        self._ensure_primary_company_assignment_line()
        self._sync_user_company_access()

    def _ensure_primary_company_assignment_line(self):
        Assignment = self.env['hr.employee.company.assignment']
        for employee in self:
            if employee.company_assignment_scope == 'single' and not employee.company_assignment_line_ids:
                continue

            primary_line = employee._get_primary_company_assignment_line()
            other_primary_lines = employee.company_assignment_line_ids.filtered(
                lambda line: line.is_primary and line != primary_line
            )
            if other_primary_lines:
                other_primary_lines.with_context(skip_company_assignment_sync=True).write({'is_primary': False})

            vals = employee._prepare_primary_company_assignment_vals()
            if primary_line:
                primary_line.with_context(skip_company_assignment_sync=True).write(vals)
            else:
                Assignment.with_context(skip_company_assignment_sync=True).create({
                    'employee_id': employee.id,
                    'sequence': 1,
                    **vals,
                })

    def _sync_primary_fields_from_company_assignments(self):
        if self.env.context.get('skip_company_assignment_sync'):
            return

        for employee in self:
            primary_line = employee._get_primary_company_assignment_line()
            if not primary_line:
                employee._sync_user_company_access()
                continue

            other_primary_lines = employee.company_assignment_line_ids.filtered(
                lambda line: line.is_primary and line != primary_line
            )
            if other_primary_lines:
                other_primary_lines.with_context(skip_company_assignment_sync=True).write({'is_primary': False})
            if not primary_line.is_primary:
                primary_line.with_context(skip_company_assignment_sync=True).write({'is_primary': True})

            vals = {}
            if employee.company_id != primary_line.company_id:
                vals['company_id'] = primary_line.company_id.id
            if employee.address_id != primary_line.address_id:
                vals['address_id'] = primary_line.address_id.id or False
            if employee.work_location_id != primary_line.work_location_id:
                vals['work_location_id'] = primary_line.work_location_id.id or False
            if vals:
                employee.with_context(skip_company_assignment_sync=True).write(vals)

            employee._sync_user_company_access()

    def _sync_user_company_access(self):
        if self.env.context.get('skip_company_assignment_user_sync'):
            return

        for employee in self.filtered('user_id'):
            companies = employee.work_company_ids or employee.company_id
            if not companies:
                continue

            primary_company = employee.company_id if employee.company_id in companies else companies[:1]
            vals = {}
            user = employee.user_id.sudo()

            if set(user.company_ids.ids) != set(companies.ids):
                vals['company_ids'] = [(6, 0, companies.ids)]
            if primary_company and user.company_id != primary_company:
                vals['company_id'] = primary_company.id

            if vals:
                user.with_context(skip_company_assignment_user_sync=True).write(vals)
