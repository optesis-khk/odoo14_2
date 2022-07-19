from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _name = "purchase.order"
    _inherit = "purchase.order"

    crossovered_budget_line = fields.One2many('budget.lines', 'p_analytic_account_id','Budgets', compute='_get_lines', store="True")
    amount_total_to_word = fields.Char(compute='_compute_amount_total_to_word', store=True)

    to_19_fr = ( u'zĂŠro',  'un',   'deux',  'trois', 'quatre',   'cinq',   'six',
          'sept', 'huit', 'neuf', 'dix',   'onze', 'douze', 'treize',
          'quatorze', 'quinze', 'seize', 'dix-sept', 'dix-huit', 'dix-neuf' )
    tens_fr  = ( 'vingt', 'trente', 'quarante', 'Cinquante', 'Soixante', 'Soixante-dix', 'Quatre-vingts', 'Quatre-vingt Dix')
    denom_fr = ( '',
              'Mille',     'Millions',         'Milliards',       'Billions',       'Quadrillions',
              'Quintillion',  'Sextillion',      'Septillion',    'Octillion',      'Nonillion',
              'DĂŠcillion',    'Undecillion',     'Duodecillion',  'Tredecillion',   'Quattuordecillion',
              'Sexdecillion', 'Septendecillion', 'Octodecillion', 'Icosillion', 'Vigintillion' )

    state = fields.Selection(selection_add=[
        ('finance_approval', 'Waiting Finance Approval'),
        ('director_approval', 'Waiting Director Approval'),
        ('refuse', 'Refuse')],
        string='Status',
    )
    po_refuse_user_id = fields.Many2one(
        'res.users',
        string="Refused By",
        readonly = True,
    )
    po_refuse_date = fields.Date(
        string="Refused Date",
        readonly=True
    )
    refuse_reason_note = fields.Text(
        string="Refuse Reason",
        readonly=True
    )
    dept_manager_id = fields.Many2one(
        'res.users',
        string='Purchase/Department Manager',
        states={'done':[('readonly',True)], 'cancel':[('readonly',True)]}
    )
    finance_manager_id = fields.Many2one(
        'res.users',
        string='Finance Manager',
        states={'done':[('readonly',True)], 'cancel':[('readonly',True)]}
    )
    director_manager_id = fields.Many2one(
        'res.users',
        string='Director Manager',
        states={'done':[('readonly',True)], 'cancel':[('readonly',True)]}
    )

    confirm_manager_id = fields.Many2one(
        'res.users',
        string='Confirm Manager',
        readonly=True,
    )

    approve_dept_manager_id = fields.Many2one(
        'res.users',
        string='Approve Department Manager',
        readonly=True,
    )
    approve_finance_manager_id = fields.Many2one(
        'res.users',
        string='Approve Finance Manager',
        readonly=True,
    )
    approve_director_manager_id = fields.Many2one(
        'res.users',
        string='Approve Director Manager',
        readonly=True,
    )

    manager_confirm_date = fields.Datetime(
        string='Confirm Manager Date',
        readonly=True,
    )

    dept_manager_approve_date = fields.Datetime(
        string='Department Manager Approve Date',
        readonly=True,
    )
    finance_manager_approve_date = fields.Datetime(
        string='Finance Manager Approve Date',
        readonly=True,
    )
    director_manager_approve_date = fields.Datetime(
        string='Director Manager Approve Date',
        readonly=True,
    )
    purchase_user_id = fields.Many2one(
        'res.users',
        string='Purchase User',
        compute='_set_purchase_user',
        store=True,
    )

    @api.depends('state')
    def _set_purchase_user(self):
        for rec in self:
            if rec.state == 'draft' or 'sent':
                rec.purchase_user_id = self.env.user.id,

    @api.model
    def _get_finance_validation_amount(self):
#         finance_validation_amount = self.env['ir.values'].get_default('purchase.config.settings', 'finance_validation_amount')
        finance_validation_amount = self.env.user.company_id.finance_validation_amount
        return finance_validation_amount

    @api.model
    def _get_director_validation_amount(self):
