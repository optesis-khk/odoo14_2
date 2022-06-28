#-*- coding:utf-8 -*-
from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    batch_id = fields.Many2one('hr.payslip.run', string="Payroll Batch")
    
#add by mpb
class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'
    
    #add by mpb
    register_id = fields.Many2one('hr.contribution.register', string='Contribution Register',
        help="Eventual third party involved in the salary payment of the employees.")
        #fin    

    def _get_partner_id(self, credit_account):
        """
        Get partner_id of slip line to use in account_move_line
        """
        # use partner of salary rule or fallback on employee's address
        register_partner_id = self.salary_rule_id.register_id.partner_id
        partner_id = register_partner_id.id or self.slip_id.employee_id.address_home_id.id
        if credit_account:
            if register_partner_id or self.salary_rule_id.account_credit.internal_type in ('receivable', 'payable'):
                return partner_id
        else:
            if register_partner_id or self.salary_rule_id.account_debit.internal_type in ('receivable', 'payable'):
                return partner_id
        return False

