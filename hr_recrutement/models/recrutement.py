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
import logging
_logger = logging.getLogger(__name__)

class RecruitmentDirectType(models.Model):
    _name = 'recruitment.direct.type'

    name = fields.Char(string='Recruitment direct Type', required=True, translate=True)

class ExitRecruitment(models.Model):
    _name = 'hr.recruitment.exit'
    _description = 'Exit Recruitment'
    _order = "id desc"

    @api.one
    @api.depends('line_ids')
    def _get_employee(self):
        list = []
        if self.line_ids:
            for line in self.line_ids:
                list.append(line.pv_id.id)
            employee_ids = self.env['hr.employee'].search([('recruitment_pv_id', 'in', list)])
            if employee_ids:
                self.employee_to_trait_ids = employee_ids

    @api.one
    @api.depends('line_ids')
    def _get_record_count(self):
        if self.line_ids:
            self.is_records_line = True
        else:
            self.is_records_line = False

    @api.one
    @api.depends('corps_id')
    def _get_corps(self):
        if self.corps_id:
            self.corps_copy_id = self.corps_id.id

    @api.one
    @api.depends('recruitment_pv_type')
    def _get_rec_pv_type(self):
        if self.recruitment_pv_type:
            self.recruitment_pv_copy_type = self.recruitment_pv_type

    @api.one
    @api.depends('line_ids')
    def _get_pv(self):
        if self.line_ids:
            list = []
            for line in self.line_ids:
                list.append(line.pv_id.id)
            pv = self.env['hr.recruitment.pv'].search([('id', 'in', list)]).ids
            if pv:
                self.pv_check_ids = pv

    @api.one
    def _get_pv_treat(self):
        rec = self.env['hr.recruitment.exit.line'].search([('recruitment_exit_id', '!=', self.id)])
        if rec:
            list = []
            for line in rec:
                list.append(line.pv_id.id)
            pv_treat_ids = self.env['hr.recruitment.pv'].search([('id', 'in', list)]).ids
            if pv_treat_ids:
                self.pv_treat_ids = pv_treat_ids

    @api.one
    @api.depends('recruitment_pv_type', 'date')
    def _get_type_arrete(self):
        if self.recruitment_pv_type:
            if self.recruitment_pv_type == 'direct':
                self.type_arrete = 'arrete_nomination'
                self.date_nomination = self.date
            if self.recruitment_pv_type == 'training_school':
                self.type_arrete = 'arrete_nomination_titularisation'
                if self.date:
                    self.date_titularisation = self.date
                    self.date_nomination = self.date

    name = fields.Char(string='Référence', required=True, copy=False, readonly=True, default=lambda self: self.env['ir.sequence'].next_by_code('rec.exit.default.seq'))
    name_arrete = fields.Char(string='Arrêté')
    corps_id = fields.Many2one('hr.employee.corps', string='Corps', required=True)
    corps_copy_id = fields.Many2one('hr.employee.corps', string='Corps', compute='_get_corps')
    echelle_id = fields.Many2one('hr.echelle', 'Echelle', related='corps_id.echelle_id', readonly=True)
    date = fields.Date('Date', required=True)
    date_titularisation = fields.Date('Date Titularisation', compute='_get_type_arrete')
    date_nomination = fields.Date('Date Nomination', compute='_get_type_arrete')
    new_graduates = fields.Boolean(string='Nouveaux diplômés', default=True)
    employee_to_trait_ids = fields.One2many('hr.employee', compute='_get_employee')
    employee_ids = fields.Many2many('hr.employee', 'recrutement_employee_rel', 'employee_id', 'recruitment_exit_id', 'Employés', domain="[('id','in',employee_to_trait_ids)]")
    line_ids = fields.One2many('hr.recruitment.exit.line', 'recruitment_exit_id', string='PV/NS')
    pv_treat_ids = fields.One2many('hr.recruitment.pv', string='PV/NS', compute='_get_pv_treat')
    pv_check_ids = fields.One2many('hr.recruitment.pv', compute='_get_pv')
    state = fields.Selection([('draft', 'Brouillon'), ('preparation_budget', 'Préparation budget'), ('preparation_arrete', 'Préparation Arrêté'), ('validate', 'Valider')],
                                 string='State', default='draft')
    corps_line_id = fields.Many2one('hr.employee.corps.line', string='Rémuniration', domain="[('corps_id','=',corps_id)]")
    notes = fields.Text('Notes', translate=True)
    subject = fields.Char(string='Subject')
    section = fields.Char(string='Section')
    is_records_line = fields.Boolean(string='PV existe', default=False, compute='_get_record_count')
    type_arrete = fields.Selection(
        [('arrete_nomination', 'Arrêté de Nomination'), ('arrete_titularisation', 'Arrêté de Titularisation'),
         ('arrete_nomination_titularisation', 'Arrêté de Nomination et Titularisation')], string='Type arrêté', compute='_get_type_arrete')
    recruitment_pv_type = fields.Selection([('direct', 'Direct'), ('training_school', 'Training school')], string='Type Recrutement', required=True)
    recruitment_pv_copy_type = fields.Selection([('direct', 'Direct'), ('training_school', 'Training school')], string='Type Recrutement', compute='_get_rec_pv_type')
    affectation_ids = fields.Many2many('hr.assignment', 'rec_exit_assignment_rel', 'assignment_id', 'rec_exit_id', string='Affections')

    @api.onchange('line_ids')
    def _onchange_employee(self):
        list = []
        if self.line_ids:
            for line in self.line_ids:
                list.append(line.pv_id.id)
            employee_ids = self.env['hr.employee'].search([('recruitment_pv_id', 'in', list)])
            if employee_ids:
                self.employee_ids = employee_ids

    @api.multi
    def act_preparation_budget(self):
        if not self.employee_ids:
            raise ValidationError("Il faut séléctionner au moin un employé!")
        else:
            self.state = 'preparation_budget'

    @api.multi
    def act_preparation_arrete(self):
        self.state = 'preparation_arrete'

    @api.multi
    def act_remetrre_en_brouillon(self):
        self.state = 'draft'

    @api.multi
    def act_validate(self):
        position=self.env['hr.assignment.type'].search([('code','=','01')])
        motif = self.env['hr.assignment.type.motif'].search([('code', '=', '0102')])
        for employee in self.employee_ids:
            employee.recruitment_type ='employee'
            employee.corps_id = self.corps_id.id
            employee.corps_line_id = self.corps_line_id.id
            employee.date_nomination = self.date_nomination
            employee.date_titularisation = self.date_titularisation
            if position:
                employee.position_id = position.id
            if motif:
                employee.motif_id = motif.id
        self.state = 'validate'

