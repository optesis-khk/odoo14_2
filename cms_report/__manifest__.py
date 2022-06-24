# -*- coding: utf-8 -*-
{
    
     'name': 'Cms Report',
    'summary': """Gérez les rapports de CMS""",
    'description': """Ce module permet de créer des rapports pour cms""",
    'category': 'Report',
    'author': 'OPTESIS SA',
    'version': '14.0.1',
    'maintainer': 'Optesis',
    'company': 'Optesis SA',
    'website': 'https://www.optesis.com',
    
    

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase', 'private_control_budget'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/report_bon_commande_cms.xml',
        'views/report_cms_mission.xml',
        'views/cms_layout.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
