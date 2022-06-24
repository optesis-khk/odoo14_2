# Migrate v14 by Optesis-CTD
{
    'name': 'Control Budget For Private',
    'author': 'OPTESIS SA',
    'version': '14.0.1',
    'category': 'Tools',
    'description': """
Ce module permet de faire le control budgetaire pour le secteur privé
""",
    'summary': 'Comptabilite',
    'sequence': 9,
    'depends': ['base','account','account_reports','analytic','account_budget','purchase','report_xlsx'],
    'data': [
        'data/approve_mail_template.xml',
        'data/refuse_mail_template.xml',
        'security/ir.model.access.csv',
        'security/purchase_security.xml',
        'views/menu_view.xml',
        'reports/reports.xml',
        'views/account_budget_view.xml',
        'views/account_analytic_account_view.xml',
        'wizard/purchase_order_refuse_wizard_view.xml',
        'views/purchase_view.xml',
        'views/account_invoice_view.xml',
        'views/account_move_view.xml',
        'views/res_company_view.xml',
    ],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