class HrRecExitLine(models.Model):
    _name = 'hr.recruitment.exit.line'

    recruitment_exit_id = fields.Many2one('hr.recruitment.exit', string='Recrutement Externe')
    pv_id = fields.Many2one('hr.recruitment.pv', string='PV/NS')
    date = fields.Date('Date', related='pv_id.date')
    corps_id = fields.Many2one('hr.employee.corps', string='Corps', related='pv_id.corps_id')

class EntryRecruitment(models.Model):
    _name = 'hr.recruitment.entry'
    _description = 'Entry Recruitment'
    _order = "id desc"

    @api.one
    @api.depends('corps_id')
    def _get_corps(self):
        if self.corps_id:
            self.corps_copy_id = self.corps_id.id

    @api.one
    @api.depends('recruitment_pv_type')
    def _get_rec_pv_type(self):
        if self.recruitment_pv_type:
            self.recruitment_pv_copy_type = self.recruitment_pv_type

    @api.one
    @api.depends('line_ids')
    def _get_record_count(self):
        if self.line_ids:
            self.is_records_line = True
        else:
            self.is_records_line = False

    @api.one
    @api.depends('line_ids')
    def _get_pv(self):
        if self.line_ids:
            list = []
            for line in self.line_ids:
                list.append(line.pv_id.id)
            pv = self.env['hr.recruitment.entry.pv.line'].search([('id', 'in', list)]).ids
            if pv:
                self.pv_check_ids = pv

    @api.one
    def _get_pv_treat(self):
        rec = self.env['hr.recruitment.entry.pv.line'].search([('recruitment_entry_id', '!=', self.id)])
        if rec:
            list = []
            for line in rec:
                list.append(line.pv_id.id)
            pv_treat_ids = self.env['hr.recruitment.pv'].search([('id', 'in', list)]).ids
            if pv_treat_ids:
                self.pv_treat_ids = pv_treat_ids

    @api.one
    @api.depends('line_ids')
    def _get_employee(self):
        self.env['hr.recruitment.entry.line'].search([('recruitment_entry_id', '=', self.id)]).unlink()
        list = []
        if self.line_ids:
            for line in self.line_ids:
                for employee in line.pv_id.employee_interne_ids:
                    if employee.id not in list:
                        list.append(employee.id)
            employee_ids = self.env['hr.employee'].search([('id', 'in', list)])
            if employee_ids:
                for employee in employee_ids:
                    self.env['hr.recruitment.entry.line'].create({
                        'employee_id': employee.id,
                        'recruitment_entry_id': self.id
                    })
            self.recruitment_entry_line_ids = self.env['hr.recruitment.entry.line'].search([('recruitment_entry_id', '=', self.id)])
        else:
            self.recruitment_entry_line_ids = False

    @api.one
    @api.depends('recruitment_pv_type', 'date')
    def _get_type_arrete(self):
        if self.recruitment_pv_type:
            if self.recruitment_pv_type == 'titularisation':
                self.type_arrete = 'arrete_titularisation'
                if self.date:
                    self.date_titularisation = self.date
            if self.recruitment_pv_type == 'direct':
                self.type_arrete = 'arrete_nomination'
                if self.date:
                    self.date_nomination = self.date
            if self.recruitment_pv_type == 'training_school':
                self.type_arrete = 'arrete_nomination_titularisation'
                if self.date:
                    self.date_nomination = self.date
                    self.date_titularisation = self.date

    name = fields.Char(string='Référence', required=True, copy=False, readonly=True, default=lambda self: self.env['ir.sequence'].next_by_code('rec.entry.default.seq'))
    name_arrete = fields.Char(string='Arrêté')
    corps_id = fields.Many2one('hr.employee.corps', string='Corps', required=True)
    corps_copy_id = fields.Many2one('hr.employee.corps', string='Corps', compute='_get_corps')
    echelle_id = fields.Many2one('hr.echelle', 'Echelle', related='corps_id.echelle_id', readonly=True)
    date = fields.Date('Date', required=True)
    date_titularisation = fields.Date('Date Titularisation', compute='_get_type_arrete')
    date_nomination = fields.Date('Date Nomination', compute='_get_type_arrete')
    new_graduates = fields.Boolean(string='Nouveaux diplômés', default=False)
    line_ids = fields.One2many('hr.recruitment.entry.pv.line', 'recruitment_entry_id', string='PV/NS')
    pv_treat_ids = fields.One2many('hr.recruitment.pv', string='PV/NS', compute='_get_pv_treat')
    pv_check_ids = fields.One2many('hr.recruitment.pv', compute='_get_pv')
    state = fields.Selection(
        [('draft', 'Brouillon'), ('preparation_budget', 'Préparation budget'), ('preparation_arrete', 'Préparation Arrêté'),
         ('validate', 'Valider')],
        string='State', default='draft')
    type_arrete = fields.Selection(
        [('arrete_nomination', 'Arrêté de Nomination'), ('arrete_titularisation', 'Arrêté de Titularisation'),
         ('arrete_nomination_titularisation', 'Arrêté de Nomination et Titularisation')], string='Type arrêté',
        compute='_get_type_arrete')
    corps_line_id = fields.Many2one('hr.employee.corps.line', string='Rémuniration', )
    notes = fields.Text('Notes', translate=True)
    subject = fields.Char(string='Subject')
    section = fields.Char(string='Section')
    is_records_line = fields.Boolean(string='PV existe', default=False, compute='_get_record_count')
    recruitment_entry_line_ids = fields.One2many('hr.recruitment.entry.line', 'recruitment_entry_id', string='Entry Recruitment Line', compute='_get_employee')
    recruitment_pv_type = fields.Selection([('direct', 'Direct'), ('training_school', 'Training school'), ('titularisation', 'Titularisation')], string='Type PV/NS', required=True)
    recruitment_pv_copy_type = fields.Selection([('direct', 'Direct'), ('training_school', 'Training school'), ('titularisation', 'Titularisation')], string='Type Recrutement', compute='_get_rec_pv_type')
    affectation_ids = fields.Many2many('hr.assignment', 'rec_entry_assignment_rel', 'assignment_id', 'rec_entry_id', string='Affectation',)

    @api.multi
    def act_preparation_budget(self):
        if not self.line_ids:
            raise ValidationError("Il faut séléctionner au moin un PV!")
        else:
            self.state = 'preparation_budget'

    @api.multi
    def act_preparation_arrete(self):
        self.state = 'preparation_arrete'

    @api.multi
    def act_remetrre_en_brouillon(self):
        self.state = 'draft'

    @api.multi
    def act_validate(self):
        position = self.env['hr.assignment.type'].search([('code', '=', '01')])
        motif = self.env['hr.assignment.type.motif'].search([('code', '=', '0102')])
        for employee in self.recruitment_entry_line_ids:
            employee.employee_id.recruitment_type = 'employee'
            if self.recruitment_pv_type == 'titularisation':
                employee.employee_id.date_titularisation = self.date_titularisation
            if position:
                employee.employee_id.position_id = position.id
            if motif:
                employee.employee_id.motif_id = motif.id
        self.state = 'validate'

