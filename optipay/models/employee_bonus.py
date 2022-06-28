# -*- coding: utf-8 -*-
###################################################################################
#    A part of OpenHRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Treesa Maria Jude (<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################
import time
from datetime import datetime, date, time as t
from dateutil import relativedelta
from odoo.tools.misc import format_date
from odoo.tools import float_compare, float_is_zero
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class EmployeeBonus(models.Model):
    _name = 'hr.employee.bonus'
    _description = 'Employee Bonus'

    #name = fields.Char(readonly=True, compute="_get_name")

    salary_rule_id = fields.Many2one('hr.salary.rule', string="Salary Rule", required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee')
    amount = fields.Float(string='Amount', required=True)
    date_from = fields.Date(string='Date From',
                            default=time.strftime('%Y-%m-%d'), required=True)
    date_to = fields.Date(string='Date To',
                          default=str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],
                          required=True)
    state = fields.Selection([('active', 'Active'),
                              ('expired', 'Expired'), ],
                             default='active', string="State", compute='get_status')
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    contract_id = fields.Many2one('hr.contract', string='Contract')
    
    #@api.onchange('employee_id')
    #def _get_name(self):
     #   for rec in self:
      #      if rec.employee_id:
       #         rec.name = '%s - %s ' % ('Element Variable ' + rec.employee_id.name or '', format_date(rec.env, rec.date_from, date_format="MMMM y"))

    def get_status(self):
        current_datetime = datetime.now()
        for i in self:
            x = datetime.strptime(str(i.date_from), '%Y-%m-%d')
            y = datetime.strptime(str(i.date_to), '%Y-%m-%d')
            if x <= current_datetime <= y:
                i.state = 'active'
            else:
                i.state = 'expired'
                
    @api.onchange('contract_id')
    def onchange_contract(self):
        list = []
        for rec in self.contract_id.structure_type_id.struct_ids:
            list.append(rec.id)
        return {'domain': {'salary_rule': [('struct_id', 'in', list)]}}


class OptesisRelation(models.Model):
    _name = 'optesis.relation'
    _description = "les relations familiales"

    type = fields.Selection([('conjoint', 'Conjoint'), ('conjoint2', 'Conjoint 2'), ('conjoint3', 'Conjoint 3'), ('conjoint4', 'Conjoint 4'), ('enfant', 'Enfant'), ('autre', 'Autres parents')],
                            'Type de relation')
    nom = fields.Char('Nom')
    prenom = fields.Char('Prenom')
    birth = fields.Datetime('Date de naissance')
    date_mariage = fields.Datetime('Date de mariage')
    salari = fields.Boolean('Salarie', default=0)
    employee_id = fields.Many2one('hr.employee')


class HrPayslipRunInherit(models.Model):
    _inherit = 'hr.payslip.run'
    
    journal_id = fields.Many2one('account.journal', 'Salary Journal', readonly=False)
    
    #add by mpb
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validate', 'Validé'),
        ('close', 'Done'),
    ], string='Status', index=True, readonly=True, copy=False, default='draft')

    
    def validate_payslip(self):
        for slip in self.slip_ids:
            if slip.state != 'validate' and slip.state != 'done':
                slip.action_payslip_validate()
        self.write({'state': 'validate'})
        
        #fin


    


class SaveAllocMensual(models.Model):
    """class for saving alloc mensuel """
    _name = "optesis.save.alloc.mensuel"
    _description = "optesis save alloc mensuel class"

    slip_id = fields.Many2one('hr.payslip')
    cumul_mensuel = fields.Float()
    # -*- coding: utf-8 -*-
###################################################################################
#    A part of OpenHRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Treesa Maria Jude (<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################
import time
from datetime import datetime, date, time as t
from dateutil import relativedelta
from odoo.tools.misc import format_date
from odoo.tools import float_compare, float_is_zero
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class EmployeeBonus(models.Model):
    _name = 'hr.employee.bonus'
    _description = 'Employee Bonus'

    #name = fields.Char(readonly=True, compute="_get_name")
    
    salary_rule_id = fields.Many2one('hr.salary.rule', string="Salary Rule", required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee')
    amount = fields.Float(string='Amount', required=True)
    date_from = fields.Date(string='Date From',
                            default=time.strftime('%Y-%m-%d'), required=True)
    date_to = fields.Date(string='Date To',
                          default=str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],
                          required=True)
    state = fields.Selection([('active', 'Active'),
                              ('expired', 'Expired'), ],
                             default='active', string="State", compute='get_status')
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    contract_id = fields.Many2one('hr.contract', string='Contract')
    
    #@api.onchange('employee_id')
    #def _get_name(self):
     #   for rec in self:
      #      if rec.employee_id:
       #         rec.name = '%s - %s ' % ('Element Variable ' + rec.employee_id.name or '', format_date(rec.env, rec.date_from, date_format="MMMM y"))

    def get_status(self):
        current_datetime = datetime.now()
        for i in self:
            x = datetime.strptime(str(i.date_from), '%Y-%m-%d')
            y = datetime.strptime(str(i.date_to), '%Y-%m-%d')
            if x <= current_datetime <= y:
                i.state = 'active'
            else:
                i.state = 'expired'
                
    @api.onchange('contract_id')
    def onchange_contract(self):
        list = []
        for rec in self.contract_id.structure_type_id.struct_ids:
            list.append(rec.id)
        return {'domain': {'salary_rule': [('struct_id', 'in', list)]}}


class OptesisRelation(models.Model):
    _name = 'optesis.relation'
    _description = "les relations familiales"

    type = fields.Selection([('conjoint', 'Conjoint'), ('conjoint2', 'Conjoint 2'), ('conjoint3', 'Conjoint 3'), ('conjoint4', 'Conjoint 4'), ('enfant', 'Enfant'), ('autre', 'Autres parents')],
                            'Type de relation')
    nom = fields.Char('Nom')
    prenom = fields.Char('Prenom')
    birth = fields.Datetime('Date de naissance')
    date_mariage = fields.Datetime('Date de mariage')
    salari = fields.Boolean('Salarie', default=0)
    employee_id = fields.Many2one('hr.employee')


class HrPayslipRunInherit(models.Model):
    _inherit = 'hr.payslip.run'
    
    journal_id = fields.Many2one('account.journal', 'Salary Journal', readonly=False)
    
    #add by mpb
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validate', 'Validé'),
        ('close', 'Done'),
    ], string='Status', index=True, readonly=True, copy=False, default='draft')

    
    def validate_payslip(self):
        for slip in self.slip_ids:
            if slip.state != 'validate' and slip.state != 'done':
                slip.action_payslip_validate()
        self.write({'state': 'validate'})
        
        #fin


    


class SaveAllocMensual(models.Model):
    """class for saving alloc mensuel """
    _name = "optesis.save.alloc.mensuel"
    _description = "optesis save alloc mensuel class"

    slip_id = fields.Many2one('hr.payslip')
    cumul_mensuel = fields.Float()
    nbj_alloue = fields.Float()

