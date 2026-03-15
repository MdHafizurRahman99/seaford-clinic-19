from odoo import models


class ThemeMedicalClinic(models.AbstractModel):
    _inherit = 'theme.utils'

    def _theme_medical_clinic_post_copy(self, mod):
        self.enable_view('theme_medical_clinic.header_top_bar')
        self.enable_view('theme_medical_clinic.custom_footer')
        self.enable_view('website.option_footer_scrolltop')

        website = self.env['website'].get_current_website()
        if website:
            self._bind_theme_records_to_website('theme_medical_clinic', website.id)

    def _bind_theme_records_to_website(self, module_name, website_id):
        data_records = self.env['ir.model.data'].sudo().search([
            ('module', '=', module_name),
            ('model', 'in', ['website.menu', 'website.page']),
        ])
        for data_record in data_records:
            record = self.env[data_record.model].browse(data_record.res_id).exists()
            if record and 'website_id' in record._fields:
                record.website_id = website_id