#         director_validation_amount = self.env['ir.values'].get_default('purchase.config.settings', 'director_validation_amount')
        director_validation_amount = self.env.user.company_id.director_validation_amount
        return director_validation_amount

    @api.model
    def _get_three_step_validation(self):
#         three_step_validation = self.env['ir.values'].get_default('purchase.config.settings', 'three_step_validation')
        three_step_validation = self.env.user.company_id.three_step_validation
        return three_step_validation

    @api.model
    def _get_email_template_id(self):
#         email_template_id = self.env['ir.values'].get_default('purchase.config.settings', 'email_template_id')
        email_template_id = self.env.user.company_id.email_template_id
        return email_template_id

    @api.model
    def _get_refuse_template_id(self):
#         refuse_template_id = self.env['ir.values'].get_default('purchase.config.settings', 'refuse_template_id')
        refuse_template_id = self.env.user.company_id.refuse_template_id
        return refuse_template_id

    def _convert_nn_fr(self, val):
        """ convert a value < 100 to French
        """
        if val < 20:
            return self.to_19_fr[val]
        for (dcap, dval) in ((k, 20 + (10 * v)) for (v, k) in enumerate(self.tens_fr)):
            if dval + 10 > val:
                if val % 10:
                    return dcap + '-' + self.to_19_fr[val % 10]
                return dcap

    def _convert_nnn_fr(self, val):
        """ convert a value < 1000 to french

            special cased because it is the level that kicks
            off the < 100 special case.  The rest are more general.  This also allows you to
            get strings in the form of 'forty-five hundred' if called directly.
        """
        word = ''
        (mod, rem) = (val % 100, val // 100)
        if rem > 0:
            word = self.to_19_fr[rem] + ' Cent'
            if mod > 0:
                word += ' '
        if mod > 0:
            word += self._convert_nn_fr(mod)
        return word

    def french_number(self, val):
        if val < 100:
            return self._convert_nn_fr(val)
        if val < 1000:
             return self._convert_nnn_fr(val)
        for (didx, dval) in ((v - 1, 1000 ** v) for v in range(len(self.denom_fr))):
            if dval > val:
                mod = 1000 ** didx
                l = val // mod
                r = val - (l * mod)
                ret = self._convert_nnn_fr(l) + ' ' + self.denom_fr[didx]
                if r > 0:
                    ret = ret + ', ' + self.french_number(r)
                return ret

    def amount_to_text_fr(self, number, currency):
        number = '%.2f' % number
        units_name = currency
        list = str(number).split('.')
        start_word = self.french_number(abs(int(list[0])))
        end_word = self.french_number(int(list[1]))
        cents_number = int(list[1])
        cents_name = (cents_number > 1) and ' Cents' or ' Cent'
        final_result = start_word +' '+units_name+' '+ end_word +' '+cents_name
        return final_result

    
    @api.depends('amount_total')
    def _compute_amount_total_to_word(self):
        for record in self:
            record.amount_total_to_word = record.amount_to_text_fr(record.amount_total, currency='')[:-10]

    
    @api.constrains('crossovered_budget_line','order_line')
    def _control_budget_date(self):
        _logger.info("entrer dans fonction")
        for record in self:
            ok = False
            for crossovered_line in record.crossovered_budget_line:
                for line in record.order_line:
                    if line.account_analytic_id == crossovered_line.analytic_account_id and line.account_id in crossovered_line.general_budget_id.account_ids and (line.date_planned.date() >= crossovered_line.date_from and line.date_planned.date() <= crossovered_line.date_to):
                        ok = True
                        break
            if not ok:
                raise ValidationError(_("La date prevu n'est pas comprise dans la plage du poste budgetaire"))
        return True

    
    def button_cancel(self):
        for order in self:
            for inv in order.invoice_ids:
                if inv and inv.state not in ('cancel', 'draft'):
                    raise UserError(_("Unable to cancel this purchase order. You must first cancel the related vendor bills."))
        self.env['account.budget.line'].search([('ref','=',order.name)]).unlink()
        self.write({'state': 'cancel'})

    
    @api.depends('order_line')
    def _get_lines(self):
        temoin = []
        for line in self.order_line:
            date = line.date_planned.date()
            budgets = self.env['budget.lines'].search([('analytic_account_id','=',line.account_analytic_id.id),('general_budget_id.account_ids','=',line.account_id.id),('date_from', '<', date),('date_to', '>', date)])
            if budgets:
                for budget in budgets:
                    if budget.id not in temoin:
                        _logger.info("budget_id => %s , temoin => %s",budget.id, temoin)
                        self.crossovered_budget_line += budget
                        temoin.append(budget.id)
    
    def write(self, vals):
        vals, partner_vals = self._write_partner_values(vals)
        if vals.get('state') == 'to approve':
            if not self.dept_manager_id:
                raise UserError(_('Please select Purchase/Department Manager.'))
            else:
                email_to = self.dept_manager_id.email
                email_template_id = self._get_email_template_id()
                ctx = self._context.copy()
                ctx.update({'name': self.dept_manager_id.name})
                #reminder_mail_template.with_context(ctx).send_mail(user)
                if email_template_id:
                    email_template_id.with_context(ctx).send_mail(self.id, email_values={'email_to': email_to, 'subject': _('Purchase Order: ') + self.name + _(' (Approval Waiting)')})
        
        if vals.get('state') == 'finance_approval':
            if not self.finance_manager_id:
                raise UserError(_('Please select Finance Manager.'))
            else:
                email_to = self.finance_manager_id.email
                email_template_id = self._get_email_template_id()
#                     mail = self.env['mail.template'].browse(email_template_id)
                ctx = self._context.copy()
                ctx.update({'name': self.finance_manager_id.name})
                #mail.send_mail(self.id, email_values={'email_to': email_to, 'subject': "Finance Manager Approve"})
                if email_template_id:
                    email_template_id.with_context(ctx).send_mail(self.id, email_values={'email_to': email_to, 'subject': _('Purchase Order: ') + self.name + _(' (Approval Waiting)')})
        
        if vals.get('state') == 'director_approval':
            if not self.director_manager_id:
                raise UserError(_('Please select Director Manager.'))
            else:
                email_to = self.director_manager_id.email
                email_template_id = self._get_email_template_id()
#                     mail = self.env['mail.template'].browse(email_template_id)
                ctx = self._context.copy()
                ctx.update({'name': self.director_manager_id.name})
                #mail.send_mail(self.id, email_values={'email_to': email_to, 'subject': "Director Manager Approve"})
                if email_template_id:
                    email_template_id.with_context(ctx).send_mail(self.id, email_values={'email_to': email_to, 'subject': _('Purchase Order: ') + self.name + _(' (Approval Waiting)')})
        
        if self.state == 'draft' and vals.get('state') == 'purchase':
            self.confirm_manager_id = self.env.user.id
            self.manager_confirm_date = fields.Datetime.now()
        elif self.state == 'draft' and vals.get('state') == 'to approve':
            self.confirm_manager_id = self.env.user.id
            self.manager_confirm_date = fields.Datetime.now()

        if self.state == 'to approve' and vals.get('state') == 'purchase':
            self.approve_dept_manager_id = self.env.user.id
            self.dept_manager_approve_date = fields.Datetime.now()
        elif self.state == 'to approve' and vals.get('state') == 'finance_approval':
            self.approve_dept_manager_id = self.env.user.id
            self.dept_manager_approve_date = fields.Datetime.now()

        if self.state == 'finance_approval' and vals.get('state') == 'purchase':
            self.approve_finance_manager_id = self.env.user.id
            self.finance_manager_approve_date = fields.Datetime.now()
        elif self.state == 'finance_approval' and vals.get('state') == 'director_approval':
            self.approve_finance_manager_id = self.env.user.id
            self.finance_manager_approve_date = fields.Datetime.now()

        if self.state == 'director_approval' and vals.get('state') == 'purchase':
            self.approve_director_manager_id = self.env.user.id
            self.director_manager_approve_date = fields.Datetime.now()
        res = super().write(vals)
        if partner_vals:
            self.partner_id.sudo().write(partner_vals)  # Because the purchase user doesn't have write on `res.partner`
        return res
    
    validator_finance_approval = fields.Many2one(comodel_name='res.users', string='finance validation user')
    
    def button_finance_approval(self):
        finance_validation_amount = self._get_finance_validation_amount()
        director_validation_amount = self._get_director_validation_amount()
        amount_total = self.currency_id.compute(self.amount_total, self.company_id.currency_id)
        for order in self:
            #order.check_finance_approval = True #by diw
            if amount_total > director_validation_amount:
                order.write({'state': 'director_approval',  'validator_finance_approval': self.env.user.id,})
            if amount_total < director_validation_amount:
                order.write({'state': 'director_approval',  'validator_finance_approval': self.env.user.id,})
                order.button_director_approval()
        return True

    
    validator_director_approval = fields.Many2one(comodel_name='res.users', string='director_approval validation user')
    
    def button_director_approval(self):
        for order in self:
            #order.check_director_approv = True
            order.with_context(call_super=True).button_approve()
            order.write({'validator_director_approval': self.env.user.id,})
        return True


    order_validator_id_confirm = fields.Many2one(comodel_name='res.users', string='user qui confirm la commande', help='The user validating the order.')
    
    def button_confirm(self):
        for order in self:
            order._add_supplier_to_product()
            # Deal with double validation process
            if order._approval_allowed():
            #\
                    #or order.user_has_groups('purchase.group_purchase_manager'):
                order.write({
                    'order_validator_id_confirm': self.env.user.id,
                    
                })
                order.button_approve()
            else:
                order.write({
                    'state': 'to approve',
                    'order_validator_id_confirm': self.env.user.id,
                    
                })
                #print("Send message 1")
                if order.partner_id not in order.message_partner_ids:
                    order.message_subscribe([order.partner_id.id])
                
        return {}

    #by diw
    
    order_validator_id_approve = fields.Many2one(comodel_name='res.users', string='user qui approuve la commande', help='The user validating the order.') 
    
    def button_approve(self, force=False):
        if self._context.get('call_super', False):
            if self.crossovered_budget_line:
                for crossovered_line in self.crossovered_budget_line:
                    self.order_line.create_budget_lines(crossovered_line.general_budget_id.id, crossovered_line.analytic_account_id, crossovered_line.general_budget_id.account_ids)
            return super(PurchaseOrder, self).button_approve()

        three_step_validation = self._get_three_step_validation()
        if not three_step_validation:
            if self.crossovered_budget_line:
                for crossovered_line in self.crossovered_budget_line:
                    self.order_line.create_budget_lines(crossovered_line.general_budget_id.id, crossovered_line.analytic_account_id, crossovered_line.general_budget_id.account_ids)
            return super(PurchaseOrder, self).button_approve()

        amount_total = self.currency_id.compute(self.amount_total, self.company_id.currency_id)
        po_double_validation_amount = self.env.user.company_id.currency_id.compute(self.company_id.po_double_validation_amount, self.currency_id)
        finance_validation_amount = self._get_finance_validation_amount()
        director_validation_amount = self._get_director_validation_amount()

        if three_step_validation and not self._context.get('call_super', False):
             for order in self:
                if amount_total > po_double_validation_amount and order.state != 'to approve':
                   
                    order.write({'state': 'to approve'})
               
                elif amount_total < finance_validation_amount and order.state == 'to approve':
                    return super(PurchaseOrder, self).button_approve()
                elif order.state == 'to approve':
                    order.write({'state': 'finance_approval', 'order_validator_id_approve': self.env.user.id,})

                else:
                    return super(PurchaseOrder, self).button_approve()
        return True
    
    def button_refuse(self):
        for order in self:
            order.write({'state': 'refuse'})
        return True

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    account_id = fields.Many2one('account.account', string='Compte',
        required=True, domain=[('deprecated', '=', False)],
        help="The income or expense account related to the selected product.")

    #available =  fields.Float(string='Montant budget restant',compute="_compute_value", digits=0 , default="0", store="True")

    #planned =  fields.Float(string='Montant budget prevu',compute="_compute_value", digits=0 , default="0", store="True")

    analytic_budget_ids = fields.One2many('account.budget.line', 'move_id', string='Account Budget lines')

    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        if not self.product_id:
            return result

        # Reset date, price and quantity since _onchange_quantity will provide default values
        self.date_planned = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self.price_unit = self.product_qty = 0.0
        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        self.account_id = self.product_id.property_account_expense_id.id or self.product_id.categ_id.property_account_expense_categ_id.id
        result['domain'] = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}

        product_lang = self.product_id.with_context({
            'lang': self.partner_id.lang,
            'partner_id': self.partner_id.id,
        })
        self.name = product_lang.display_name
        if product_lang.description_purchase:
            self.name += '\n' + product_lang.description_purchase

        fpos = self.order_id.fiscal_position_id
        if self.env.uid == SUPERUSER_ID:
            company_id = self.env.user.company_id.id
            self.taxes_id = fpos.map_tax(self.product_id.supplier_taxes_id.filtered(lambda r: r.company_id.id == company_id))
        else:
            self.taxes_id = fpos.map_tax(self.product_id.supplier_taxes_id)

        self._suggest_quantity()
        self._onchange_quantity()

        return result

    
    @api.onchange('account_id','account_analytic_id','date_planned')
    def _onchange_value(self):
        for record in self:
            if record.account_id and record.account_analytic_id:
                ok = False
                for line in record.account_analytic_id.budget_line:
                    if (record.account_id.id in line.general_budget_id.account_ids.ids) and record.date_planned.date() >= line.date_from and record.date_planned.date() <= line.date_to:
                        ok = True
                        break
                if not ok:
                    raise UserError('Pas de budget prevu pour effectuer cet achat')


    @api.onchange('price_subtotal','account_analytic_id')
    def _budget_control(self):
        if self.price_subtotal and self.account_analytic_id:
            ok = 0
            for line in self.account_analytic_id.budget_line:
                if (self.account_id.id in line.general_budget_id.account_ids.ids) and (self.date_planned.date() >= line.date_from) and (self.date_planned.date() <= line.date_to):
                    ok = line.available_amount - self.price_subtotal
                    break
            if ok < 0:
                raise UserError('Attention votre budget est insusffisant vour effectuer l\'achat')


    
    def create_budget_lines(self, general_budget_id, analytic_account_id, ids):
        """ Create analytic items upon validation of an account.move.line having an budget account. This
            method first remove any existing analytic item related to the line before creating any new one.
        """
        for obj_line in self:
            available = planned = 0
            if obj_line.account_analytic_id == analytic_account_id and obj_line.account_id in ids:
                for line in obj_line.account_analytic_id.budget_line:
                    if (obj_line.account_id.id in line.general_budget_id.account_ids.ids) and obj_line.date_planned.date() >= line.date_from and obj_line.date_planned.date() <= line.date_to:
                        available = line.available_amount
                        planned = line.planned_amount
                        break
                vals_line = {
                    'name': obj_line.name,
                    'date': obj_line.date_planned,
                    'account_id': obj_line.account_analytic_id.id or False,
                    'unit_amount': obj_line.product_qty,
                    'product_id': obj_line.product_id.id or False,
                    'amount': obj_line.price_subtotal,
                    'available_amount':(available-obj_line.price_subtotal),
                    'planned_amount':planned,
                    'general_budget_id':general_budget_id or False,
                    'general_account_id': obj_line.account_id.id or False,
                    'ref': obj_line.order_id.name,
                    'partner_id':obj_line.order_id.partner_id.id,
                }

                self.env['account.budget.line'].create(vals_line)
