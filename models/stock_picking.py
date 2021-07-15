# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, exceptions


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    invoice_ids = fields.Many2many('account.invoice', string='Invoice')
    invoice_count = fields.Integer(string="Invoice Count", compute="count_invoices")

    @api.multi
    @api.depends('invoice_ids')
    def count_invoices(self):
        for rec in self:
            rec.invoice_count = len(rec.invoice_ids)


    def action_view_invoice(self):
        if self.picking_type_code != 'incoming' :
            action = self.env.ref('account.action_invoice_tree1').read()[0]
            if len(self.invoice_ids) > 1 :
                action['domain'] = [('id','in',self.invoice_ids.ids)]
            else:
                action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
                action['res_id'] = self.invoice_ids and self.invoice_ids[0].id or False 
            action['context']=self.id
            return action 
        else:
            action = self.env.ref('account.action_invoice_tree1').read()[0]
            if len(self.invoice_ids) > 1 :
                action['domain'] = [('id','in',self.invoice_ids.ids)]
            else:
                action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
                action['res_id'] = self.invoice_ids and self.invoice_ids[0].id or False 
            action['context']=self.id
            return action 


    def create_invoice(self):
        account_obj = self.env['account.account']
        inv_data = []
        journal = self.env['account.invoice'].with_context(default_type='out_invoice')._default_journal()
        if not journal: raise exceptions.UserError(_('Please define an accounting sales journal for the company %s (%s).') % (self.company_id.name, self.company_id.id))
        if self.picking_type_code != 'incoming' :
            inv_data = {'type': 'out_invoice',
                        'account_id': self.move_line_ids and self.move_line_ids[0].product_id.categ_id.property_account_income_categ_id.id or account_obj.search([('name', '=', 'Incomes')], limit=1).id
            }

        else:
            journal = self.env['account.invoice'].with_context(default_type='in_invoice')._default_journal()
            inv_data = {'type': 'in_invoice',
                        'account_id': self.move_line_ids and self.move_line_ids[0].product_id.categ_id.property_account_expense_categ_id.id or account_obj.search([('name', '=', 'Expenses')], limit=1).id
            }

        if self.sale_id:

            inv_data = { 'invoice_payment_term_id': self.sale_id.payment_term_id and self.sale_id.payment_term_id.id or False,
            'invoice_user_id': self.sale_id.user_id and self.sale_id.user_id.id or False,
            'team_id': self.sale_id.team_id and self.sale_id.team_id.id or False,
            'invoice_origin': self.sale_id.name or '',
            'narration': self.sale_id.note or '',
            'ref': self.sale_id.client_order_ref or '',
            'partner_shipping_id': self.sale_id.partner_shipping_id.id or False,
            }

        if self.purchase_id:

            inv_data = { 'invoice_payment_term_id': self.purchase_id.payment_term_id and self.purchase_id.payment_term_id.id or False,
            'invoice_user_id': self.purchase_id.user_id and self.purchase_id.user_id.id or False,
            'team_id': self.purchase_id.team_id and self.purchase_id.team_id.id or False,
            'invoice_origin': self.purchase_id.name or '',
            'narration': self.purchase_id.note or '',
            'ref': self.purchase_id.client_order_ref or '',
            'partner_shipping_id': self.purchase_id.partner_shipping_id.id or False,
            }


        data = {
            
            'partner_id': self.partner_id.id or False,
            'date_invoice': str(self.scheduled_date),
            'currency_id': self.company_id.currency_id.id or False,
            'journal_id': journal.id,
            'company_id': self.company_id.id or False,
            
            
            'invoice_line_ids': [(0, 0, {
                'product_id': line.product_id.id or False,
                'name':  line.product_id.name or '',
                'quantity': line.product_uom_qty or '',
                'price_unit': 1.0, 
                'account_id': line.product_id.categ_id.property_account_income_categ_id.id or line.product_id.categ_id.property_account_expense_categ_id.id or account_obj.search([('name', '=', 'Expenses')], limit=1).id or account_obj.search([('name', '=', 'Incomes')], limit=1).id,
                'journal_id': journal.id,
            }) for line in self.move_line_ids],
        }
        data.update(inv_data)
        data.update(self.env['account.invoice'].default_get(['reference_type']))
        invoice = self.env['account.invoice'].create(data)
        self.invoice_ids = invoice

        if self.sale_id:
            self.sale_id.invoice_ids = invoice
            if self.sale_id.order_line : 
                for line in self.sale_id.order_line: line.write({
                        'invoice_lines':  [(4, inl.id)
                         for inl in invoice.invoice_line_ids.filtered(
                             lambda x: x.product_id.id == line.product_id.id)]
                    })

        if self.purchase_id:
            self.purchase_id.invoice_ids = invoice
            if self.purchase_id.order_line : 
                for line in self.purchase_id.order_line: line.write({
                        'invoice_lines':  [(4, inl.id)
                         for inl in invoice.invoice_line_ids.filtered(
                             lambda x: x.product_id.id == line.product_id.id)]
                    })
