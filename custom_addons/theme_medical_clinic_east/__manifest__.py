{
    'name': 'Seaford East medical clinic',
    'description': 'Professional sea-green website theme for Seaford East Medical Clinic',
    'category': 'Theme/Medical',
    'sequence': 900,
    'version': '19.0.2.0.0',
    'depends': ['website'],
    'data': [
        'data/generate_primary_template.xml',
        'data/images.xml',
        'views/theme_medical_clinic_templates.xml',
        'views/snippets/s_medical_hero.xml',
        'views/snippets/s_services_grid.xml',
        'views/snippets/s_doctor_cards.xml',
        'views/snippets/s_clinic_hours.xml',
        'views/snippets/s_appointment_cta.xml',
        'views/snippets/s_patient_testimonials.xml',
        'views/snippets/s_accreditations.xml',
        'views/snippets/snippets.xml',
        'data/pages/home.xml',
        'data/pages/about.xml',
        'data/pages/services.xml',
        'data/pages/team.xml',
        'data/pages/contact.xml',
        'data/menu.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [
            'theme_medical_clinic_east/static/src/scss/primary_variables.scss',
        ],
        'web._assets_secondary_variables': [
            'theme_medical_clinic_east/static/src/scss/secondary_variables.scss',
        ],
        'web.assets_frontend': [
            'theme_medical_clinic_east/static/src/scss/theme.scss',
            'theme_medical_clinic_east/static/src/scss/snippets/*.scss',
        ],
    },
    'images': [
        'static/description/cover.png',
    ],
    'configurator_snippets': {
        'homepage': [],
        # 'homepage': ['s_medical_hero', 's_services_grid', 's_doctor_cards',
        #              's_patient_testimonials', 's_appointment_cta'],
    },
    'new_page_templates': {
        'basic': {
            'clinic_home': ['s_medical_hero', 's_services_grid',
                            's_doctor_cards', 's_appointment_cta'],
        },
    },
    'author': 'Seaford East Medical Clinic',
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
