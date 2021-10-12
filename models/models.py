# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

def find_matching_lind_id(action, vals):
    matching_line = [ x for x in vals.get('line_ids', [(False, False, {})]) if x[0] in [0, 1] and x[2].get('name') == action[2].get('name') ]
    # raise UserError( str(matching_line) )
    if len(matching_line) > 1:
        raise UserError(_("The labels for the invoice/bill lines must be unique"))
    elif len(matching_line) == 1:
        return matching_line[0]
    else:
        return False

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    category_id = fields.Many2one('product.category', string='Category')

    @api.onchange('category_id')
    def category_id_change(self):
        self.product_id = False


class AccountMove(models.Model):
    _inherit = "account.move"

    # Because account.move have two function that change the values variable before passing them to create() & write()
    # So we need to edit the edit the two following tables instead

    @api.model
    def _move_autocomplete_invoice_lines_create(self, vals_list):
        for move in vals_list:
            for action in move['invoice_line_ids']:
                if action[0] in [0, 1]:
                    # finding the line in line_ids that matched the line in invoice_line_ids
                    matching_line = find_matching_lind_id(action, move)
                    if matching_line:
                        matching_line[2]['category_id'] = action[2]['category_id']
                    else:
                        pass

        res = super(AccountMove, self)._move_autocomplete_invoice_lines_create(vals_list)
        return res

    def _move_autocomplete_invoice_lines_write(self, vals):
        if vals.get("invoice_line_ids"):
            for action in vals['invoice_line_ids']:
                if action[0] in [0, 1] and action[2].get("category_id"):
                    # finding the line in line_ids that matched the line in invoice_line_ids
                    matching_line = find_matching_lind_id(action, vals)
                    if matching_line:
                        matching_line[2]['category_id'] = action[2]['category_id']
                    else:
                        pass

        res = super(AccountMove, self)._move_autocomplete_invoice_lines_write(vals)
        return res