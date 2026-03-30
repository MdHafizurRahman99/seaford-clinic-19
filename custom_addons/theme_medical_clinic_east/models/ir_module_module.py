from odoo import models


class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    _BINDING_THEME_NAME = 'theme_medical_clinic_east'

    def write(self, vals):
        modules_to_rebind = self.browse()
        if vals.get('state') == 'installed':
            modules_to_rebind = self.filtered(
                lambda mod: mod.name == self._BINDING_THEME_NAME and mod.state in ('to install', 'to upgrade')
            )

        result = super().write(vals)

        if modules_to_rebind:
            website_model = self.env['website'].sudo().with_context(active_test=False)
            websites = website_model.search([('theme_id', 'in', modules_to_rebind.ids)])
            if websites:
                theme_utils = self.env['theme.utils']
                for website in websites:
                    theme_utils.with_context(website_id=website.id)._post_copy(website.theme_id)

        return result
