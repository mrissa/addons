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

class PvRecruitment(models.Model):
    _name = 'hr.recruitment.pv'
    _description = 'PV Recruitment'
    _inherit = ['mail.thread']
    _order = "id desc"

    @api.one
    @api.depends('employee_ids', 'employee_interne_ids')
    def _get_record_count(self):
        if self.employee_ids or self.employee_interne_ids:
            self.is_records_line = True
        else:
            self.is_records_line = False

    @api.one
    @api.depends('corps_id', 'new_graduates')
    def _get_fields_copy(self):
        if self.corps_id:
            self.corps_copy_id = self.corps_id.id
        if self.new_graduates:
            self.new_graduates_copy = self.new_graduates

    @api.one
    @api.depends('recruitment_pv_type')
    def _get_rec_pv_type(self):
        if self.recruitment_pv_type:
            self.recruitment_pv_copy_type = self.recruitment_pv_type

    @api.one
    @api.depends('employee_ids', 'employee_interne_ids')
    def _get_employee(self):
        if self.employee_ids:
            self.employee_copy_ids = self.employee_ids
        if self.employee_interne_ids:
            self.employee_copy_ids = self.employee_interne_ids

    corps_id = fields.Many2one('hr.employee.corps', string='Corps', required=True)
    corps_copy_id = fields.Many2one('hr.employee.corps', string='Corps', compute='_get_fields_copy')
    new_graduates = fields.Boolean(string='Nouveaux diplômés', default=True)
    new_graduates_copy = fields.Boolean(string='Nouveaux diplômés', compute='_get_fields_copy')
    recruitment_pv_type_ns = fields.Selection([('direct', 'Recrutement direct'), ('titularisation', 'Titularisation')], string='Type PV/NS',)
    recruitment_pv_type = fields.Selection([('direct', 'Recrutement direct'), ('training_school', 'Training school'), ('titularisation', 'Titularisation')], string='Type PV/NS', required=True)
    recruitment_pv_copy_type = fields.Selection([('direct', 'Recrutement direct'), ('training_school', 'Training school'), ('titularisation', 'Titularisation')], string='Type PV/NS', compute='_get_rec_pv_type')
    training_school_id = fields.Many2one('training.school', string='Ecole de formation')
    recruitment_direct_type = fields.Many2one('recruitment.direct.type', string='Type')
    name = fields.Char(string='Num PV/NS', required=True)
    date = fields.Date('Date', required=True)
    employee_ids = fields.One2many('hr.employee', 'recruitment_pv_id', 'Employee')
    employee_copy_ids = fields.One2many('hr.employee', compute='_get_employee')
    employee_interne_ids = fields.Many2many('hr.employee', 'pv_interne_employee_rel', 'employee_id',
                              'pv_id', string='PV',)
    notes = fields.Text('Notes', translate=True)
    year_success = fields.Selection([(num, str(num)) for num in range(1940, (datetime.now().year) + 1)], 'Année de réussite')
    state = fields.Selection(
        [('draft', 'Draft'), ('validate', 'Valider')], 'State',
        readonly=True, default='draft', track_visibility='onchange')
    is_records_line = fields.Boolean(string='Employés', compute='_get_record_count')
    invisible = fields.Boolean(string='Invisible',)
    lien = fields.Many2many(comodel_name="ir.attachment",
                                relation="ir_pv_rel",
                                column1="pv_id",
                                column2="attachment_id",
                                string="Lien PV")

    @api.onchange('recruitment_pv_type')
    def _onchange_information(self):
        if self.recruitment_pv_type == 'titularisation':
            self.new_graduates = False

    @api.onchange('recruitment_pv_type_ns')
    def _onchange_information_ns(self):
        if self.recruitment_pv_type_ns:
            self.recruitment_pv_type = self.recruitment_pv_type_ns

    @api.multi
    def act_validate(self):
        if not self.employee_ids and not self.employee_interne_ids:
            raise ValidationError("Vous devez créer au moin un employé!")
        else:
            if self.training_school_id:
                if self.employee_ids:
                    for employee in self.employee_ids:
                        employee.training_school_id=self.training_school_id.id
                if self.employee_interne_ids:
                    for employee in self.employee_interne_ids:
                        employee.training_school_id=self.training_school_id.id
        self.state = 'validate'

    @api.multi
    def act_remetrre_en_brouillon(self):
        rec_exit= self.env['hr.recruitment.exit.line'].search([('pv_id', '=', self.id)])
        if rec_exit:
            raise ValidationError("Vous ne pouvez pas réouvrir ce PV, il est déjà utiliser dans un recrutement externe")
        rec_entry= self.env['hr.recruitment.entry.pv.line'].search([('pv_id', '=', self.id)])
        if rec_entry:
            raise ValidationError("Vous ne pouvez pas réouvrir ce PV, il est déjà utiliser dans un recrutement interne")
        self.state = 'draft'