{
    'name': 'Travel Request Branch',
    'author': 'OPTESIS SA',
    'version': '14.0.0.0',
    'category': 'Accounting',
    'description': """
Ce module permet de gérer les budgets dans plusieurs branches
""",
    'summary': 'Comptabilite',
    'sequence': 9,
    "depends" : ['base', 'branch','employee_travel_managment'],
    "data": [
        'security/travel_request_ir_rule.xml',
        'views/travel_request.xml',
        'views/hr_employee.xml',
         'views/report_cms_mission.xml',
        'views/cms_layout_mission.xml',
    ],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
