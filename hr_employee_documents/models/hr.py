# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models
from odoo import tools, _

_logger = logging.getLogger(__name__)


class Employee(models.Model):
    _name = "hr.employee"
    _description = "Employee"
    _inherit = "hr.employee"

    @api.multi
    def attachment_tree_view(self):
        self.ensure_one()
        return {
            'name': _('Attachments'),
            'domain': [('res_model', '=', self._name), ('res_id', '=', self.id)],
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'view_mode': 'kanban,tree,form',
            'view_type': 'form',
            'context': "{'default_res_model': '%s','default_res_id': %d, 'default_product_downloadable': True}" % (self._name, self.id),
            'help': """
                <p class="oe_view_nocontent_create">Click on create to add attachments for this digital product.</p>
                <p>The attached files are the ones that will be purchased and sent to the customer.</p>
                """,
        }


    @api.multi
    def _get_attached_docs(self):
        IrAttachment = self.env['ir.attachment']
        for employee in self:
            employee.doc_count = IrAttachment.search_count([('res_model', '=', 'hr.employee'), ('res_id', 'in', employee.ids)])


    doc_count = fields.Integer(compute='_get_attached_docs', string='# Number of documents attached')

