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

from odoo import models, fields

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    name = fields.Char(related='resource_id.name', store=True, oldname='name_related', translate=True)
    place_of_birth = fields.Char('Lieu de naissance', translate=True)
    state_birth = fields.Many2one('nmcl.state', string='State of birth', ondelete='restrict')
    city_birth = fields.Many2one('nmcl.city', string='City of birth', domain="[('state_id','=',state_birth)]")
    town_birth = fields.Many2one('nmcl.town', string='Town of birth', domain="[('city_id','=',city_birth)]")
    state_residence = fields.Many2one('nmcl.state', string='State of residence', ondelete='restrict')
    city_residence = fields.Many2one('nmcl.city', string='City of residence', domain="[('state_id','=',state_residence)]")
    town_residence = fields.Many2one('nmcl.town', string='Town of residence', domain="[('city_id','=',city_residence)]")
    nationality_id = fields.Many2one('res.country', string='Nationality 2', ondelete='restrict')
    adress = fields.Text('Adresse postal', translate=True)
    adress_birth = fields.Text('Adresse birth', translate=True)
    nni = fields.Char(string='NNI', size=10)
    cnam = fields.Char(string='CNAM')
    status = fields.Many2one('hr.status', string='Status')
    state = fields.Many2one('hr.state', string='State')
    classifying = fields.Many2one('hr.classifying', string='Classifying')
    is_employee = fields.Boolean('Is Employee', default=False)
    recruitment_type = fields.Selection(
        [('aucun', 'En instance'), ('employee', 'Employee'), ('pnp', 'PNP'), ('contractual', 'Contractual'), ('prived', 'Prived employee'), ('detached', 'Détaché')],
        string='Recruitment Type', default='aucun', readonly=True)
    ref_autorisation = fields.Char(string='REF Autorisation')
    date_autorisation = fields.Date(string='Date Autorisation')

    _sql_constraints = [
        ('nni_uniq', 'unique(nni)',
         'The NNI must be unique.')
    ]

class HrGrade(models.Model):
    _name = 'hr.grade'
    _description = 'Employee Grade'

    name = fields.Char(string='Employee Grade', translate=True, required=True)

class HrEchelle(models.Model):
    _name = 'hr.echelle'
    _description = 'Employee Echelle'

    name = fields.Char(string='Employee Echelle', translate=True, required=True)

class HrEchelon(models.Model):
    _name = 'hr.echelon'
    _description = 'Employee Echelon'

    name = fields.Char(string='Employee Echelon', translate=True, required=True)

class HrIndice(models.Model):
    _name = 'hr.indice'
    _description = 'Employee Indice'

    name = fields.Char(string='Employee Indice', translate=True, required=True)

class HrStatus(models.Model):
    _name = 'hr.status'
    _description = 'Employee Status'

    name = fields.Char(string='Status', translate=True, required=True)

class HrState(models.Model):
    _name = 'hr.state'
    _description = 'Employee state'

    name = fields.Char(string='State', translate=True, required=True)

class HrClassifying(models.Model):
    _name = 'hr.classifying'
    _description = 'Classifying'

    name = fields.Char(string='Classifying', translate=True, required=True)