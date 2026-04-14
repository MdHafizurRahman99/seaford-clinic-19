from odoo import fields, models


class MedicalClinicContactRequest(models.Model):
    _name = 'medical.clinic.contact.request'
    _description = 'Medical Clinic Contact Request'
    _order = 'create_date desc'

    name = fields.Char(required=True)
    email = fields.Char(required=True)
    phone = fields.Char()
    subject = fields.Char(required=True)
    message = fields.Text(required=True)
    website_id = fields.Many2one('website', string='Website')
    status = fields.Selection(
        [
            ('new', 'New'),
            ('reviewed', 'Reviewed'),
            ('closed', 'Closed'),
        ],
        default='new',
        required=True,
    )
    submitted_on = fields.Datetime(default=fields.Datetime.now, readonly=True)
