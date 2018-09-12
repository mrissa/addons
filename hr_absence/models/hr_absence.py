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
from datetime import datetime
from odoo.exceptions import ValidationError
from odoo import tools, _

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    absence_ids = fields.One2many('hr.absence', 'employee_id', string='Abscences',)
    suspensions_ids = fields.One2many('hr.suspension', 'employee_id', string='Suspensions')

class HrAbsence(models.Model):
    _name = "hr.absence"
    _description = "Absence"
    _inherit = ['mail.thread']

    @api.one
    @api.depends('absence_type_id.nbr_limit_day')
    def _get_solde(self):
        if self.absence_type_id.nbr_limit_day:
            solde = self.absence_type_id.nbr_limit_day
            val = 0.0
            absences = self.search(
                [('employee_id', '=', self.employee_id.id), ('absence_type_id', '=', self.absence_type_id.id), ('state', '=', 'validate')])
            if absences:
                for absence in absences:
                    val = val + absence.nbr_day
            solde = solde - val
            self.solde = solde

    @api.one
    @api.depends('date_start','date_end')
    def _get_number_of_days(self):
        if self.date_end and self.date_start:
            fmt = '%Y-%m-%d'
            date_start = self.date_start
            date_end = self.date_end
            d1 = datetime.strptime(date_start, fmt)
            d2 = datetime.strptime(date_end, fmt)
            daysDiff = str((d2 - d1).days)
            self.nbr_day = float(daysDiff)

    name = fields.Char(string="Name", copy=False, readonly=True, default= lambda self: self.env['ir.sequence'].next_by_code('absence.default.seq'))
    company_id = fields.Many2one('res.company', string='Company', related='employee_id.company_id')
    employee_id = fields.Many2one('hr.employee', "Employee", required=True, )
    absence_categ_id = fields.Many2one('hr.absence.category', string='Category', required=True)
    absence_type_id = fields.Many2one('hr.absence.type', string='Type', required=True, domain="[('absence_categ_id','=',absence_categ_id)]")
    date_start =  fields.Date('Start Date',)
    date_end = fields.Date(string='Date End', )
    nbr_day = fields.Float('Number of day', required=True, compute='_get_number_of_days')
    solde = fields.Float('Solde', compute='_get_solde', store=True)
    notes = fields.Char(string="Description", translate=True)
    state = fields.Selection([('draft', 'Draft'), ('validate', 'Validate'), ('cancel', 'Cancel')],
                             string='State', default='draft', track_visibility='onchange')

    _sql_constraints = [
        ('date_check', "CHECK (date_start <= date_end)","The start date must be anterior to the end date."),
    ]

    @api.multi
    def act_validate(self):
        self.state = 'validate'

    @api.multi
    def act_cancel(self):
        self.state = 'cancel'

    @api.constrains('date_start', 'date_end')
    def _check_date(self):
        for absence in self:
            domain = [
                ('date_start', '<=', absence.date_start),
                ('date_end', '>=', absence.date_end),
                ('employee_id', '=', absence.employee_id.id),
                ('id', '!=', absence.id),
                ('absence_type_id', '=', absence.absence_type_id.id),
                ('state', '=', 'validate'),
            ]
            nabsences = self.search_count(domain)
            if nabsences:
                raise ValidationError(_('You can not have 2 absences that overlaps on same day!'))

class HrAbsenceLine(models.Model):
    _name = "hr.absence.line"
    _description = "Line Absence"

    @api.one
    @api.depends('absence_id.company_id')
    def _get_company(self):
        if self.absence_id.company_id:
            self.company_id = self.absence_id.company_id

    absence_id = fields.Many2one('hr.absence', "Absence", required=True)
    company_id = fields.Many2one('res.company', string='Company', compute='_get_company')
    employee_id = fields.Many2one('hr.employee', "Employee", required=True, domain="[('company_id','=',company_id)]")
    nbr_day = fields.Integer('Number of day', required=True)
    note = fields.Char(string="Note", translate=True)

class HrAbsenceType(models.Model):
    _name = "hr.absence.type"
    _description = "Type Absence"

    name = fields.Char(string='Type', required=True)
    absence_categ_id = fields.Many2one('hr.absence.category', string='Absence category', required=True)
    nbr_limit_day = fields.Float('Number limit of day', required=True)

class HrAbsenceCategory(models.Model):
    _name = "hr.absence.category"
    _description = "Category Absence"

    name = fields.Char(string='Category', required=True)
    absence_types = fields.One2many('hr.absence.type',  'absence_categ_id', string='Absence Type')

class HrSuspension(models.Model):
    _name = "hr.suspension"
    _description = "Suspension"
    _inherit = ['mail.thread']

    name = fields.Char(string="Name", copy=False, readonly=True, default= lambda self: self.env['ir.sequence'].next_by_code('suspension.default.seq'))
    company_id = fields.Many2one('res.company', string='Company', related='employee_id.company_id')
    employee_id = fields.Many2one('hr.employee', "Employee", required=True,)
    date_start =  fields.Date('Start Date', required=True,)
    date_end = fields.Date(string='Date End', )
    motif = fields.Char(string="Motif", translate=True, required=True)
    notes = fields.Text(string="Notes", translate=True)
    state = fields.Selection([('draft', 'Draft'), ('validate', 'Validate'),('lifting_suspension', 'Lifting of suspension'), ('close_suspension', 'Close suspension'), ('cancel', 'Cancel')],
                             string='State', default='draft', track_visibility='onchange')

    _sql_constraints = [
        ('date_check', "CHECK (date_start <= date_end)","The start date must be anterior to the end date."),
    ]

    @api.multi
    def act_validate(self):
        self.state = 'validate'

    @api.multi
    def act_lifting_suspension(self):
        self.state = 'lifting_suspension'

    @api.multi
    def act_close_suspension(self):
        if not self.date_end:
            raise ValidationError(_('You must enter an end date!'))
        else:
            self.state = 'close_suspension'

    @api.multi
    def act_cancel(self):
        self.state = 'cancel'

    @api.constrains('date_start', 'date_end')
    def _check_date(self):
        for supension in self:
            domain = [
                ('date_start', '<=', supension.date_start),
                ('date_end', '>=', supension.date_end),
                ('employee_id', '=', supension.employee_id.id),
                ('id', '!=', supension.id),
                ('state', '=', 'validate'),
            ]
            nsupensions = self.search_count(domain)
            if nsupensions:
                raise ValidationError(_('You can not have 2 suspension that overlaps on same day!'))
