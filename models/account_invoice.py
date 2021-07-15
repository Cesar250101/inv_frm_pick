# -*- coding: utf-8 -*-
from odoo import api, fields, models,


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('quantity')
    def onchange_product_id(self):
        for line in self:
            line.price_subtotal = abs(line.price_unit * line.quantity)

    @api.onchange('quantity')
    def _onchange_uom_id(self):
        res = super(AccountMoveLine, self)._onchange_uom_id()
        self.price_subtotal = abs(self.price_unit * self.quantity)
        return res

    @api.model
    def _get_price_total_and_subtotal_model(self, price_unit, quantity,
                                            discount, currency, product,
                                            partner, taxes, move_type):
        res = super(AccountMoveLine, self)._get_price_total_and_subtotal_model(
            price_unit, quantity, discount, currency, product, partner, taxes,
            move_type)
        subtotal = res['price_subtotal']
        res['price_subtotal'] = abs(subtotal)
        return res
