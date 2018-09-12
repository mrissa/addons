# -*- coding:utf-8 -*-
#
#
#    Copyright (C) 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import ValidationError

class NmclState(models.Model):
    _name = "nmcl.state"
    _description = "State"

    name = fields.Char(string="Name of State", required=True, translate=True)
    code = fields.Char(string="Code", required=True)

    _sql_constraints = [
        ('code_uniq', 'unique(code)',
         'The Code must be unique.')
    ]

class NmclCity(models.Model):
    _name = "nmcl.city"
    _description = "City"

    name = fields.Char(string="Name of City", required=True, translate=True)
    code = fields.Char(string="Code", required=True)
    state_id = fields.Many2one('nmcl.state', string='State', required=True)

    _sql_constraints = [
        ('code_uniq', 'unique(code,state_id)',
         'The Code must be unique per state.')
    ]

class NmclTown(models.Model):
    _name = "nmcl.town"
    _description = "Town"

    name = fields.Char(string="Name of Town" , required=True, translate=True)
    code = fields.Char(string="Code", required=True)
    city_id = fields.Many2one('nmcl.city', string='City', required=True)

    _sql_constraints = [
        ('code_uniq', 'unique(code,city_id)',
         'The Code must be unique per city.')
    ]

class Nmcldren(models.Model):
    _name = "nmcl.dren"
    _description = "dren"

    name = fields.Char(string='Name Of DREN', required=True, translate=True)
    code = fields.Char(string="Code", related="state_id.code", required=True)
    state_id = fields.Many2one('nmcl.state',string='State', required=True)

class YearScholarly(models.Model):
    _name = "year.scholarly"
    _description = "Year Scholarly"
    _order = 'year_start desc'
    _inherit = ['mail.thread']

    @api.one
    @api.depends('year_start', 'year_end')
    def _get_name(self):
        if self.year_end and self.year_start:
            self.name=str(self.year_start)[2:4]+'/'+str(self.year_end)[2:4]+ ' '+str(self.chaine)

    @api.one
    @api.depends('year_start')
    def _get_year_end(self):
        if self.year_start:
            self.year_end = self.year_start+ 1
    @api.one
    @api.depends('year_start')
    def _get_next(self):
        if self.year_start:
            year_next = self.year_start + 1
            next_year = self.search([('year_start','=',year_next), ('type','=','central'), ('niveau','=','central')], limit=1)
            if next_year:
                self.next_scolarity_id = next_year.id
    @api.one
    @api.depends('year_start')
    def _get_previous(self):
        if self.year_start:
            year_next = self.year_start - 1
            next_year = self.search([('year_start', '=', year_next), ('type','=','central'), ('niveau','=','central')], limit=1)
            if next_year:
                self.previous_scolarity_id = next_year.id

    @api.one
    def _get_inscription_draft_ids(self):
        inscriptions = self.env['stud.inscription'].search([('scholarly_id', '=', self.id), ('state', '=', 'draft')])
        if inscriptions:
            self.inscription_draft_ids = inscriptions

    @api.one
    def _get_inscription_ids(self):
        inscriptions = self.env['stud.inscription'].search([('scholarly_id', 'child_of', self.id)])
        if inscriptions:
            self.inscription_ids = inscriptions

    name = fields.Char(string="Nom", translate=True, readonly=True, compute='_get_name', store=True)
    chaine = fields.Char(string="Chaine", default='')
    year_start = fields.Selection([(num, str(num)) for num in range(1900, ((datetime.now().year) + 2))], 'Année début', required=True)
    year_end = fields.Selection([(num, str(num)) for num in range(1900, ((datetime.now().year) + 3))], 'Année Fin', required=True, compute='_get_year_end', readonly=True)
    next_scolarity_id = fields.Many2one('year.scholarly', string='Année prochaine', compute='_get_next')
    previous_scolarity_id = fields.Many2one('year.scholarly', string='Année précédente', compute='_get_previous')
    state = fields.Selection(
        [('draft', 'En cours d\'ouverture'), ('open', 'ouvert'), ('pending_closed', 'En cours de fermeture'),
         ('closed', 'Fermé')],
        string='Etat', default='draft')
    inscription_draft_ids = fields.One2many('stud.inscription', compute='_get_inscription_draft_ids')
    inscription_ids = fields.One2many('stud.inscription', compute='_get_inscription_ids')
    echeance_ids = fields.One2many('year.scholarly.echeance', 'scholarly_id', string='Discipline')
    type = fields.Selection(
        [('central', 'Central'), ('fondamentale', 'Fondamentale'), ('secondaire', 'Secondaire')],
        string='Type')
    niveau = fields.Selection(
        [('central', 'Central'), ('dren', 'DREN'), ('etablissement', 'Etablissement')],
        string='Niveau')
    parent_id = fields.Many2one('year.scholarly', string='Année Scolaire')

    _sql_constraints = [
        ('code_uniq', 'unique(name, type, niveau)','The name must be unique.'),
        ('year_start_uniq', 'unique(year_start, type, niveau, name)', 'Année scolaire doit etre unique.'),
        ('year_end_uniq', 'unique(year_end, type, niveau, name)', 'The year end must be unique.'),
    ]

    @api.constrains('year_start', 'year_end')
    def _check_date(self):
        for years in self:
            if int(years.year_end) - int(years.year_start) > 1:
                raise ValidationError(_('the number of years between the two dates is greater than 1!'))
            if int(years.year_end) < int(years.year_start):
                raise ValidationError(_('the end year must not be less than the start year!'))

    @api.multi
    def act_close(self):
        self.state = 'closed'

