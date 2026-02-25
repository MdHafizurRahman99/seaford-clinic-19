from odoo import models


class ThemeMedicalClinicEast(models.AbstractModel):
    _inherit = 'theme.utils'

    def _theme_medical_clinic_east_post_copy(self, mod):
        self.enable_view('theme_medical_clinic_east.header_top_bar')
        self.enable_view('theme_medical_clinic_east.custom_footer')
        self.enable_view('website.option_footer_scrolltop')

        website = self.env['website'].get_current_website()
        if website:
            # Bind pages and menus to this specific website
            for record_id in ['menu_home', 'menu_about', 'menu_services', 'menu_team', 'menu_contact', 
                              'page_home', 'page_about_us', 'page_services', 'page_our_team', 'page_contact']:
                record = self.env.ref(f'theme_medical_clinic_east.{record_id}', raise_if_not_found=False)
                if record:
                    record.website_id = website.id
