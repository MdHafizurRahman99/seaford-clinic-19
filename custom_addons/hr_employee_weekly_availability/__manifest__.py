{
    'name': 'HR Employee Weekly Availability',
    'summary': 'Track employee weekday availability and unavailability windows',
    'version': '19.0.5.0.0',
    'category': 'Human Resources/Employees',
    'author': 'Custom',
    'license': 'LGPL-3',
    'depends': ['hr_homeworking', 'planning'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/hr_employee_views.xml',
        'views/res_users_views.xml',
        'views/employee_schedule_entry_views.xml',
    ],
    'installable': True,
    'application': False,
}
