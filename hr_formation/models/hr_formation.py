# -*- encoding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from odoo import api, fields, models
from odoo import tools, _

class hr_employee(models.Model):
    _inherit = 'hr.employee'

    @api.one
    def _formation_count(self):
        self._cr.execute("select count(employee_id) FROM event_employee_rel WHERE event_id = %s", (self.id, )),
        res = self._cr.fetchone()[0]
        if res:
            self.formation_count = res
        else:
            self.formation_count = 0

    @api.multi
    def formation_view(self):
        self.ensure_one()
        self._cr.execute("select employee_id FROM event_employee_rel WHERE event_id = %s", (self.id,)),
        res = self._cr.fetchone()
        domain = [
            ('id', 'in', res)]
        return {
            'name': _('Formations'),
            'domain': domain,
            'res_model': 'event.event',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                                       Click to Create New Evaluation
                                    </p>'''),
            'limit': 80,
        }

    formation_count = fields.Integer(compute='_formation_count', string='Formation')
    formation_ids = fields.Many2many('event.event', 'event_employee_rel', 'event_id', 'employee_id',
                                        string='Liste des formations')

class HrFormation(models.Model):
    _inherit = 'event.event'

    jour_count = fields.Float(string='Nombre de jours')
    heure_count = fields.Float(string='Nombre Heures')
    commentaires = fields.Char(string='Commentaires')
    employee_ids = fields.Many2many('hr.employee', 'event_employee_rel', 'employee_id', 'event_id',
                                        string='Liste des employés')
