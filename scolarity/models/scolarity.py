# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import logging
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)

class EducaEtabSection(models.Model):
    _inherit = "educa.etab.section"

    inscription_ids = fields.Many2many('stud.inscription', 'section_inscription_rel', 'inscription_id', 'section_id', string='Elèves')

class EducaEtabSectionLine(models.Model):
    _inherit = "educa.etab.section.line"

    employee_id = fields.Many2one('hr.employee', string='Employé', required=True)

class EducaStructure(models.Model):
    _inherit = "educa.structure"

    scholarly_id = fields.Many2one('year.scholarly', string='Scholarly')
    line_ids = fields.One2many('line.structure', 'structure_id', string='Discipline')

class StructureLine(models.Model):
    _name = "line.structure"

    @api.one
    @api.depends('scholarly_line_id.section_number')
    def _get_count_section(self):
        if self.scholarly_line_id.section_number:
            self.count_section = self.scholarly_line_id.section_number

    @api.one
    @api.depends('volume_horaire', 'count_section')
    def _get_count_volume_horaire(self):
        if self.count_section and self.volume_horaire:
            self.volume_horaire_total = self.volume_horaire * self.count_section

    structure_id = fields.Many2one('educa.structure', string='Structure pedagogique')
    discipline_id = fields.Many2one('skill.discipline', string='Discipline')
    volume_horaire = fields.Float(string='Volume Horraire Unitaire', )
    count_section = fields.Float(string='Section', compute='_get_count_section')
    volume_horaire_total = fields.Float(string='Volume Horraire', compute='_get_count_volume_horaire')
    scholarly_line_id = fields.Many2one('year.scholarly.line', string='Scolarité')

class YearScolarityLine(models.Model):
    _inherit = "year.scholarly.line"

    @api.one
    @api.depends('inscription_ids')
    def _inscription_count(self):
        if self.inscription_ids:
            # inscription
            count = len(self.inscription_ids)
            self.inscriptions_count = count
            # inscription_redoublant
            inscription_redoublant = self.env['stud.inscription'].search(
                [('structure', '=', self.name), ('state', '=', 'redoublant'),
                 ('id', 'in', self.scholarly_id.inscription_ids.ids)])
            if inscription_redoublant:
                count_re = len(inscription_redoublant)
                self.redoubles_count = count_re
            # inscription_exclu
            inscription_exclu = self.env['stud.inscription'].search(
                [('structure', '=', self.name), ('state', '=', 'exclu'),
                 ('id', 'in', self.scholarly_id.inscription_ids.ids)])
            if inscription_exclu:
                count_ex = len(inscription_exclu)
                self.exclu_count = count_ex
            # inscription_abandonner
            inscription_abandonner = self.env['stud.inscription'].search(
                [('structure', '=', self.name), ('state', '=', 'abandonner'),
                 ('id', 'in', self.scholarly_id.inscription_ids.ids)])
            if inscription_abandonner:
                count_ab = len(inscription_abandonner)
                self.abandonner_count = count_ab
            # inscription_admis
            inscription_admis = self.env['stud.inscription'].search(
                [('structure', '=', self.name), ('state', '=', 'admis'),
                 ('id', 'in', self.scholarly_id.inscription_ids.ids)])
            if inscription_admis:
                count_admis = len(inscription_admis)
                self.admis_count = count_admis
            # inscriptions_male
            inscriptions_male = self.env['stud.inscription'].search(
                [('structure', '=', self.name), ('id', 'in', self.scholarly_id.inscription_ids.ids)])
            if inscriptions_male:
                count_male = 0
                for inscription in inscriptions_male:
                    if inscription.student_id.gender == 'male':
                        count_male = count_male + 1
                self.inscriptions_male = count_male
            # inscriptions_female
            inscriptions_female = self.env['stud.inscription'].search(
                [('structure', '=', self.name), ('id', 'in', self.scholarly_id.inscription_ids.ids)])
            if inscriptions_female:
                count_female = 0
                for inscription in inscriptions_female:
                    if inscription.student_id.gender == 'female':
                        count_female = count_female + 1
                self.inscriptions_female = count_female
            # inscriptions_female_redoublant
            inscriptions_female_redoublant = self.env['stud.inscription'].search(
                [('structure', '=', self.name), ('id', 'in', self.scholarly_id.inscription_ids.ids),
                 ('state', '=', 'redoublant')])
            if inscriptions_female_redoublant:
                count_f_re = 0
                for inscription in inscriptions_female_redoublant:
                    if inscription.student_id.gender == 'female':
                        count_f_re = count_f_re + 1
                self.inscriptions_female_redoublant = count_f_re

    line_ids = fields.One2many('line.structure', 'scholarly_line_id', string='Discipline')
    etablissement_id = fields.Many2one('educa.establishment', string='Etablissement',)
    inscriptions_count = fields.Integer(string='Elève', compute='_inscription_count', store=True)
    inscriptions_female = fields.Integer(string='Filles', compute='_inscription_count', store=True)
    inscriptions_male = fields.Integer(string='Garçons', compute='_inscription_count', store=True)
    redoubles_count = fields.Integer(string='Redoublants', compute='_inscription_count', store=True)
    admis_count = fields.Integer(string='Admis', compute='_inscription_count', store=True)
    exclu_count = fields.Integer(string='Exlus', compute='_inscription_count', store=True)
    abandonner_count = fields.Integer(string='Abondonnées', compute='_inscription_count', store=True)
    redouble_fille_count = fields.Integer(string='Redoublants filles', compute='_inscription_count', store=True)

