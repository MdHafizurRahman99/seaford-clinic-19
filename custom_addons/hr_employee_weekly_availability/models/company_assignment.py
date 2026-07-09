from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrEmployeeCompanyAssignment(models.Model):
    _name = 'hr.employee.company.assignment'
    _description = 'Employee Company Assignment'
    _order = 'sequence, is_primary desc, company_id, id'
    _rec_name = 'display_name'

    sequence = fields.Integer(default=10)
    employee_id = fields.Many2one(
        'hr.employee',
        required=True,
        ondelete='cascade',
        index=True,
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        tracking=True,
    )
    address_id = fields.Many2one(
        'res.partner',
        string='Work Address',
        default=lambda self: self.env.company.partner_id,
        check_company=True,
        tracking=True,
    )
    work_location_id = fields.Many2one(
        'hr.work.location',
        string='Work Location',
        domain="[('company_id', '=', company_id), ('address_id', '=', address_id)]",
        check_company=True,
        tracking=True,
    )
    is_primary = fields.Boolean(string='Primary Assignment')
    available_company_ids = fields.Many2many(
        'res.company',
        compute='_compute_available_company_ids',
    )
    display_name = fields.Char(compute='_compute_display_name')

    @api.depends_context('allowed_company_ids', 'uid')
    def _compute_available_company_ids(self):
        companies = self.env.user.company_ids
        for line in self:
            line.available_company_ids = companies

    @api.depends('company_id', 'address_id', 'work_location_id', 'is_primary')
    def _compute_display_name(self):
        for line in self:
            parts = [line.company_id.display_name or _('No company')]
            if line.work_location_id:
                parts.append(line.work_location_id.display_name)
            elif line.address_id:
                parts.append(line.address_id.display_name)
            if line.is_primary:
                parts.append(_('Primary'))
            line.display_name = ' / '.join(parts)

    @api.onchange('company_id')
    def _onchange_company_id(self):
        for line in self:
            if not line.company_id:
                line.address_id = False
                line.work_location_id = False
                continue
            line.address_id = line.company_id.partner_id
            if line.work_location_id and line.work_location_id.company_id != line.company_id:
                line.work_location_id = False

    @api.onchange('address_id')
    def _onchange_address_id(self):
        for line in self:
            if line.work_location_id and line.work_location_id.address_id != line.address_id:
                line.work_location_id = False

    @api.constrains('employee_id', 'is_primary')
    def _check_primary_assignment(self):
        for line in self.filtered('is_primary'):
            primary_lines = line.employee_id.company_assignment_line_ids.filtered('is_primary')
            if len(primary_lines) > 1:
                raise ValidationError(_('An employee can only have one primary company assignment.'))

    @api.constrains('company_id', 'address_id', 'work_location_id')
    def _check_work_location_company(self):
        for line in self.filtered('work_location_id'):
            if line.work_location_id.company_id != line.company_id:
                raise ValidationError(_('The work location company must match the assignment company.'))
            if line.address_id and line.work_location_id.address_id != line.address_id:
                raise ValidationError(_('The work location address must match the assignment work address.'))

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if not self.env.context.get('skip_company_assignment_sync'):
            records.mapped('employee_id')._sync_primary_fields_from_company_assignments()
        return records

    def write(self, vals):
        result = super().write(vals)
        if not self.env.context.get('skip_company_assignment_sync'):
            self.mapped('employee_id')._sync_primary_fields_from_company_assignments()
        return result

    def unlink(self):
        employees = self.mapped('employee_id')
        result = super().unlink()
        if not self.env.context.get('skip_company_assignment_sync'):
            employees._sync_primary_fields_from_company_assignments()
        return result
