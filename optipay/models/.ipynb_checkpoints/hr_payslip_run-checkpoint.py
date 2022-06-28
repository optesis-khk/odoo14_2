import time
from datetime import datetime, date, time as t
from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, float_compare , float_is_zero
from odoo.exceptions import ValidationError, UserError
from pytz import timezone
import logging
_logger = logging.getLogger(__name__)



class HrPayslipRunInherit(models.Model):
    _inherit = 'hr.payslip.run'

    journal_id = fields.Many2one('account.journal', 'Salary Journal', readonly=False)
    

    def action_validate(self):
        precision = self.env['decimal.precision'].precision_get('Payroll')

        line_ids = []
        dict = {}

        index_deb = 0
        index_cred = 0

        for slip in self.slip_ids:
            debit_sum = 0.0
            credit_sum = 0.0
            date = slip.date or slip.date_to
            analityc_account_id = str(slip.contract_id.analytic_account_id.id or 0)
            if slip.state != 'done':
                for line in slip.line_ids:
                    amount = slip.credit_note and -line.total or line.total
                    if float_is_zero(amount, precision_digits=precision):
                        continue
                    debit_account_id = line.salary_rule_id.account_debit.id
                    credit_account_id = line.salary_rule_id.account_credit.id

                    # manage debit
                    if debit_account_id and line.total > 0:
                        # if account code start with 421 we do not regroup
                        if line.salary_rule_id.account_debit.code[:3] == "421":
                            index_deb += 1
                            dict[str(debit_account_id) + str(index_deb)] = {}
                            dict[str(debit_account_id) + str(index_deb)]['name'] = line.name
                            dict[str(debit_account_id) + str(index_deb)]['partner_id'] = line._get_partner_id(credit_account=True)
                            dict[str(debit_account_id) + str(index_deb)]['account_id'] = debit_account_id
                            dict[str(debit_account_id) + str(index_deb)]['journal_id'] = slip.journal_id.id
                            dict[str(debit_account_id) + str(index_deb)]['date'] = date
                            dict[str(debit_account_id) + str(index_deb)]['debit'] = round(amount > 0.0 and amount or 0.0)
                            dict[str(debit_account_id) + str(index_deb)]['credit'] = 0 #round(amount < 0.0 and -amount or 0.0)
                            dict[str(debit_account_id) + str(index_deb)]['analytic_account_id'] = False
                            #dict[str(debit_account_id) + str(index_deb)]['tax_line_id'] = line.salary_rule_id.account_tax_id.id
                        # we regroup by account and analytic account started by 7 or 6
                        elif line.salary_rule_id.account_debit.code[:1] in ["7", "6"]:
                            if analityc_account_id == '0':
                                _logger.info('MISSING ANALYTIC ACCOUNT IN CONTRACT '+str(slip.contract_id.name))
                            if str(debit_account_id)+analityc_account_id in dict:
                                dict[str(debit_account_id)+analityc_account_id]['debit'] += round(amount > 0.0 and amount or 0.0)
                                dict[str(debit_account_id)+analityc_account_id]['credit'] += 0 #round(amount < 0.0 and -amount or 0.0)
                            else:
                                dict[str(debit_account_id)+analityc_account_id] = {}
                                dict[str(debit_account_id)+analityc_account_id]['name'] = line.name
                                dict[str(debit_account_id)+analityc_account_id]['partner_id'] = False
                                dict[str(debit_account_id)+analityc_account_id]['account_id'] = debit_account_id
                                dict[str(debit_account_id)+analityc_account_id]['journal_id'] = slip.journal_id.id
                                dict[str(debit_account_id)+analityc_account_id]['date'] = date
                                dict[str(debit_account_id)+analityc_account_id]['debit'] = round(amount > 0.0 and amount or 0.0)
                                dict[str(debit_account_id)+analityc_account_id]['credit'] = 0 #amount < 0.0 and -amount or 0.0
                                dict[str(debit_account_id)+analityc_account_id]['analytic_account_id'] = analityc_account_id if analityc_account_id != '0' else False
                                #dict[str(debit_account_id)+analityc_account_id]['tax_line_id'] = line.salary_rule_id.account_tax_id.id
                        # we regroup others by account
                        else:
                            if debit_account_id in dict:
                                _logger.info('DEBIT KEY IN' + str(credit_account_id))
                                dict[debit_account_id]['debit'] += round(amount > 0.0 and amount or 0.0)
                                dict[debit_account_id]['credit'] += 0 #round(amount < 0.0 and -amount or 0.0)
                            else:
                                _logger.info('DEBIT KEY ' + str(credit_account_id))
                                dict[debit_account_id] = {}
                                dict[debit_account_id]['name'] = line.name
                                dict[debit_account_id]['partner_id'] = False #line._get_partner_id(credit_account=False)
                                dict[debit_account_id]['account_id'] = debit_account_id
                                dict[debit_account_id]['journal_id'] = slip.journal_id.id
                                dict[debit_account_id]['date'] = date
                                dict[debit_account_id]['debit'] = round(amount > 0.0 and amount or 0.0)
                                dict[debit_account_id]['credit'] = 0 #amount < 0.0 and -amount or 0.0
                                dict[debit_account_id]['analytic_account_id'] = False
                                #dict[debit_account_id]['tax_line_id'] = line.salary_rule_id.account_tax_id.id
                        debit_sum += round(amount > 0.0 and amount or 0.0 - amount < 0.0 and -amount or 0.0)
                    elif debit_account_id and line.total < 0:
                        amount = abs(amount)
                        # if account code start with 421 we do not regroup
                        if line.salary_rule_id.account_debit.code[:3] == "421":
                            index_cred += 1
                            dict[str(credit_account_id) + str(index_cred)] = {}
                            dict[str(credit_account_id) + str(index_cred)]['name'] = line.name
                            dict[str(credit_account_id) + str(index_cred)]['partner_id'] = line._get_partner_id(credit_account=True)
                            dict[str(credit_account_id) + str(index_cred)]['account_id'] = debit_account_id
                            dict[str(credit_account_id) + str(index_cred)]['journal_id'] = slip.journal_id.id
                            dict[str(credit_account_id) + str(index_cred)]['date'] = date
                            dict[str(credit_account_id) + str(index_cred)]['debit'] = 0
                            dict[str(credit_account_id) + str(index_cred)]['credit'] = round(amount > 0.0 and amount or 0.0)
                            dict[str(credit_account_id) + str(index_cred)]['analytic_account_id'] = False
                            #dict[str(credit_account_id) + str(index_cred)]['tax_line_id'] = line.salary_rule_id.account_tax_id.id
                        # we regroup by account and analytic account started by 7 or 6
                        elif line.salary_rule_id.account_debit.code[:1] in ["7", "6"]:
                            if str(credit_account_id)+analityc_account_id in dict:
                                dict[str(credit_account_id)+analityc_account_id]['credit'] += round(amount > 0.0 and amount or 0.0)
                            else:
                                dict[str(credit_account_id)+analityc_account_id] = {}
                                dict[str(credit_account_id)+analityc_account_id]['name'] = line.name
                                dict[str(credit_account_id)+analityc_account_id]['partner_id'] = False
                                dict[str(credit_account_id)+analityc_account_id]['account_id'] = debit_account_id
                                dict[str(credit_account_id)+analityc_account_id]['journal_id'] = slip.journal_id.id
                                dict[str(credit_account_id)+analityc_account_id]['date'] = date
                                dict[str(credit_account_id)+analityc_account_id]['debit'] = 0
                                dict[str(credit_account_id)+analityc_account_id]['credit'] = round(amount > 0.0 and amount or 0.0)
                                dict[str(credit_account_id)+analityc_account_id]['analytic_account_id'] = analityc_account_id if analityc_account_id != '0' else False
                                #dict[str(credit_account_id)+analityc_account_id]['tax_line_id'] = line.salary_rule_id.account_tax_id.id
                        # we regroup others by account
                        else:
                            if credit_account_id in dict:
                                dict[credit_account_id]['credit'] += round(amount > 0.0 and amount or 0.0)
                            else:
                                dict[credit_account_id] = {}
                                dict[credit_account_id]['name'] = line.name
                                dict[credit_account_id]['partner_id'] = line._get_partner_id(credit_account=False)
                                dict[credit_account_id]['account_id'] = debit_account_id
                                dict[credit_account_id]['journal_id'] = slip.journal_id.id
                                dict[credit_account_id]['date'] = date
                                dict[credit_account_id]['debit'] = 0
                                dict[credit_account_id]['credit'] = round(amount > 0.0 and amount or 0.0)
                                dict[credit_account_id]['analytic_account_id'] = False
                                #dict[credit_account_id]['tax_line_id'] = line.salary_rule_id.account_tax_id.id
                        credit_sum += round(amount > 0.0 and amount or 0.0 - amount < 0.0 and -amount or 0.0)


                    # manage credit
                    if credit_account_id and line.total > 0:
                        # if account code start with 421 we do not regroup
                        if line.salary_rule_id.account_credit.code[:3] == "421":
                            index_cred += 1
                            dict[str(credit_account_id) + str(index_cred)] = {}
                            dict[str(credit_account_id) + str(index_cred)]['name'] = line.name
                            dict[str(credit_account_id) + str(index_cred)]['partner_id'] = line._get_partner_id(credit_account=True)
                            dict[str(credit_account_id) + str(index_cred)]['account_id'] = credit_account_id
                            dict[str(credit_account_id) + str(index_cred)]['journal_id'] = slip.journal_id.id
                            dict[str(credit_account_id) + str(index_cred)]['date'] = date
                            dict[str(credit_account_id) + str(index_cred)]['debit'] = 0 #round(amount < 0.0 and -amount or 0.0)
                            dict[str(credit_account_id) + str(index_cred)]['credit'] = round(amount > 0.0 and amount or 0.0)
                            dict[str(credit_account_id) + str(index_cred)]['analytic_account_id'] = False
                            #dict[str(credit_account_id) + str(index_cred)]['tax_line_id'] = \
                            #    line.salary_rule_id.account_tax_id.id
                        # we regroup by account and analytic account started by 7 or 6
                        elif line.salary_rule_id.account_credit.code[:1] in ["7", "6"]:
                            if str(credit_account_id)+analityc_account_id in dict:
                                dict[str(credit_account_id)+analityc_account_id]['credit'] += round(amount > 0.0 and amount or 0.0)
                                dict[str(credit_account_id)+analityc_account_id]['debit'] += 0 #round(amount < 0.0 and -amount or 0.0)
                            else:
                                dict[str(credit_account_id)+analityc_account_id] = {}
                                dict[str(credit_account_id)+analityc_account_id]['name'] = line.name
                                dict[str(credit_account_id)+analityc_account_id]['partner_id'] = False
                                dict[str(credit_account_id)+analityc_account_id]['account_id'] = credit_account_id
                                dict[str(credit_account_id)+analityc_account_id]['journal_id'] = slip.journal_id.id
                                dict[str(credit_account_id)+analityc_account_id]['date'] = date
                                dict[str(credit_account_id)+analityc_account_id]['debit'] = 0 #amount < 0.0 and -amount or 0.0
                                dict[str(credit_account_id)+analityc_account_id]['credit'] = round(amount > 0.0 and amount or 0.0)
                                dict[str(credit_account_id)+analityc_account_id][
                                    'analytic_account_id'] = analityc_account_id if analityc_account_id != 0 else False
                                #dict[str(credit_account_id)+analityc_account_id]['tax_line_id'] = line.salary_rule_id.account_tax_id.id
                        # we regroup others by account
                        else:
                            if credit_account_id in dict:
                                dict[credit_account_id]['credit'] += round(amount > 0.0 and amount or 0.0)
                                dict[credit_account_id]['debit'] += 0 #round(amount < 0.0 and -amount or 0.0)
                            else:
                                dict[credit_account_id] = {}
                                dict[credit_account_id]['name'] = line.name
                                dict[credit_account_id]['partner_id'] = False #line._get_partner_id(credit_account=False)
                                dict[credit_account_id]['account_id'] = credit_account_id
                                dict[credit_account_id]['journal_id'] = slip.journal_id.id
                                dict[credit_account_id]['date'] = date
                                dict[credit_account_id]['debit'] = 0 #amount < 0.0 and -amount or 0.0
                                dict[credit_account_id]['credit'] = round(amount > 0.0 and amount or 0.0)
                                dict[credit_account_id][
                                    'analytic_account_id'] = False
                                #dict[credit_account_id]['tax_line_id'] = line.salary_rule_id.account_tax_id.id
                        credit_sum += round(amount > 0.0 and amount or 0.0 - amount < 0.0 and -amount or 0.0)
                    elif credit_account_id and line.total < 0:
                        amount = abs(amount)
                        if line.salary_rule_id.account_credit.code[:3] == "421":
                            index_deb += 1
                            dict[str(debit_account_id) + index_deb] = {}
                            dict[str(debit_account_id) + index_deb]['name'] = line.name
                            dict[str(debit_account_id) + index_deb]['partner_id'] = line._get_partner_id(credit_account=True)
                            dict[str(debit_account_id) + index_deb]['account_id'] = credit_account_id
                            dict[str(debit_account_id) + index_deb]['journal_id'] = slip.journal_id.id
                            dict[str(debit_account_id) + index_deb]['date'] = date
                            dict[str(debit_account_id) + index_deb]['debit'] = round(amount > 0.0 and amount or 0.0)
                            dict[str(debit_account_id) + index_deb]['credit'] = 0
                            dict[str(debit_account_id) + index_deb]['analytic_account_id'] = False
                            #dict[str(debit_account_id) + index_deb]['tax_line_id'] = line.salary_rule_id.account_tax_id.id
                        # we regroup by account and analytic account started by 7 or 6
                        elif line.salary_rule_id.account_credit.code[:1] in ["7", "6"]:
                            if str(debit_account_id)+analityc_account_id in dict:
                                dict[str(debit_account_id)+analityc_account_id]['debit'] += round(amount > 0.0 and amount or 0.0)
                            else:
                                dict[str(debit_account_id)+analityc_account_id] = {}
                                dict[str(debit_account_id)+analityc_account_id]['name'] = line.name
                                dict[str(debit_account_id)+analityc_account_id]['partner_id'] = False
                                dict[str(debit_account_id)+analityc_account_id]['account_id'] = credit_account_id
                                dict[str(debit_account_id)+analityc_account_id]['journal_id'] = slip.journal_id.id
                                dict[str(debit_account_id)+analityc_account_id]['date'] = date
                                dict[str(debit_account_id)+analityc_account_id]['debit'] = round(amount > 0.0 and amount or 0.0)
                                dict[str(debit_account_id)+analityc_account_id]['credit'] = 0
                                dict[str(debit_account_id)+analityc_account_id][
                                    'analytic_account_id'] = analityc_account_id if analityc_account_id != '0' else False
                                #dict[str(debit_account_id)+analityc_account_id]['tax_line_id'] = line.salary_rule_id.account_tax_id.id
                        # we regroup others by account
                        else:
                            if debit_account_id in dict:
                                dict[debit_account_id]['debit'] += round(amount > 0.0 and amount or 0.0)
                            else:
                                dict[debit_account_id] = {}
                                dict[debit_account_id]['name'] = line.name
                                dict[debit_account_id]['partner_id'] = False
                                dict[debit_account_id]['account_id'] = credit_account_id
                                dict[debit_account_id]['journal_id'] = slip.journal_id.id
                                dict[debit_account_id]['date'] = date
                                dict[debit_account_id]['debit'] = round(amount > 0.0 and amount or 0.0)
                                dict[debit_account_id]['credit'] = 0
                                dict[debit_account_id][
                                    'analytic_account_id'] = False
                                #dict[debit_account_id]['tax_line_id'] = line.salary_rule_id.account_tax_id.id
                        debit_sum += round(amount > 0.0 and amount or 0.0 - amount < 0.0 and -amount or 0.0)

            if float_compare(credit_sum, debit_sum, precision_digits=precision) == -1:
                acc_id = slip.journal_id.default_account_id.id
                if not acc_id:
                    raise UserError(
                        _('The Expense Journal "%s" has not properly configured the Credit Account!') % (
                            slip.journal_id.name))
                adjust_credit = (0, 0, {
                    'name': _('Adjustment Entry'),
                    'partner_id': False,
                    'account_id': acc_id,
                    'journal_id': slip.journal_id.id,
                    'date': date,
                    'debit': 0.0,
                    'credit': debit_sum - credit_sum,
                })
                line_ids.append(adjust_credit)

            elif float_compare(debit_sum, credit_sum, precision_digits=precision) == -1:
                acc_id = slip.journal_id.default_account_id.id
                if not acc_id:
                    raise UserError(
                        _('The Expense Journal "%s" has not properly configured the Debit Account!') % (
                            slip.journal_id.name))
                adjust_debit = (0, 0, {
                    'name': _('Adjustment Entry'),
                    'partner_id': False,
                    'account_id': acc_id,
                    'journal_id': slip.journal_id.id,
                    'date': date,
                    'debit': credit_sum - debit_sum,
                    'credit': 0.0,
                })
                line_ids.append(adjust_debit)


        for key, value in dict.items():
            move_line = (0, 0, {
                'name': dict[key]['name'],
                'partner_id': dict[key]['partner_id'],
                'account_id': dict[key]['account_id'],
                'journal_id': dict[key]['journal_id'],
                'date': dict[key]['date'],
                'debit': dict[key]['debit'],
                'credit': dict[key]['credit'],
                'analytic_account_id': dict[key]['analytic_account_id'],
            })
            line_ids.append(move_line)


        name = _('Payslips of  Batch %s') % self.name
        move_dict = {
            'narration': name,
            'ref': self.name,
            'journal_id': self.journal_id.id,
            'date': date,
            'line_ids': line_ids
        }

        move = self.env['account.move'].create(move_dict)
        move.write({'batch_id': slip.payslip_run_id.id})
        for slip_obj in self.slip_ids:
            if slip_obj.state != 'done':
                provision_amount = 0.0
                provision_fin_contrat = 0.0
                provision_amount += sum(line.total for line in slip_obj.line_ids if line.code == 'C1150')
                provision_fin_contrat += sum(line.total for line in slip_obj.line_ids if line.code == 'C1160')
                slip_obj.contract_id._get_droit(provision_amount,provision_fin_contrat)
                slip_obj.write({'move_id': move.id, 'date': date, 'state': 'done'})
        self.write({'state': 'close'})