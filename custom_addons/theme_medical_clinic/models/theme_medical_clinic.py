from odoo import models


class ThemeMedicalClinic(models.AbstractModel):
    _inherit = 'theme.utils'

    def _theme_medical_clinic_post_copy(self, mod):
        self.enable_view('website.template_header_default')
        self.enable_view('website.template_footer_contact')
        self.enable_view('website.option_footer_scrolltop')