class YearScolarityEcheance(models.Model):
    _name = "year.scholarly.echeance"
    _description = "Echéance"

    name = fields.Char(string="Echéance", required=True)
    date = fields.Date(string="Date Echéance", required=True)
    scholarly_id = fields.Many2one('year.scholarly', string='Scolarité')

class YearScolarityLine(models.Model):
    _name = "year.scholarly.line"
    _description = "Structure Pédagogique"

    @api.one
    @api.depends('scholarly_id.inscription_ids')
    def _get_inscription_ids(self):
        if self.scholarly_id.inscription_ids:
            inscription_parent = self.env['stud.inscription'].search(
                [('structure', '=', self.name), ('id', 'in', self.scholarly_id.inscription_ids.ids)])
            if inscription_parent:
                self.inscription_ids = inscription_parent

    @api.one
    @api.depends('structure_id.name')
    def _get_name(self):
        if self.structure_id:
            self.name = str(self.structure_id.name)

    @api.one
    @api.depends('scholarly_id.type')
    def _get_type(self):
        if self.scholarly_id:
            self.type = self.scholarly_id.type

    @api.one
    @api.depends('section_ids')
    def _section_count(self):
        if self.section_ids:
            count = len(self.section_ids)
            self.section_number = count

    @api.one
    @api.depends('section_ids')
    def _get_employee_ids(self):
        list = []
        if self.section_ids:
            for section in self.section_ids:
                if section.line_ids:
                    for line in section.line_ids:
                        list.append(line.employee_id.id)
            if list:
                emplyees = self.env['hr.employee'].search([('id', 'in', list)])
                self.employee_ids = emplyees

    name = fields.Char(string="Nom", compute='_get_name')
    type = fields.Selection(
        [('fondamentale', 'Fondamentale'), ('secondaire', 'Secondaire')],
        string='Type', compute='_get_type')
    scholarly_id = fields.Many2one('year.scholarly', string='Scholarly')
    structure_id = fields.Many2one('educa.structure', string='Structure Pédagogique', required=True, domain="[('type', '=', type)]")
    section_ids = fields.One2many('educa.etab.section', 'year_ligne_id', string='Section')
    section_number = fields.Integer('Section', compute='_section_count')
    employee_ids = fields.One2many('hr.employee', compute='_get_employee_ids')
    notes = fields.Char(string='Notes')
    inscription_ids = fields.One2many('stud.inscription', compute='_get_inscription_ids')

    @api.multi
    def action_structure_form_view(self):
        return {
            'name': _('Discipline'),
            'res_model': 'year.scholarly.line',
            'view_mode': 'form',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'res_id': self.id,
        }

class EducaStructure(models.Model):
    _name = "educa.structure"
    _description = "Educational Structure"
    _order = 'name'
    _inherit = ['mail.thread']

    name = fields.Char(string="Nom", required=True, translate=True)
    type = fields.Selection([('first_level', 'First Level'),('last_level', 'Last Level'),('none', 'None')], string='Type', required=True)
    type_enseig = fields.Selection([('fondamentale', 'Fondamentale'), ('secondaire', 'Secondaire')],
                             string='Type')

class EducaSection(models.Model):
    _name = "educa.etab.section"
    _description = "Section"

    name = fields.Char(string='Section')
    year_ligne_id = fields.Many2one('year.scholarly.line', string='Structure Pédagogique')
    line_ids = fields.One2many('educa.etab.section.line', 'section_id', string='Section')

    @api.multi
    def action_section_line_form_view(self):
        return {
            'name': _('Section'),
            'res_model': 'educa.etab.section',
            'view_mode': 'form',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'res_id': self.id,
        }

class EducaSectionLine(models.Model):
    _name = "educa.etab.section.line"
    _description = "Ligne section"

    section_id = fields.Many2one('educa.etab.section', string='Section')
    discipline_ids = fields.Many2many('skill.discipline', 'section_line_descipline_rel', 'skill_id', 'section_line_id', string='Discipline', required=True)
