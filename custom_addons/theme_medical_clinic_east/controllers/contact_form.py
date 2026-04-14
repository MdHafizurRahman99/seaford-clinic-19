from werkzeug.utils import redirect

from odoo import http
from odoo.http import request


class MedicalClinicContactFormController(http.Controller):
    @http.route(
        ['/contact/submit'],
        type='http',
        auth='public',
        website=True,
        methods=['POST'],
        csrf=True,
    )
    def submit_contact_form(self, **post):
        name = (post.get('name') or '').strip()
        email = (post.get('email') or '').strip()
        phone = (post.get('phone') or '').strip()
        subject = (post.get('subject') or '').strip()
        message = (post.get('message') or '').strip()

        if not name or not email or not subject or not message:
            return redirect('/contact?error=1#contact-form')

        request.env['medical.clinic.contact.request'].sudo().create({
            'name': name,
            'email': email,
            'phone': phone,
            'subject': subject,
            'message': message,
            'website_id': request.website.id,
        })
        return redirect('/contact?submitted=1#contact-form')
