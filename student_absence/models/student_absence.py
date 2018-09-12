# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
from datetime import datetime

class StudAbsence(models.Model):
    _name = "stud.absence"
    _description = "Student Absence"
    _inherit = ['mail.thread']

    @api.one
    @api.depends('date', 'date_end')
    def _get_number_of_days(self):
        if self.date_end and self.date:
            fmt = '%Y-%m-%d'
            date = self.date
            date_end = self.date_end
            d1 = datetime.strptime(date, fmt)
            d2 = datetime.strptime(date_end, fmt)
            daysDiff = str((d2 - d1).days)
            self.nbr_day = float(daysDiff)

    date = fields.Date(string="Date Debut", required=True)
    date_end = fields.Date(string="Date End", required=True)
    student_id = fields.Many2one('stud.student', "Student", required=True)
    categ_id = fields.Many2one('stud.absence.category', "Category Absence", required=True)
    type_id = fields.Many2one('stud.absence.type', string='Type', required=True, domain="[('categ_id','=',categ_id)]")
    nbr_day = fields.Float('Number of day', required=True, compute='_get_number_of_days')
    reason = fields.Char('Reason', translate=True)
    note = fields.Char(string="Note", translate=True)
    state = fields.Selection([('draft', 'Draft'), ('validate', 'Validate'), ('cancel', 'Cancel')],
                             string='State', default='draft')
    _sql_constraints = [
        ('date_check', "CHECK (date <= date_end)","The start date must be anterior to the end date."),
    ]

    @api.multi
    def act_validate(self):
        self.state = 'validate'

    @api.multi
    def act_cancel(self):
        self.state = 'cancel'

    @api.constrains('date', 'date_end')
    def _check_date(self):
        for absence in self:
            domain = [
                ('date', '<=', absence.date),
                ('date_end', '>=', absence.date_end),
                ('student_id', '=', absence.student_id.id),
                ('id', '!=', absence.id),
                ('type_id', '=', absence.type_id.id),
                ('state', '=', 'validate'),
            ]
            nabsences = self.search_count(domain)
            if nabsences:
                raise ValidationError(_('You can not have 2 absences that overlaps on same day!'))

class StudAbsenceType(models.Model):
    _name = "stud.absence.type"
    _description = "Student Type Absence"

    name = fields.Char(string='Type', required=True)
    categ_id = fields.Many2one('stud.absence.category', string='Absence category', required=True)

class StudAbsenceCateg(models.Model):
    _name = "stud.absence.category"
    _description = "Student Absence Category"
    _inherit = ['mail.thread']

    name = fields.Char(string="Name", translate=True, required=True)
    absence_types = fields.One2many('stud.absence.type', 'categ_id', string='Absence Type')

class StudStudent(models.Model):
    _inherit = 'stud.student'

    @api.multi
    def _absence_count(self):
        for each in self:
            absences_ids = self.env['stud.absence'].search([('student_id', '=', each.id)])
            each.absence_count = len(absences_ids)

    @api.multi
    def absence_view(self):
        self.ensure_one()
        domain = [
            ('student_id', '=', self.id)]
        return {
            'name': _('Absences'),
            'domain': domain,
            'res_model': 'stud.absence',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                                   Click to Create
                                </p>'''),
            'limit': 80,
        }

    absence_ids = fields.One2many('stud.absence', 'student_id', 'Absences')
    absence_count = fields.Integer(compute='_absence_count', string='Absences')