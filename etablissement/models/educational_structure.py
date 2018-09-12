# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource

class EducaEducation(models.Model):
    _name = "educa.education"
    _description = "Educa Education"
    _order = 'name'

    name = fields.Char(string="Name Of Education", required=True)

class EducaEducationFeliere(models.Model):
    _name = "educa.establishment.feliere"
    _description = "Educa Education Feliere"

    name = fields.Char(string="Name", required=True)

class EducaEducationLevel(models.Model):
    _name = "educa.establishment.level"
    _description = "Educa Education level"

    name = fields.Char(string="Name", required=True)

class EducaStructure(models.Model):
    _inherit = "educa.structure"

    @api.one
    @api.depends('level_id.name', 'feliere_id.name')
    def _get_name(self):
        if self.level_id and self.feliere_id:
            self.name = self.level_id.name + self.feliere_id.name

    name = fields.Char(string="Nom", required=True, translate=True, compute='_get_name')
    designation = fields.Char(string="Designation", translate=True)
    type_id = fields.Many2one('educa.establishment.type', string="Type Enseignement")
    level_id = fields.Many2one('educa.establishment.level', string="Level", required=True)
    feliere_id = fields.Many2one('educa.establishment.feliere', string="Fliere", required=True)
    notes = fields.Text('Notes')
    type = fields.Selection([('fondamentale', 'Fondamentale'), ('secondaire', 'Secondaire')], string='Type',
                            required=True)
    cycle = fields.Many2one('educa.establishment.cycle', string="Cycle", domain="[('type', '=', type)]")

class EducaSection(models.Model):
    _name = "educa.section"
    _description = "Name Section"

    name = fields.Char(string="Name", required=True, translate=True)
