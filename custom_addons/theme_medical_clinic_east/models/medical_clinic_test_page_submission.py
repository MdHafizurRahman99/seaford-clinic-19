from odoo import fields, models


class MedicalClinicTestPageSubmission(models.Model):
    _name = 'medical.clinic.test.page.submission'
    _description = 'Medical Clinic Test Page Submission'
    _order = 'submitted_on desc, id desc'

    name = fields.Char(required=True)
    email = fields.Char(required=True)
    phone = fields.Char()
    signature_name = fields.Char()
    signature = fields.Binary(required=True, attachment=True)
    website_id = fields.Many2one('website', string='Website')
    submitted_on = fields.Datetime(default=fields.Datetime.now, readonly=True)
