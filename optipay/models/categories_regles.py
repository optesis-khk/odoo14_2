# Copyright 2015 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from odoo import api, fields, models, _
from odoo import SUPERUSER_ID
from odoo.exceptions import ValidationError


class HrCategory_inherit(models.Model):
    _inherit = 'hr.salary.rule.category'
  
    
    #add by diw
    
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id,  String="company")
    
    
