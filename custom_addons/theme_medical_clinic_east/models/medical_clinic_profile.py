import re

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class MedicalClinicProfile(models.Model):
    _name = 'medical.clinic.profile'
    _description = 'Medical Clinic Team Profile'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    slug = fields.Char(
        required=True,
        help='URL-safe slug. Example: dr-jane-smith',
    )
    profile_type = fields.Selection(
        [('doctor', 'Doctor'), ('allied', 'Allied Health')],
        required=True,
        default='doctor',
    )
    qualification = fields.Char()
    summary = fields.Text(help='Short summary used on listing cards.')
    bio = fields.Html(help='Full profile content shown on detail page.')
    special_interests = fields.Char(
        help='Comma-separated interests. Example: Women health, Skin checks',
    )
    languages = fields.Char(help='Comma-separated language list.')

    availability_status = fields.Selection(
        [
            ('accepting', 'Accepting New Patients'),
            ('limited', 'Limited New Patients'),
            ('unavailable', 'Appointments Unavailable'),
            ('on_leave', 'On Leave'),
        ],
        default='accepting',
        required=True,
    )
    availability_note = fields.Char(
        help='Optional short status note shown below the badge.',
    )
    booking_url = fields.Char(help='External or internal booking link.')
    phone_fallback = fields.Char(
        default='0398756222',
        help='Digits only. Used when online booking is not available.',
    )
    show_in_listing = fields.Boolean(default=True)
    is_published = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)

    image_1920 = fields.Image(max_width=1920, max_height=1920)
    website_id = fields.Many2one('website', string='Website')

    website_url = fields.Char(compute='_compute_website_url')
    availability_label = fields.Char(compute='_compute_availability_ui')
    availability_bg_color = fields.Char(compute='_compute_availability_ui')
    availability_text_color = fields.Char(compute='_compute_availability_ui')
    booking_available = fields.Boolean(compute='_compute_booking_available')

    _sql_constraints = [
        (
            'slug_profile_type_unique',
            'unique(profile_type, slug)',
            'Slug must be unique per profile type.',
        ),
    ]

    @api.depends('profile_type', 'slug')
    def _compute_website_url(self):
        for profile in self:
            if profile.profile_type == 'doctor':
                profile.website_url = '/our-health-team-doctors/%s' % profile.slug
            else:
                profile.website_url = '/our-health-team-allied-health/%s' % profile.slug

    @api.depends('availability_status')
    def _compute_availability_ui(self):
        mapping = {
            'accepting': ('Accepting New Patients', '#eaf9f2', '#217f59'),
            'limited': ('Limited New Patients', '#eef5ff', '#2c5ea8'),
            'unavailable': ('Appointments Unavailable', '#f3f5f6', '#5b6366'),
            'on_leave': ('On Leave', '#fdf6e5', '#8a6513'),
        }
        for profile in self:
            label, bg, text = mapping.get(
                profile.availability_status,
                ('Status', '#f3f5f6', '#5b6366'),
            )
            profile.availability_label = label
            profile.availability_bg_color = bg
            profile.availability_text_color = text

    @api.depends('availability_status', 'booking_url')
    def _compute_booking_available(self):
        for profile in self:
            profile.booking_available = bool(
                profile.booking_url and profile.availability_status not in ('on_leave', 'unavailable')
            )

    @api.constrains('slug')
    def _check_slug(self):
        pattern = re.compile(r'^[a-z0-9-]+$')
        for profile in self:
            if not pattern.match(profile.slug or ''):
                raise ValidationError(
                    'Slug can only contain lowercase letters, numbers, and hyphens.'
                )

    @api.constrains('phone_fallback')
    def _check_phone_fallback(self):
        for profile in self:
            if profile.phone_fallback and not re.match(r'^[0-9+]+$', profile.phone_fallback):
                raise ValidationError(
                    'Phone fallback should contain digits and optional + only.'
                )
