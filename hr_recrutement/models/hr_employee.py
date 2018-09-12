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

from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class EmployeeCorps(models.Model):
    _name = 'hr.employee.corps'
    _order = 'name'

    name = fields.Char(string='Corps', required=True, translate=True)
    echelle_id = fields.Many2one('hr.echelle', string='Echelle', required=True)
    line_ids = fields.One2many('hr.employee.corps.line', 'corps_id', string='Ligne corps')

class EmployeeCorpsLine(models.Model):
    _name = 'hr.employee.corps.line'

    @api.one
    @api.depends('indice_id')
    def _get_indice(self):
        if self.indice_id:
            self.indice = int(self.indice_id.name)

    @api.one
    def _get_name(self):
        if self.indice_id:
            self.name = str(self.grade_id.name)+'/'+str(self.echelon_id.name)+'/'+str(self.indice_id.name)

    name = fields.Char('Rémunération', compute='_get_name')
    corps_id = fields.Many2one('hr.employee.corps', string='Corps')
    echelle_id = fields.Many2one('hr.echelle', string='Echelon', related='corps_id.echelle_id')
    echelon_id = fields.Many2one('hr.echelon', string='Echelon', required=True)
    grade_id = fields.Many2one('hr.grade', string='Grade', required=True)
    indice_id = fields.Many2one('hr.indice', string='Indice', required=True)
    indice = fields.Integer('Indice', compute='_get_indice', store=True)

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    date_titularisation = fields.Date('Date Titularisation')
    date_nomination = fields.Date('Date Nomination',)
    specialty_id1 = fields.Many2one('hr.employee.specialty', string='Specialté 1')
    specialty_id2 = fields.Many2one('hr.employee.specialty', string='Specialté 2')
    recruitment_pv_id = fields.Many2one('hr.recruitment.pv', string='PV Recruitment')
    ref_exit_recrutement = fields.Char('Reference PV/NS', related='recruitment_exit_id.name_arrete', store=True)
    corps_id = fields.Many2one('hr.employee.corps', string='Corps', store=True)
    echelle = fields.Many2one('hr.echelle', string='Echelle', related='corps_id.echelle_id')
    corps_line_id = fields.Many2one('hr.employee.corps.line', string='Rémuniration', store=True)
    training_school_id = fields.Many2one('training.school', string='Ecole de formation')
    note_graduation = fields.Float(string='Moyenne réussite')
    assignment_choice1 = fields.Many2one('nmcl.state',string='Choix 1', domain="[('id','not in', (assignment_choice2, assignment_choice3))]")
    assignment_choice2 = fields.Many2one('nmcl.state',string='Choix 2', domain="[('id','not in', (assignment_choice1, assignment_choice3))]")
    assignment_choice3 = fields.Many2one('nmcl.state',string='Choix 3', domain="[('id','not in', (assignment_choice1, assignment_choice2))]")
    assignment_choice4 = fields.Many2one('nmcl.state', string='Choix 4',)
    assignment_choice5 = fields.Many2one('nmcl.state', string='Choix 5',)
    discipline_ids = fields.Many2many('skill.discipline', 'employee_discipline_rel', 'discipline_id', 'employee_id', string='Discipline Employee')
    number_training_school = fields.Char(String='Number training school')
    recruitment_exit_id = fields.Many2one('hr.recruitment.exit', string='Exit Recruitment')
    recruitment_entry_ids = fields.One2many('hr.recruitment.entry.line', 'employee_id', string='Entry Recruitment')
    recruitment_demande_id = fields.Many2one('hr.recruitment.on.demand', string='Recruitment on demande')
    recruitment_demande_ids = fields.Many2many('hr.recruitment.on.demand', 'employee_recruitment_demande_rel', 'recruitment_demande_id',
                                    'employee_id',
                                    string='Recruitment on demande')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], default="male")

    @api.multi
    def action_detail_employee_form_view(self):
        employee_detail = self.env.ref('hr_recrutement.view_employee_grh_detail_form', False)
        return {
            'name': _('Détail employé'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.employee',
            'res_id': self.id,
            'views': [(employee_detail.id, 'form')],
            'view_id': employee_detail.id,
        }

class EmployeeSpecialty(models.Model):
    _name = 'hr.employee.specialty'

    name = fields.Char(string='Specialty', required=True, translate=True)

class TrainingSchool(models.Model):
    _name = 'training.school'

    name = fields.Char(string='Training School', required=True, translate=True)