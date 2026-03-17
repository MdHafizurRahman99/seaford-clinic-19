from odoo import api, models


class ThemeMedicalClinic(models.AbstractModel):
    _inherit = 'theme.utils'

    def _theme_medical_clinic_post_copy(self, mod):
        self.enable_view('theme_medical_clinic.header_top_bar')
        self.enable_view('theme_medical_clinic.custom_footer')
        self.enable_view('website.option_footer_scrolltop')

    @api.model
    def _theme_medical_clinic_restore_baseline(self):
        website = self._get_clinic_website('theme_medical_clinic', 'seafordcentralmedical', 'Seaford Central Medical Clinic')
        if website:
            self._bind_theme_records_to_website('theme_medical_clinic', website.id)
            website.sudo().homepage_url = False
        return bool(website)

    def _get_clinic_website(self, module_name, domain_keyword, clinic_name):
        website_model = self.env['website'].sudo()
        website = website_model.search([('theme_id.name', '=', module_name)], limit=1)
        if website:
            return website
        return website_model.search([
            '|',
            ('domain', 'ilike', domain_keyword),
            ('name', 'ilike', clinic_name),
        ], limit=1)

    def _bind_theme_records_to_website(self, module_name, website_id):
        data_records = self.env['ir.model.data'].sudo().search([
            ('module', '=', module_name),
            ('model', 'in', ['website.menu', 'website.page']),
        ])
        for data_record in data_records:
            record = self.env[data_record.model].sudo().browse(data_record.res_id).exists()
            if record and 'website_id' in record._fields:
                record.website_id = website_id
