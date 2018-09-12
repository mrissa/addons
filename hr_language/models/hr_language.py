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
from odoo.exceptions import ValidationError

AVAILABLE_PRIORITIES = [
    ('0', 'Niveau 0'),
    ('1', 'Niveau 1'),
    ('2', 'Niveau 2'),
    ('3', 'Niveau 3'),
    ('4', 'Niveau 4'),
    ('5', 'Niveau 5'),
    ('6', 'Niveau 6'),
    ('7', 'Niveau 7'),
    ('8', 'Niveau 8'),
    ('9', 'Niveau 9'),
    ('10', 'Niveau 10')
]

class hr_language(models.Model):
    _name = 'hr.language'
    _inherit = ['mail.thread']

    name = fields.Selection(
        tools.scan_languages(),
        string='Language', required=True,)
    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=True)
    can_read = fields.Selection(AVAILABLE_PRIORITIES, 'Read')
    can_write = fields.Selection(AVAILABLE_PRIORITIES, 'Write')
    can_speak = fields.Selection(AVAILABLE_PRIORITIES, 'Speak')
    date = fields.Date('Update date')
    note = fields.Text('Commentaires', translate=True)

class hr_employee(models.Model):
    _inherit = 'hr.employee'

    language_ids = fields.One2many('hr.language', 'employee_id', string='Languages')