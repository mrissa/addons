# -*- coding: utf-8 -*-
# Copyright 2013 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo import tools, _


class Employee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def _skill_count(self):
        for each in self:
            skill_ids = self.env['hr.skill'].search([('employee_id', '=', each.id)])
            each.skill_count = len(skill_ids)

    @api.multi
    def employee_view(self):
        self.ensure_one()
        domain = [
            ('employee_id', '=', self.id)]
        return {
            'name': _('Employee'),
            'domain': domain,
            'res_model': 'hr.skill',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                                   Click to Create New Competance
                                </p>'''),
            'limit': 80,
        }

    skill_ids = fields.One2many('hr.skill', 'employee_id', 'Employee')
    skill_count = fields.Integer(compute='_skill_count', string='Employee')