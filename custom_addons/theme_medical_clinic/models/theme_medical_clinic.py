from odoo import api, models


class ThemeMedicalClinic(models.AbstractModel):
    _inherit = 'theme.utils'

    def _theme_medical_clinic_post_copy(self, mod):
        self.enable_view('theme_medical_clinic.header_top_bar')
        self.enable_view('theme_medical_clinic.custom_footer')
        self.enable_view('website.option_footer_scrolltop')
        self._theme_medical_clinic_sync_records()

    @api.model
    def _theme_medical_clinic_sync_records(self):
        website = self._get_theme_target_website('theme_medical_clinic')
        if website:
            self._bind_theme_records_to_website('theme_medical_clinic', website.id)
        return bool(website)

    def _get_theme_target_website(self, module_name):
        website_model = self.env['website'].sudo()
        context_website_id = self.env.context.get('website_id')
        if context_website_id:
            website = website_model.browse(context_website_id).exists()
            if website and website.theme_id and website.theme_id.name == module_name:
                return website
        return website_model.search([('theme_id.name', '=', module_name)], limit=1)

    def _bind_theme_records_to_website(self, module_name, website_id):
        data_records = self.env['ir.model.data'].sudo().search([
            ('module', '=', module_name),
            ('model', 'in', ['website.menu', 'website.page']),
        ])
        for data_record in data_records:
            record = self.env[data_record.model].browse(data_record.res_id).exists()
            if record and 'website_id' in record._fields:
                record.website_id = website_id
