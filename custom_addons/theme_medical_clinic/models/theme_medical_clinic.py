from odoo import models


class ThemeMedicalClinic(models.AbstractModel):
    _inherit = 'theme.utils'

    def _iter_theme_records(self, module_name, model_name):
        data_model = self.env['ir.model.data'].sudo()
        model = self.env[model_name].sudo().with_context(active_test=False)
        data_rows = data_model.search([
            ('module', '=', module_name),
            ('model', '=', model_name),
        ], order='id')
        for data_row in data_rows:
            record = model.browse(data_row.res_id)
            if record.exists():
                yield record

    def _ensure_page_for_website(self, page, website):
        page = page.sudo().with_context(active_test=False)
        if not page.website_id:
            # Move generic page to the target website without triggering COW.
            page.with_context(no_cow=True).write({'website_id': website.id})
            return page

        if page.website_id == website:
            return page

        page_model = self.env['website.page'].sudo().with_context(active_test=False)
        existing_page = page_model.search([
            ('key', '=', page.key),
            ('website_id', '=', website.id),
        ], limit=1)
        if existing_page:
            return existing_page

        key_value = page.key or page.view_id.key
        new_view_vals = {'website_id': website.id}
        if key_value:
            new_view_vals['key'] = key_value
        new_view = page.view_id.with_context(active_test=False).copy(new_view_vals)

        new_page_vals = {
            'website_id': website.id,
            'view_id': new_view.id,
            'url': page.url,
        }
        if new_view.key:
            new_page_vals['key'] = new_view.key
        return page.copy(new_page_vals)

    def _bind_module_pages_and_menus(self, module_name, website):
        page_map = {}
        for page in self._iter_theme_records(module_name, 'website.page'):
            page_map[page.id] = self._ensure_page_for_website(page, website)

        menu_model = self.env['website.menu'].sudo().with_context(active_test=False)
        for source_menu in self._iter_theme_records(module_name, 'website.menu'):
            if not source_menu.website_id or source_menu.website_id == website:
                target_menu = source_menu
            else:
                target_menu = menu_model.search([
                    ('website_id', '=', website.id),
                    ('url', '=', source_menu.url),
                    ('name', '=', source_menu.name),
                ], limit=1)

            if not target_menu:
                continue

            values = {}
            target_page = page_map.get(source_menu.page_id.id)
            if target_page and target_menu.page_id != target_page:
                values['page_id'] = target_page.id
            if not target_menu.website_id:
                values['website_id'] = website.id
            if values:
                target_menu.write(values)

    def _theme_medical_clinic_post_copy(self, mod):
        self.enable_view('theme_medical_clinic.header_top_bar')
        self.enable_view('theme_medical_clinic.custom_footer')
        self.enable_view('website.option_footer_scrolltop')

        website = self.env['website'].get_current_website()
        if website:
            self._bind_module_pages_and_menus(mod.name, website)
