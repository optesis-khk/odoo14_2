# -*- coding: utf-8 -*-
# by khk
from odoo import fields, models,api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval


class HrSalaryRuleInherit(models.Model):
    _inherit = 'hr.salary.rule'

    is_prorata = fields.Boolean(string='Prorata', default=True,
                                help="Used to check if we apply prorata")

    simulate_ok = fields.Boolean(string='Peut être simulée', default=False,
                                 help="Used to check if the salary rule can be used for simulation")
    
    #add by mpb
    company_id = fields.Many2one('res.company', 'Company', copy=False)
    struct_id = fields.Many2one('hr.payroll.structure', string="Salary Structure", required=False)
    child_ids = fields.One2many('hr.salary.rule', 'parent_rule_id', string='Child Salary Rule', copy=True)
    parent_rule_id = fields.Many2one('hr.salary.rule', string='Parent Salary Rule', index=True)
    input_ids = fields.One2many('hr.rule.input', 'input_id', string='Inputs', copy=True)
    register_id = fields.Many2one('hr.contribution.register', string='Contribution Register',
        help="Eventual third party involved in the salary payment of the employees.")
    
    
    def _recursive_search_of_rules(self):
        """
        @return: returns a list of tuple (id, sequence) which are all the children of the passed rule_ids
        """
        children_rules = []
        for rule in self.filtered(lambda rule: rule.child_ids):
            children_rules += rule.child_ids._recursive_search_of_rules()
        return [(rule.id, rule.sequence) for rule in self] + children_rules
    
#add by mpb
class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'
  

    
    @api.model
    def _get_parent(self):
        return self.env.ref('hr_payroll.structure_base', False)

    name = fields.Char(required=True)
    code = fields.Char(string='Reference')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    note = fields.Text(string='Description')
    parent_id = fields.Many2one('hr.payroll.structure', string='Parent', default=_get_parent)
    children_ids = fields.One2many('hr.payroll.structure', 'parent_id', string='Children', copy=True)
    rule_ids = fields.Many2many('hr.salary.rule', 'hr_structure_salary_rule_rel', 'struct_id', 'rule_id', string='Salary Rules')
    type_id = fields.Many2one('hr.payroll.structure.type', required = False)

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create a recursive salary structure.'))

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {}, code=_("%s (copy)") % (self.code))
        return super(HrPayrollStructure, self).copy(default)

    def get_all_rules(self):
        """
        @return: returns a list of tuple (id, sequence) of rules that are maybe to apply
        """
        all_rules = []
        for struct in self:
            all_rules += struct.rule_ids._recursive_search_of_rules()
        return all_rules

    def _get_parent_structure(self):
        parent = self.mapped('parent_id')
        if parent:
            parent = parent._get_parent_structure()
        return parent + self

#add by mpb
class HrRuleInput(models.Model):
    _name = 'hr.rule.input'
    _description = 'Salary Rule Input'

    name = fields.Char(string='Description', required=True)
    code = fields.Char(required=True, help="The code that can be used in the salary rules")
    input_id = fields.Many2one('hr.salary.rule', string='Salary Rule Input', required=True)
    company_id = fields.Many2one('res.company', 'Company', copy=False,
                                 default=lambda self: self.env.user.company_id)
    
class HrContributionRegister(models.Model):
    _name = 'hr.contribution.register'
    _description = 'Contribution Register'

    company_id = fields.Many2one('res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get())
    partner_id = fields.Many2one('res.partner', string='Partner')
    name = fields.Char(required=True)
    register_line_ids = fields.One2many('hr.payslip.line', 'register_id',
        string='Register Line', readonly=True)
    note = fields.Text(string='Description')