class HrRecEntryPvLine(models.Model):
    _name = 'hr.recruitment.entry.pv.line'

    recruitment_entry_id = fields.Many2one('hr.recruitment.entry', string='Recrutement Interne')
    pv_id = fields.Many2one('hr.recruitment.pv', string='PV/NS')
    date = fields.Date('Date', related='pv_id.date')
    corps_id = fields.Many2one('hr.employee.corps', string='Corps', related='pv_id.corps_id')

class EntryRecruitmentLine(models.Model):
    _name = 'hr.recruitment.entry.line'
    _description = 'Entry Recruitment Line'

    @api.one
    @api.depends('employee_id')
    def _get_ancien_corps(self):
        if self.employee_id:
            if self.employee_id.recruitment_entry_ids:
                _logger.info("------data_list------%s", self.id)
                rec_interne = self.env['hr.recruitment.entry.line'].search([('employee_id', '=', self.employee_id.id)],order='date asc', limit=1)
                if rec_interne:
                    self.corps_line_id=rec_interne.new_corps_line_id.id
                    self.corps_id = rec_interne.new_corps_id.id
    @api.one
    @api.depends('corps_line_id')
    def _get_new_corps(self):
        if self.corps_line_id:
            corps = self.env['hr.employee.corps.line'].search([('corps_id', '=', self.recruitment_entry_id.corps_id.id), (
            'indice', '>=', int(self.corps_line_id.indice_id.name))], order='indice asc', limit=1)
            if corps:
                self.new_corps_line_id = corps.id

    recruitment_entry_id = fields.Many2one('hr.recruitment.entry', string='Recrutement interne')
    employee_id = fields.Many2one('hr.employee', 'Employee')
    nni = fields.Char(string='NNI', related='employee_id.nni')
    identification_id = fields.Char(string='Matricule', related='employee_id.identification_id')
    corps_id = fields.Many2one('hr.employee.corps', string='Corps', compute='_get_ancien_corps')
    corps_line_id = fields.Many2one('hr.employee.corps.line', string='Rémuniration',
                                    related='employee_id.corps_line_id')
    echelle_id = fields.Many2one('hr.echelle', 'Echelle', related='corps_id.echelle_id')
    new_corps_id = fields.Many2one('hr.employee.corps', string='Corps', related='recruitment_entry_id.corps_id')
    new_echelle = fields.Many2one('hr.echelle', 'Nouveau Echelle', related='corps_id.echelle_id')
    new_corps_line_id = fields.Many2one('hr.employee.corps.line', string='Nouveau rémuniration', compute='_get_new_corps')
    date = fields.Date('Date', related='recruitment_entry_id.date')
    state = fields.Selection(
        [('draft', 'Brouillon'), ('preparation_budget', 'Préparation budget'), ('preparation_arrete', 'Préparation Arrêté'),
         ('validate', 'Valider')],
        string='State', related='recruitment_entry_id.state')
    date_titularisation = fields.Date('Date Titularisation', related='recruitment_entry_id.date_titularisation')
    date_nomination = fields.Date('Date Nomination', related='recruitment_entry_id.date_nomination')

