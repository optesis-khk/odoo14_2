{
    'name': 'Control Budget For Private Community',
    'author': 'OPTESIS SA',
    'version': '14.0.0.0',
    'category': 'Tools',
    'description': """
Ce module permet de faire le control budgetairepour le secteur privé
""",
    'summary': 'Comptabilite',
    'sequence': 9,
    'depends': ['base','analytic','base_accounting_kit','purchase','ks_percent_field'],
    'data': [
        'data/approve_mail_template.xml',
        'data/refuse_mail_template.xml',
        'security/ir.model.access.csv',
        'security/purchase_security.xml',
        'views/menu_view.xml',
        'views/account_budget_view.xml',
        'views/account_analytic_account_view.xml',
        'views/purchase_view.xml',
        'views/res_company_view.xml',
    ],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
