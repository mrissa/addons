# -*- coding: utf-8 -*-
# Copyright 2013 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo import tools, _

AVAILABLE_PRIORITIES = [
    ('0', 'Level 0'),
    ('1', 'Level 1'),
    ('2', 'Level 2'),
    ('3', 'Level 3'),
    ('4', 'Level 4'),
    ('5', 'Level 5'),
    ('6', 'Level 6'),
    ('7', 'Level 7'),
    ('8', 'Level 8'),
    ('9', 'Level 9'),
    ('10', 'Level 10')
]

class HrSkill(models.Model):
    _name = 'hr.skill'

    name = fields.Many2one('skill.qualification', 'Qualification', required=True)
    employee_id = fields.Many2one('hr.employee', 'Employee(s)', required=True)
    #discipline_id = fields.Many2one('skill.discipline', 'Discipline')
    matricule = fields.Char(string='Matricule', related="employee_id.identification_id", readonly=True)
    date = fields.Date('Date acquisition')
    note = fields.Text('Commentaires', translate=True)
    experience = fields.Integer('Nbre annee experience')
    level = fields.Selection(AVAILABLE_PRIORITIES, 'Level')

class SkillDiscipline(models.Model):
    _name = 'skill.discipline'

    name = fields.Char('Name', required=True, translate=True)
    code = fields.Char('code', required=True, translate=True)
    line_ids = fields.One2many('skill.discipline.line', 'discipline_id', string='line descipline')

class SkillDisciplineLine(models.Model):
    _name = 'skill.discipline.line'

    discipline_id = fields.Many2one('skill.discipline', 'Discipline')
    level_id = fields.Many2one('skill.level', 'Level Teaching', required=True)
    qualification_id = fields.Many2one('skill.qualification', 'Qualification', required=True)

class SkillLevel(models.Model):
    _name = 'skill.level'

    name = fields.Char('Level', required=True, translate=True)

class SkillQualification(models.Model):
    _name = 'skill.qualification'

    name = fields.Char('Qualification', required=True, translate=True)
    line_ids = fields.One2many('skill.discipline.line', 'qualification_id', string='line qualification')