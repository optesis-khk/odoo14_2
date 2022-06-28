#add diw
import time
from datetime import datetime, date, time as t
from odoo import models, fields, api, _
from odoo.tools.float_utils import float_round

class hr_employee_new(models.Model):
    _inherit = 'hr.employee'
    
    contract_cours = fields.Boolean(string='Contrat en cours', store=True, compute='_compute_contract_cours')
   

   
    @api.depends('contract_id', 'contract_id.state')
    def _compute_contract_cours(self):
        for employee in self:
            if (employee.contract_id.state) == 'open':                        
                employee.contract_cours = True
                                    
    state_contract = fields.Selection([
        ('draft', 'Nouveau'),
        ('open', 'Open'),
        ('pending', 'To Renew'),
        ('close', 'Expired'),
        ('cancel', 'Cancelled')
    ], string='Status', compute="_onchange_state_contract")
        
   
    
    @api.onchange('contract_id', 'contract_id.state')
    def _onchange_state_contract(self):
        for r in self:
            r.state_contract = r.contract_id.state
           
        
    #date debut du contrat pour le formule provision de retraite
    date_start_contrat = fields.Date('Date début contrat', compute="_onchangedate")
    
    @api.onchange('employee_id')
    def _onchangedate(self):
        for r in self:
            contracts = self.env['hr.contract'].search([('employee_id', '=', r.id)], order='id desc', limit=1)
            if contracts:
                for rec in contracts:
                    r.date_start_contrat = rec.date_start
            
             #lié employée à contrat
                
    #nombre jour alloué pour la société
    nbj_alloue = fields.Float(related='company_id.nbj_alloue',string="Nombre de jour alloue", default="2.0", readonly=False)
    
    nbj_alloue_2ans = fields.Float(compute='_nbj_reset_after_2years')

    #nombre jour alloué pour la société pendant 2 ans
   
    def _nbj_reset_after_2years(self):
        for nbj in self:
            nbj.nbj_alloue_2ans = nbj.nbj_alloue * 24 
    
   
    #pour un employé on calcule le nbre jr aquis validé par un responsable
    nbj_aquis_sans_condition = fields.Float(compute='_number_of_days_aquis_valider_sans_condition')
    
    
    def _number_of_days_aquis_valider_sans_condition(self):
        all_leaves = self.env['hr.leave.report'].read_group([
            ('employee_id', 'in', self.ids),
            ('state', '=', 'validate'),
            ('leave_type', '=', 'allocation')
        ], fields=['number_of_days', 'employee_id'], groupby=['employee_id'])
        mapping = dict([(leave['employee_id'][0], leave['number_of_days']) for leave in all_leaves])
        for employee in self:
            employee.nbj_aquis_sans_condition = float_round(mapping.get(employee.id, 0), precision_digits=2)

    #pour un employé Le cumul des droits acquis doit être infieur à 2 ans. Le salarié perd le jours non pris au bout de 2 ans
    nbj_aquis = fields.Float(compute='_number_of_days_aquis_valider')

    @api.depends('nbj_aquis_sans_condition','nbj_alloue_2ans')
    def _number_of_days_aquis_valider(self):
        for employee in self:
            if employee.nbj_aquis_sans_condition < employee.nbj_alloue_2ans:
                employee.nbj_aquis = employee.nbj_aquis_sans_condition
            else:
                employee.nbj_aquis = employee.nbj_alloue_2ans

    nbj_pris = fields.Float("Nombre de jour pris",compute='_compute_number_of_days_pris_new')

    
    def _compute_number_of_days_pris_new(self):
        all_leaves = self.env['hr.leave.report'].read_group([
            ('employee_id', 'in', self.ids),
            ('state', '=', 'validate'),
            ('leave_type', '=', 'request')
        ], fields=['number_of_days', 'employee_id'], groupby=['employee_id'])
        mapping = dict([(leave['employee_id'][0], leave['number_of_days']) for leave in all_leaves])
        for employee in self:
            employee.nbj_pris = float_round(mapping.get(employee.id, 0), precision_digits=2)
            
            #fin diw
            
            



   
            