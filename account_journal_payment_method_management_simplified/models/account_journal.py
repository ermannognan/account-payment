# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import api, fields, _
from odoo.osv import osv
from odoo.exceptions import UserError

METHOD_TYPES = [
    ('bank', 'Bank'),
    ('cash', 'Cash'),
]
USER_ERROR = _('Cannot complete operation.')


class AccountJournal(osv.Model):
    _inherit = 'account.journal'

    payment_method_simplified_type = fields.Selection(
        string="Type", selection=METHOD_TYPES, store=False,
        compute='_get_payment_method_simplified_type',
        inverse='_set_payment_method_simplified_type')

    @api.multi
    @api.depends('type')
    def _get_payment_method_simplified_type(self):
        allowed_types = [r[0] for r in METHOD_TYPES]
        for journal in self:
            journal.payment_method_simplified_type = journal.type \
                if journal.type in allowed_types else False

    def _set_payment_method_simplified_type(self):
        for journal in self:
            journal.type = journal.payment_method_simplified_type

    @api.model
    def create(self, vals):
        context = self._context or {}
        if not context.get('account_journal_payment_method_simplified') or\
                context.get('call_super_create'):
            return super(AccountJournal, self).create(vals)

        if not vals.get('payment_method_simplified_type'):
            raise UserError(_('The type is required.'))
        j_type = vals['payment_method_simplified_type']
        last_methods = self.search([
            ('type', '=', j_type),
            ('company_id', '=', self.env.user.company_id.id),
        ], order='id desc')
        if not last_methods:
            raise UserError(USER_ERROR)
        code = 'BNK' if j_type == 'bank' else 'CSH'
        code += '%d' % (len(last_methods) + 1)
        free_account_code_found = False
        last_method = last_methods[0]
        if not last_method.default_debit_account_id or \
                not last_method.default_credit_account_id or \
                last_method.default_debit_account_id != \
                last_method.default_credit_account_id:
            raise UserError(USER_ERROR)
        account_code = last_method.default_debit_account_id.code
        account_len = len(account_code)
        account_new_pattern = '%0' + str(account_len) + 'd'
        try:
            account_num = int(account_code)
        except:
            raise UserError(
                _('The account code "%s" cannot be casted to integer.')
                % account_code)
        account_obj = self.env['account.account']
        new_account = False
        while not free_account_code_found:
            account_num += 1
            account_new_code = account_new_pattern % account_num
            account_existing = account_obj.search([
                ('code', '=', account_new_code),
                ('company_id', '=', self.env.user.company_id.id),
            ])
            if not account_existing:
                free_account_code_found = True
                new_account = last_method.default_debit_account_id.sudo().copy({
                    'code': account_new_code,
                    'name': vals['name'],
                })
        vals.update({
            'default_debit_account_id': new_account.id,
            'default_credit_account_id': new_account.id,
            'code': code,
            'sequence_id': False,
        })
        new_payment_method = last_method.with_context(
            call_super_create=True).copy(vals)
        new_payment_method.name = vals['name']
        new_payment_method.sequence_id.sudo().write({
            'name': vals['name'],
            'prefix': code + '/%(range_year)s/',
        })
        return new_payment_method
