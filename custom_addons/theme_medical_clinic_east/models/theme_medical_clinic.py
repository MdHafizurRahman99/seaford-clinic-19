from odoo import api, models


class ThemeMedicalClinicEast(models.AbstractModel):
    _inherit = 'theme.utils'

    def _theme_medical_clinic_east_post_copy(self, mod):
        # The custom header view already provides the top utility bar.
        self.disable_view('theme_medical_clinic_east.header_top_bar')
        self.enable_view('theme_medical_clinic_east.custom_footer')
        self.enable_view('website.option_footer_scrolltop')
        self._theme_medical_clinic_east_sync_records()

    @api.model
    def _theme_medical_clinic_east_sync_records(self):
        website = self._get_theme_target_website('theme_medical_clinic_east')
        if website:
            self._bind_theme_records_to_website('theme_medical_clinic_east', website.id)
            self._set_theme_homepage_url(website, 'theme_medical_clinic_east.page_coming_soon')
        return bool(website)

    def _get_theme_target_website(self, module_name):
        website_model = self.env['website'].sudo()
        context_website_id = self.env.context.get('website_id')
        if context_website_id:
            website = website_model.browse(context_website_id).exists()
            if website and self._website_matches_theme(website, module_name):
                return website
        anchor_website = self._get_theme_anchor_website(module_name)
        if anchor_website:
            return anchor_website
        return website_model.search([('theme_id.name', '=', module_name)], limit=1)

    def _website_matches_theme(self, website, module_name):
        return bool(website and website.theme_id and website.theme_id.name == module_name)

    def _get_theme_anchor_website(self, module_name):
        for model_name, xmlid_name in (
            ('website.page', 'page_home'),
            ('website.menu', 'menu_home'),
            ('website.page', 'page_coming_soon'),
        ):
            data_record = self.env['ir.model.data'].sudo().search([
                ('module', '=', module_name),
                ('model', '=', model_name),
                ('name', '=', xmlid_name),
            ], limit=1)
            if not data_record:
                continue
            record = self.env[model_name].sudo().browse(data_record.res_id).exists()
            if record and 'website_id' in record._fields and record.website_id:
                return record.website_id
        return self.env['website']

    def _bind_theme_records_to_website(self, module_name, website_id):
        data_records = self.env['ir.model.data'].sudo().search([
            ('module', '=', module_name),
            ('model', 'in', ['website.menu', 'website.page']),
        ])
        for data_record in data_records:
            record = self.env[data_record.model].sudo().browse(data_record.res_id).exists()
            if record and 'website_id' in record._fields:
                record.website_id = website_id

    def _set_theme_homepage_url(self, website, page_xmlid):
        page = self.env.ref(page_xmlid, raise_if_not_found=False)
        if page:
            website.sudo().homepage_url = page.url
