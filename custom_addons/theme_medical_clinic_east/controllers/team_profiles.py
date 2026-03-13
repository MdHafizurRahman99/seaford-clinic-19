from werkzeug.exceptions import NotFound

from odoo import http
from odoo.http import request


def _sitemap_team_profiles(env, profile_type, qs):
    if qs:
        return []
    profiles = env['medical.clinic.profile'].sudo().search(
        [
            ('profile_type', '=', profile_type),
            ('is_published', '=', True),
        ],
        order='sequence, name',
    )
    return [{'loc': profile.website_url} for profile in profiles]


def sitemap_doctors(env, rule, qs):
    return _sitemap_team_profiles(env, 'doctor', qs)


def sitemap_allied(env, rule, qs):
    return _sitemap_team_profiles(env, 'allied', qs)


class TeamProfilesController(http.Controller):
    """Website routes for dynamic doctor/allied listing and profile pages."""

    @staticmethod
    def _domain_for_type(profile_type):
        website_id = request.website.id
        return [
            ('profile_type', '=', profile_type),
            ('is_published', '=', True),
            '|',
            ('website_id', '=', False),
            ('website_id', '=', website_id),
        ]

    def _fetch_profile_or_404(self, profile_type, slug):
        profile = request.env['medical.clinic.profile'].sudo().search(
            self._domain_for_type(profile_type) + [('slug', '=', slug)],
            limit=1,
        )
        if not profile:
            raise NotFound()
        return profile

    def _listing_context(self, profile_type):
        is_doctor = profile_type == 'doctor'
        title = 'Our Doctors' if is_doctor else 'Our Allied Health Team'
        subtitle = (
            'Seaford East Medical Clinic provides continuity-focused general practice '
            'with strong support across prevention, chronic disease, family care, and skin health.'
            if is_doctor
            else 'Our allied health partners work alongside the Seaford East GP team '
                 'to support nutrition, diabetes education, and emotional wellbeing.'
        )
        profiles = request.env['medical.clinic.profile'].sudo().search(
            self._domain_for_type(profile_type) + [('show_in_listing', '=', True)],
            order='sequence, name',
        )
        return {
            'page_title': title,
            'page_subtitle': subtitle,
            'profile_type': profile_type,
            'profiles': profiles,
        }

    def _team_hub_context(self):
        profile_model = request.env['medical.clinic.profile'].sudo()
        return {
            'doctor_preview': profile_model.search(
                self._domain_for_type('doctor') + [('show_in_listing', '=', True)],
                order='sequence, name',
                limit=3,
            ),
            'allied_preview': profile_model.search(
                self._domain_for_type('allied') + [('show_in_listing', '=', True)],
                order='sequence, name',
                limit=2,
            ),
        }

    @http.route(
        ['/our-team'],
        type='http',
        auth='public',
        website=True,
        sitemap=True,
    )
    def team_hub(self, **kwargs):
        return request.render(
            'theme_medical_clinic_east.page_team_hub',
            self._team_hub_context(),
        )

    @http.route(
        ['/our-health-team-doctors'],
        type='http',
        auth='public',
        website=True,
        sitemap=True,
    )
    def doctors_listing(self, **kwargs):
        return request.render(
            'theme_medical_clinic_east.page_profile_listing',
            self._listing_context('doctor'),
        )

    @http.route(
        ['/our-health-team-allied-health'],
        type='http',
        auth='public',
        website=True,
        sitemap=True,
    )
    def allied_listing(self, **kwargs):
        return request.render(
            'theme_medical_clinic_east.page_profile_listing',
            self._listing_context('allied'),
        )

    @http.route(
        ['/our-health-team-doctors/<string:slug>'],
        type='http',
        auth='public',
        website=True,
        sitemap=sitemap_doctors,
    )
    def doctor_profile(self, slug, **kwargs):
        profile = self._fetch_profile_or_404('doctor', slug)
        related_profiles = request.env['medical.clinic.profile'].sudo().search(
            self._domain_for_type('doctor') + [('id', '!=', profile.id)],
            order='sequence, name',
            limit=3,
        )
        return request.render(
            'theme_medical_clinic_east.page_profile_detail',
            {
                'profile': profile,
                'profile_type': 'doctor',
                'related_profiles': related_profiles,
            },
        )

    @http.route(
        ['/our-health-team-allied-health/<string:slug>'],
        type='http',
        auth='public',
        website=True,
        sitemap=sitemap_allied,
    )
    def allied_profile(self, slug, **kwargs):
        profile = self._fetch_profile_or_404('allied', slug)
        related_profiles = request.env['medical.clinic.profile'].sudo().search(
            self._domain_for_type('allied') + [('id', '!=', profile.id)],
            order='sequence, name',
            limit=3,
        )
        return request.render(
            'theme_medical_clinic_east.page_profile_detail',
            {
                'profile': profile,
                'profile_type': 'allied',
                'related_profiles': related_profiles,
            },
        )
