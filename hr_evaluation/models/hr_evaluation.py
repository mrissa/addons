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

AVAILABLE = [
    ('0', 'Faible'),
    ('1', 'Moyen'),
    ('2', 'Excellent')
]

class hr_employee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def _evaluation_count(self):
        for each in self:
            evaluation_ids = self.env['hr.evaluation'].search([('employee_id', '=', each.id)])
            each.evaluation_count = len(evaluation_ids)

    @api.multi
    def evaluation_view(self):
        self.ensure_one()
        domain = [
            ('employee_id', '=', self.id)]
        return {
            'name': _('Evaluation'),
            'domain': domain,
            'res_model': 'hr.evaluation',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                                   Click to Create New Evaluation
                                </p>'''),
            'limit': 80,
        }

    evaluation_ids = fields.One2many('hr.evaluation', 'employee_id', 'Evaluation')
    evaluation_count = fields.Integer(compute='_evaluation_count', string='Evaluation')

class hr_evaluation(models.Model):
    _name = 'hr.evaluation'
    _inherit = ['mail.thread']

    name = fields.Char(string='Description', size=64, required=True, translate=True)
    employee_id = fields.Many2one('hr.employee', string='Employé', required=True)
    evaluateur = fields.Many2one('hr.employee', string='Evaluateur', required=True)
    evaluateur_matricule = fields.Char(string='Matricule Evaluateur', related='evaluateur.identification_id', readonly=True, translate=True)
    employee_matricule = fields.Char(string='Matricule', related='employee_id.identification_id', readonly=True, translate=True)
    date = fields.Date('Date Inspection')
    date_prevue = fields.Date('Date Prevue')
    type = fields.Selection([('administratives', 'Administratives'), ('pedagogiques', 'Pédagogiques')],'Type Inspection', required=True)
    result = fields.Selection(AVAILABLE, 'Appréciation')
    value = fields.Float('Resultat')
    state = fields.Selection([('draft', 'Brouillon'), ('cancel', 'Annuler'), ('done', 'Valider')],string='Etat', default='draft')
    note = fields.Char(string='Notes')
    #etablissement_id = fields.Many2one('etablissement', string='Etablissement', required=True)
    #structure_id = fields.Many2one('etablissement.structure', string='Structure Pedagogique', domain="[('etablissement_id', '=', etablissement_id)]", required=True)
    line_ids = fields.One2many('line.evaluation', 'evaluation_id', string='Evaluation')


    @api.one
    def button_done(self):
        self.state = 'done'

    @api.one
    def button_cancel(self):
        self.state = 'cancel'

class LineEvaluation(models.Model):
    _name = 'line.evaluation'
    _inherit = ['mail.thread']

    evaluation_id = fields.Many2one('hr.evaluation', string='Evaluation')
    topique_id = fields.Many2one('topique.evaluation', string='Domaine de compétance', required=True)
    criterion_id = fields.Many2one('criterion.evaluation', string='Critère', required=True)
    result = fields.Selection([('0', '0'),('1', '0.25'),('2', '0.5'),('3', '0.75'),('4', '1')], 'Résultat')
    note = fields.Char(string='Notes', translate=True)

class TopiqueEvaluation(models.Model):
    _name = 'topique.evaluation'
    _inherit = ['mail.thread']

    name = fields.Char(string='Description', size=64, required=True, translate=True)
    sequence = fields.Integer(string='Sequence')
    criterion_ids = fields.One2many('criterion.evaluation', 'topique_id', string='Critères')

class CriterionEvaluation(models.Model):
    _name = 'criterion.evaluation'
    _inherit = ['mail.thread']

    topique_id = fields.Many2one('topique.evaluation', string='Topique Evaluation')
    name = fields.Char(string='Description', size=64, required=True, translate=True)
    sequence = fields.Integer(string='Séquence')

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    evaluation_ids = fields.One2many('hr.evaluation', 'employee_id', string='Evaluations',)