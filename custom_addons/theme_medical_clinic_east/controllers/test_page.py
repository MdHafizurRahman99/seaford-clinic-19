import base64
import binascii

from werkzeug.utils import redirect

from odoo import http
from odoo.http import request


class MedicalClinicTestPageController(http.Controller):
    @http.route(
        ['/test-page/submit'],
        type='http',
        auth='public',
        website=True,
        methods=['POST'],
        csrf=True,
    )
    def submit_test_page_form(self, **post):
        name = (post.get('name') or '').strip()
        email = (post.get('email') or '').strip()
        phone = (post.get('phone') or '').strip()
        signature_name = (post.get('signature_name') or '').strip()
        signature = self._extract_signature(post.get('signature'))

        if not name or not email or not signature:
            return redirect('/test-page?error=1#test-page-form')

        request.env['medical.clinic.test.page.submission'].sudo().create({
            'name': name,
            'email': email,
            'phone': phone,
            'signature': signature,
            'signature_name': signature_name or name,
            'website_id': request.website.id,
        })
        return redirect('/test-page?submitted=1#test-page-form')

    @staticmethod
    def _extract_signature(signature_value):
        signature_value = (signature_value or '').strip()
        if not signature_value:
            return False

        if ',' in signature_value:
            _, signature_value = signature_value.split(',', 1)

        try:
            base64.b64decode(signature_value, validate=True)
        except (binascii.Error, ValueError):
            return False

        return signature_value
