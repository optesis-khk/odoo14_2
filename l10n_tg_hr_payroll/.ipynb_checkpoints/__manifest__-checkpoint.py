# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Copyright (c) Optesis 2018 www.optesis.com

{
    'name': 'Paie Togolaise',
    'version': '12.1',
    'author': 'Optesis ',
    'category': 'Localization',
    'description': """
Togo Payroll Rules.
=====================

    - Configuration of hr_payroll for Togo localization
                    """,
    'website': 'http://www.optesis.com',
    'depends': ['optipay', 'l10n_pcgo'],
    'data': [
        'security/ir.model.access.csv',
        'data/salary_rule_data.xml',
        'data/chart_data.xml',
        'data/salary_rule_foreign_data.xml',
        'views/payroll_chart_template_views.xml',
        'views/multi_company_view.xml',
    ],

}