class RecruitmentOnDemande(models.Model):
    _name = 'hr.recruitment.on.demand'
    _description = 'Recruitment On Demande'

    name = fields.Char(string='Référence PV/NS', required=True)
    state = fields.Selection([('draft', 'Brouillon'), ('pending_approved', 'Pending approval'), ('approved', 'Approuver')],
                             string='State', default='draft')
    recruitment_type = fields.Selection([('pnp', 'PNP'), ('contractual', 'Contractual'), ('detached', 'Détaché')],
                                              string='Recruitment Type', required=True)
    corps_id = fields.Many2one('hr.employee.corps', string='Corps', required=True)
    date_start = fields.Date('Strat Date', required=True)
    date_end = fields.Date('End Date', required=True)
    notes = fields.Text('Notes', translate=True)
    employee_ids = fields.Many2many('hr.employee', 'employee_recruitment_demande_rel', 'employee_id', 'recruitment_demande_id',
                                   string='Employee', domain="[('recruitment_type','=','contractual')]")
    employee_new_ids = fields.One2many('hr.employee', 'recruitment_demande_id', 'Employee')

    _sql_constraints = [
        ('date_check', "CHECK (date_start <= date_end)", "The start date must be anterior to the end date."),
    ]

    @api.multi
    def act_pending_approved(self):
        self.state = 'pending_approved'

    @api.multi
    def act_approved(self):
        if self.employee_new_ids:
            for employee in self.employee_new_ids:
                if self.recruitment_type == 'pnp':
                    employee.recruitment_type = 'pnp'
                if self.recruitment_type == 'detached':
                    employee.recruitment_type = 'detached'
        if self.employee_ids:
            for employee in self.employee_ids:
                contract_obj = self.env['hr.contract']
                if self.recruitment_type == 'contractual':
                    employee.recruitment_type = 'contractual'
                    contract_obj.create({
                        'name':self.name,
                        'wage':0.0,
                        'employee_id': employee.id,
                        'date_start': self.date_start,
                        'date_end': self.date_end,
                    })
        self.state = 'approved'