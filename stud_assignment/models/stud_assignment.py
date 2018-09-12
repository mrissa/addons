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
from odoo.exceptions import ValidationError
from odoo import tools, _


class StudAssignment(models.Model):
    _name = "stud.assignment"
    _description = "Assignment"
    _order = "scholarly_id asc"

    @api.one
    @api.depends('assignment_line_ids')
    def _get_record_count(self):
        if self.assignment_line_ids:
            self.is_records_line = True
        else:
            self.is_records_line = False

    @api.one
    @api.depends('scholarly_id')
    def _get_etablissement(self):
        if self.scholarly_id:
            self.etablissement_ids = self.scholarly_id.etablissement_ids

    @api.one
    @api.depends('scholarly_id', 'establishment_id')
    def _get_child(self):
        if self.scholarly_id and self.establishment_id:
            scholarly = self.env['year.scholarly'].search([('etablissement_id', '=', self.establishment_id.id), ('year_start', '=', self.scholarly_id.year_start)], limit=1)
            self.child_id = scholarly.id

    name=fields.Char(string='Reference', required=True, copy=False, readonly=True, default= lambda self: self.env['ir.sequence'].next_by_code('stud.assignement.default.seq'))
    state=fields.Selection([('draft', 'Draft'), ('validate', 'Validate')],
                             string='State', default='draft')
    scholarly_id = fields.Many2one('year.scholarly', string='Scolarity Year', domain="[('state','=','open'), ('niveau','=','central'), ('type','!=','central')]", required=True)
    child_id = fields.Many2one('year.scholarly', string='Scolarity Year', compute='_get_child')
    establishment_id = fields.Many2one('educa.establishment', string='Establishment', domain="[('id','in', etablissement_ids)]", required=True)
    structure_year_id = fields.Many2one('year.scholarly.line', string='Structure Pedagogique', domain ="[('scholarly_id','=',child_id),('etablissement_id','=',establishment_id)]", required=True)
    structure = fields.Char(string='Structure Pedagogique', related='structure_year_id.name')
    notes = fields.Text(string='Notes')
    assignment_line_ids = fields.Many2many('stud.inscription', 'stud_assignment_rel', 'inscription_id',
                                        'assignment_id', string='Registrations', domain="[('state','=','draft'),('scholarly_id','=',scholarly_id),('structure','=',structure)]", required=True)
    is_records_line = fields.Boolean(string='ligne assignement', compute='_get_record_count')
    etablissement_ids = fields.One2many('educa.establishment', compute='_get_etablissement')

    @api.multi
    def act_validate(self):
        if not self.assignment_line_ids:
            raise ValidationError("Il faut selectionner au moin une inscription!")
        else:
            for line in self.assignment_line_ids:
                line.establishment_id = self.establishment_id.id
                line.year_line_id = self.structure_year_id.id
                line.scholarly_id = self.child_id.id
                line.state = 'inscrit'
                line.student_id.scholarly_id = line.scholarly_id.id
                line.student_id.structure_year_id = line.year_line_id.id
                line.student_id.establishment_id = self.establishment_id
                line.student_id.state_inscription = line.state
                line.student_id.state = 'actif'
            self.state = 'validate'