class YearScolarity(models.Model):
    _inherit = "year.scholarly"

    @api.one
    @api.depends('etablissement_id')
    def _get_emp_ids(self):
        if self.etablissement_id:
            assignment_line = self.env['hr.assignment.line'].search([('lieu', '=', self.etablissement_id.id)])
            list = []
            if assignment_line:
                for assg in assignment_line:
                    list.append(assg.employee_id.id)
                employees = self.env['hr.employee'].search([('id', 'in', list)])
                if employees:
                    self.employee_ids = employees
                self.assig_ids = assignment_line
        else:
            list = []
            scolarity_records = self.env['year.scholarly'].search([('id', 'child_of', self.id)])
            if scolarity_records:
                for scolarity in scolarity_records:
                    if scolarity.employee_ids:
                        for emp in scolarity.employee_ids:
                            list.append(emp.id)
            employees = self.env['hr.employee'].search([('id', 'in', list)])
            if employees:
                self.employee_ids = employees

    line_ids = fields.One2many('year.scholarly.line', 'scholarly_id', string='Structure pedagogique')
    dren_ids = fields.Many2many('nmcl.state', 'scolarity_dren_state_rel', 'state_id', 'scholarly_id', string='DREN')
    etablissement_id = fields.Many2one('educa.establishment', string='Etablissement',)
    etablissement_ids = fields.Many2many('educa.establishment', 'scolarite_etablissement_rel', 'establishment_id', 'scholarly_id', string='Etablissements', domain="[('type','=',type), ('state_id','in', dren_ids)]")
    task_ids = fields.One2many('project.task', 'scholarly_id', string='Tâches')
    employee_ids = fields.One2many('hr.employee', compute='_get_emp_ids', string='Employés')
    assig_ids = fields.One2many('hr.assignment.line', compute='_get_emp_ids', string='Affectation emp')
    strat_date = fields.Date('Date début')
    end_date = fields.Date('Date fin')

    @api.multi
    def act_open(self):
        structure = self.env['year.scholarly.line']
        structure_line = self.env['line.structure']
        open_year=self.search([('state','=','open'),('id','!=',self.id),('type','=',self.type),('niveau','=',self.niveau)])
        if open_year:
            raise ValidationError(_('you can not have two school years open at the same time!'))
        if self.niveau == 'central' and self.type == 'central':
            self.create({'year_start':self.year_start,
                         'parent_id':self.id,
                         'type': 'fondamentale',
                         'chaine': 'Fondamentale',
                        })
            self.create({'year_start': self.year_start,
                         'parent_id': self.id,
                         'type': 'secondaire',
                         'chaine': 'Secondaire',
                         })
            self.state = 'open'
        elif self.niveau == 'central' and self.type != 'central':
            if self.dren_ids:
                for dren in self.dren_ids:
                    etablissement_ids = self.env['educa.establishment'].search([('state_id','=',dren.id), ('id','in',self.etablissement_ids.ids)])
                    new=self.create({'year_start': self.year_start,
                                 'parent_id': self.id,
                                 'type': self.type,
                                 'niveau': 'dren',
                                 'chaine': dren.name+' '+str(self.type),
                                 'etablissement_ids': [(6,0,etablissement_ids.ids)]
                                 })
                    for line in self.line_ids:
                        new_str=structure.create({'scholarly_id': new.id,
                                          'structure_id': line.structure_id.id,
                                         })
                        for discipline in line.line_ids:
                            structure_line.create({'scholarly_line_id': new_str.id,
                                                   'discipline_id': discipline.discipline_id.id,
                                                   'volume_horaire': discipline.volume_horaire
                                                 })
            self.state = 'open'
        elif self.niveau == 'dren' and self.type != 'central':
            if self.etablissement_ids:
                for etab in self.etablissement_ids:
                    new=self.create({'year_start': self.year_start,
                                 'parent_id': self.id,
                                 'type': self.type,
                                 'niveau': 'etablissement',
                                 'chaine': etab.name+' '+str(self.type),
                                 'line_ids': self.line_ids,
                                 'etablissement_id': etab.id,
                                 })
                    for line in self.line_ids:
                        new_str=structure.create({'scholarly_id': new.id,
                                          'structure_id': line.structure_id.id,
                                          'etablissement_id': etab.id,
                                          })
                        for discipline in structure.line_ids:
                            structure_line.create({'scholarly_line_id': new_str.id,
                                                   'discipline_id': discipline.discipline_id.id,
                                                   'volume_horaire': discipline.volume_horaire
                                                   })
            self.state = 'open'
        else:
            self.state = 'open'

class ProjectTask(models.Model):
    _inherit = "project.task"

    scholarly_id = fields.Many2one('year.scholarly', string='Année Scolaire',)