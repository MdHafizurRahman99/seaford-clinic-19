from odoo import _, api, fields, models
from odoo.exceptions import UserError


AU_PAYROLL_MODE_SELECTION = [
    ("test", "Testing"),
    ("prod", "Production"),
]

AU_REGISTRATION_STATUS_SELECTION = [
    ("pending", "Pending"),
    ("ongoing", "Ongoing"),
    ("registered_ongoing", "Registered (Ongoing)"),
    ("registered", "Registered"),
    ("expired", "Expired"),
]


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # Compatibility shim for databases that still have the auth_totp_mail
    # settings view active while the registry does not expose these fields.
    auth_totp_enforce = fields.Boolean(
        string="Enforce two-factor authentication",
    )
    auth_totp_policy = fields.Selection(
        [
            ("employee_required", "Employees only"),
            ("all_required", "All users"),
        ],
        string="Two-factor authentication enforcing policy",
        config_parameter="auth_totp.policy",
    )

    @api.onchange("auth_totp_enforce")
    def _onchange_auth_totp_enforce(self):
        if self.auth_totp_enforce:
            self.auth_totp_policy = self.auth_totp_policy or "employee_required"
        else:
            self.auth_totp_policy = False

    @api.model
    def get_values(self):
        res = super().get_values()
        res["auth_totp_enforce"] = bool(
            self.env["ir.config_parameter"].sudo().get_param("auth_totp.policy")
        )
        return res

    l10n_au_payroll_mode = fields.Selection(
        selection=AU_PAYROLL_MODE_SELECTION,
        string="Payroll Mode",
        compute="_compute_l10n_au_payroll_compatibility_fields",
        inverse="_inverse_l10n_au_payroll_mode",
        readonly=False,
        required=True,
    )
    l10n_au_registration_status = fields.Selection(
        selection=AU_REGISTRATION_STATUS_SELECTION,
        string="Registration Status",
        compute="_compute_l10n_au_payroll_compatibility_fields",
    )
    l10n_au_current_registration_mode = fields.Selection(
        selection=AU_PAYROLL_MODE_SELECTION,
        string="Current Registration Mode",
        compute="_compute_l10n_au_payroll_compatibility_fields",
    )

    @api.depends("company_id")
    def _compute_l10n_au_payroll_compatibility_fields(self):
        for rec in self:
            company = rec.company_id.sudo()
            rec.l10n_au_payroll_mode = "test"
            rec.l10n_au_registration_status = False
            rec.l10n_au_current_registration_mode = False

            if "l10n_au_payroll_mode" in company._fields:
                rec.l10n_au_payroll_mode = company.l10n_au_payroll_mode or "test"
            if "l10n_au_registration_status" in company._fields:
                rec.l10n_au_registration_status = (
                    company.l10n_au_registration_status or False
                )
            if "l10n_au_employer_registration_id" in company._fields:
                registration = company.l10n_au_employer_registration_id
                if registration and "registration_mode" in registration._fields:
                    rec.l10n_au_current_registration_mode = (
                        registration.registration_mode or False
                    )

    def _inverse_l10n_au_payroll_mode(self):
        for rec in self:
            company = rec.company_id.sudo()
            if "l10n_au_payroll_mode" in company._fields:
                company.l10n_au_payroll_mode = rec.l10n_au_payroll_mode or "test"

    def _raise_missing_au_payroll_api(self):
        raise UserError(
            _(
                "Australian payroll API settings are unavailable because the "
                "l10n_au_hr_payroll_api registry extension is not loaded."
            )
        )

    def register_payroll(self):
        self.ensure_one()
        method = getattr(self.company_id, "register_payroll", None)
        if callable(method):
            return method()
        self._raise_missing_au_payroll_api()

    def action_view_payroll_onboarding(self):
        self.ensure_one()
        method = getattr(self.company_id, "action_view_payroll_onboarding", None)
        if callable(method):
            return method()
        self._raise_missing_au_payroll_api()

    def cancel_ongoing_registration(self):
        self.ensure_one()
        company = self.company_id.sudo()
        if "l10n_au_employer_registration_ids" in company._fields:
            company.l10n_au_employer_registration_ids.filtered(
                lambda registration: registration.status == "pending"
            ).unlink()
            return False
        self._raise_missing_au_payroll_api()
