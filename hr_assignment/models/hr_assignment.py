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
import logging
_logger = logging.getLogger(__name__)

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.one
    @api.depends('assignment_line_ids')
    def _get_info_last_affectation(self):
        if self.assignment_line_ids:
            affectation = self.env['hr.assignment.line'].search([('employee_id', '=', self.id)], order='start_date_affect asc', limit=1)
            if affectation:
                self.fonction_id = affectation.fonction_new_id.id
                self.place_job_id = affectation.place_job_new_id.id
                self.establishment_id = affectation.establishment_new_id.id
                self.discipline_enseig_id = affectation.discipline_enseig_new_id.id

    position_id = fields.Many2one('hr.assignment.type', string='Position',)
    motif_id = fields.Many2one('hr.assignment.type.motif', string='Sous position',)
    fonction_id = fields.Many2one('hr.function', string='Fonction',)
    place_job_id = fields.Many2one('hr.place.job', string='Lieu de travail', compute='_get_info_last_affectation')
    lieu_id = fields.Many2one('educa.establishment', string='Lieu de travail',)
    establishment_id = fields.Many2one('educa.establishment', string='Etablissement',)
    discipline_enseig_id = fields.Many2one('skill.discipline', string='Discipline Enseigné',)
    assignment_line_ids = fields.One2many('hr.assignment.line', 'employee_id', string='Assignments')

class HrAssignmentRequest(models.Model):
    _name = "hr.assignment.request"
    _description = "Request Assignment"
    _inherit = ['mail.thread']
    _order = "id desc"

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default=lambda self: self.env['ir.sequence'].next_by_code('request.assignement.default.seq'))
    date = fields.Date(string='Date', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True , domain="[('motif_id.code','=', '0101')]")
    ref_budget = fields.Char(string='Référence Budgétaire',)
    corps_id = fields.Many2one('hr.employee.corps', string='Corps', related='employee_id.corps_id', readonly=True)
    discipline_enseig_id = fields.Many2one('skill.discipline', string='Discipline de travail', related='employee_id.discipline_enseig_id', readonly=True )
    discipline_ids = fields.Many2many('skill.discipline', string='Discipline Formation',related='employee_id.discipline_ids', readonly=True)
    tel = fields.Char('Numéro Téléphone',)
    marital = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('cohabitant', 'Legal Cohabitant'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced')
    ], related='employee_id.marital', readonly=True)
    children = fields.Integer('Nombre enfant', related='employee_id.children', readonly=True)
    function_id = fields.Many2one('hr.function', string='Fonction', related='employee_id.fonction_id', readonly=True)
    anciente_generale= fields.Integer('Ancienté générale')
    anciente_state = fields.Integer('Ancienté wilaya')
    anciente_city = fields.Integer('Ancienté Moughataa')
    note_admin = fields.Float('Note administratif')
    note_ann1 = fields.Float('Note Année 1')
    note_ann2 = fields.Float('Note Année 2')
    note_ann3 = fields.Float('Note Année 3')
    assignment_choice1 = fields.Many2one('nmcl.state', string='Choix 1', required=True, domain="[('id','not in', (assignment_choice2, assignment_choice3))]")
    assignment_choice2 = fields.Many2one('nmcl.state', string='Choix 2', required=True, domain="[('id','not in', (assignment_choice1, assignment_choice3))]")
    assignment_choice3 = fields.Many2one('nmcl.state', string='Choix 3', required=True, domain="[('id','not in', (assignment_choice1, assignment_choice2))]")
    state = fields.Selection([('draft', 'Draft'), ('establishment_validate', 'Establishment validate'),
                              ('regional_validate', 'Regional Validate'), ('central_validate', 'Central Validate'),
                              ('objection', 'Objection'), ('refused', 'Refused')],
                             string='State', default='draft', track_visibility='onchange')
    notes = fields.Text(string='Notes')
    affectation_ids = fields.Many2many('hr.assignment', 'request_assignment_rel', 'assignment_id', 'request_id', string='Affectation')

    @api.multi
    def act_establishment_validate(self):
        self.state = 'establishment_validate'

    @api.multi
    def act_regional_validate(self):
        self.state = 'regional_validate'

    @api.multi
    def act_central_validate(self):
        if self.assignment_choice1:
            self.employee_id.assignment_choice1 = self.assignment_choice1.id
        if self.assignment_choice2:
            self.employee_id.assignment_choice2 = self.assignment_choice2.id
        if self.assignment_choice3:
            self.employee_id.assignment_choice3 = self.assignment_choice3.id
        position = self.env['hr.assignment.type'].search([('code', '=', '01')])
        motif = self.env['hr.assignment.type.motif'].search([('code', '=', '0102')])
        if position:
            self.employee_id.position_id = position.id
        if motif:
            self.employee_id.motif_id = motif.id
        self.state = 'central_validate'

    @api.multi
    def act_refused(self):
        self.state = 'refused'

    @api.multi
    def act_objection(self):
        self.state = 'objection'

class HrAssignment(models.Model):
    _name = "hr.assignment"
    _description = "Assignment"
    _inherit = ['mail.thread']
    _order = "id desc"

    @api.one
    @api.depends('liste_employee_ids')
    def _get_record_count(self):
        if self.liste_employee_ids:
            self.is_records_line = True
        else:
            self.is_records_line = False

    @api.one
    @api.depends('line_ids', 'type')
    def _get_employees(self):
        if self.line_ids and self.type != 'affectation':
            list = []
            for line in self.line_ids:
                list.append(line.employee_id.id)
            employees = self.env['hr.employee'].search([('id', 'in', list)]).ids
            if employees:
                self.employee_check_ids = employees

    @api.one
    @api.depends('type')
    def _get_employees_en_cours_affect(self):
        affectations = self.env['hr.assignment'].search([('state', '!=', 'approved')])
        if affectations:
            list = []
            for affect in affectations:
                for line in affect.liste_employee_ids:
                    list.append(line.id)
            employees = self.env['hr.employee'].search([('id', 'in', list)])
            if employees:
                self.employees_en_cours_affect = employees

    @api.one
    @api.depends('employee_ids', 'type', 'assignment_request_ids')
    def _get_liste_employee(self):
        if self.type == 'affectation':
            employee_list = []
            if self.employee_ids:
                for employee in self.employee_ids:
                    employee_list.append(employee.id)
            if self.assignment_request_ids:
                for request_assignment_record in self.assignment_request_ids:
                    if request_assignment_record.employee_id.id not in employee_list:
                        employee_list.append(request_assignment_record.employee_id.id)
            if employee_list:
                employees = self.env['hr.employee'].search(
                    [('id', 'in', employee_list)])
                self.liste_employee_ids = employees

    type = fields.Selection([('affectation', 'Affectation'), ('nomination', 'Nomination'), ('positionnement', 'Positionnement')],
                             string='Type',)
    type_affect = fields.Selection(
        [('prof', 'Professeur'), ('inst', 'Instituteur'), ('administratif', 'Administratif'), ('nomination', 'Nomination')],
        string='Type Affectation', )
    type_id = fields.Many2one('hr.type.function', string='Type fonction',)
    name = fields.Char(string='Numéro Arrêté', required=True, copy=False)
    date = fields.Date(string='Date', required=True)
    start_date_affect = fields.Date(string='Date d\'éffet')
    lien = fields.Many2many(comodel_name="ir.attachment",
                                relation="ir_assignment_rel",
                                column1="assignment_id",
                                column2="attachment_id",
                                string="Lien note service")
    state = fields.Selection([('draft', 'Préparation'), ('pending_approved', 'Affectation en cours'), ('approved', 'Approuvé')],
                             string='State', default='draft', )
    notes = fields.Text(string='Notes')
    #champs type affectation
    liste_employee_ids = fields.One2many('hr.employee', compute='_get_liste_employee')
    employee_ids = fields.Many2many('hr.employee', 'employee_assignment_rel', 'employee_id', 'assignment_id', string='Employés', domain="[('position_id.code','=', '01'), ('motif_id.code','=', '0102'), ('id','not in', employees_en_cours_affect)]")
    employees_en_cours_affect = fields.One2many('hr.employee', compute='_get_employees_en_cours_affect')
    assignment_request_ids = fields.Many2many('hr.assignment.request', 'request_assignment_rel', 'request_id', 'assignment_id', string='Demande de réaffectation', domain="[('state','=', 'central_validate'), ('affectation_ids', '=', False)]")
    employee_check_ids = fields.One2many('hr.employee', compute='_get_employees')
    line_ids = fields.One2many('hr.assignment.line', 'assignment_id', string='Assignment Line')
    #champs type positionnement
    position_id = fields.Many2one('hr.assignment.type', string='Position',)
    motif_id = fields.Many2one('hr.assignment.type.motif', string='Sous position', domain="[('assignmen_type_id','=', position_id)]")
    is_records_line = fields.Boolean(string='Employé existe', default=False, compute='_get_record_count')
    line_statistique_ids = fields.One2many('hr.assignment.stat', 'assignment_id')

    @api.multi
    def act_remetrre_en_brouillon(self):
        self.state = 'draft'
        for line in self.line_ids:
            line.state = self.state

    @api.multi
    def act_attend_approved(self):
        if not self.liste_employee_ids:
            raise ValidationError("Il faut selectionner au moin un employe!")
        else:
            states = self.env['nmcl.state'].search([])
            for state in states:
                self.env['hr.assignment.stat'].create({'assignment_id': self.id,
                                                       'state_id': state.id})
            if self.type == 'affectation':
                lines = []
                for employee in self.liste_employee_ids:
                    line_item = {
                        'employee_id': employee.id,
                    }
                    lines += [line_item]
                self.update({'line_ids': lines or False})
            self.state = 'pending_approved'
            for line in self.line_ids:
                line.state = self.state

    @api.multi
    def act_approved(self):
        list =[]
        for line in self.line_ids:
            if self.type == 'affectation':
                if not self.start_date_affect:
                    raise ValidationError("Merci de remplir le champ date Efffet!")
                if self.type_affect!='administratif':
                    if not line.establishment_new_id or not line.fonction_new_id or not line.discipline_enseig_new_id:
                        raise ValidationError("Merci de remplir les champs affectations!")
                if self.type_affect=='administratif':
                    if not line.establishment_new_id or not line.fonction_new_id or not line.lieu:
                        raise ValidationError("Merci de remplir les champs affectations!")
                position = self.env['hr.assignment.type'].search([('code', '=', '01')])
                motif = self.env['hr.assignment.type.motif'].search([('code', '=', '0101')])
                if position:
                    line.employee_id.position_id = position.id
                    self.position_id = position.id
                if motif:
                    line.employee_id.motif_id = motif.id
                    self.motif_id = motif.id
                line.employee_id.establishment_id = line.establishment_new_id.id
                line.employee_id.lieu_id = line.lieu.id
                line.employee_id.fonction_id = line.fonction_new_id.id
                line.employee_id.discipline_enseig_id = line.discipline_enseig_new_id.id
            if self.type == 'positionnement':
                line.employee_id.position_id = self.position_id.id
                line.employee_id.motif_id = self.motif_id.id
            #cloturer tout les lignes affectation précédante
            assignments = self.env['hr.assignment.line'].search(
                [('employee_id', '=', line.employee_id.id), ('state', '=', 'approved'),
                 ('assignment_id', '!=', self.id)])
            if assignments:
                for assignment in assignments:
                    assignment.state = 'closed'
                    assignment.end_date_affect = self.start_date_affect
            if line.establishment_new_id.id not in list:
                list.append(line.establishment_new_id.id)
        etablissements = self.env['educa.establishment'].search([('id', 'in', list)])
        if etablissements:
            for etab in etablissements:
                line_ids = self.env['hr.assignment.line'].search([('assignment_id','=',self.id), ('establishment_new_id','=',etab.id)])
                _logger.info("------data lines------%s", line_ids)
                assig_regional=self.env['hr.assignment.regional']
                assig_reg = assig_regional.create({'name': self.name,
                                                   'date': self.date,
                                                   'start_date_affect': self.start_date_affect,
                                                   'establishment_id': etab.id,
                                                   'assignment_id': self.id,
                                                   'type_id': self.type_id.id,
                                                   'type_affect': self.type_affect,
                                                   })
                for line in line_ids:
                    line.update({'assignment_reg_id': assig_reg.id})
        self.state = 'approved'
        for line in self.line_ids:
            line.state = self.state

class HrAssignmentLine(models.Model):
    _name = "hr.assignment.line"
    _description = "Assignment Line"

    @api.one
    @api.depends('employee_id')
    def _get_info_employee(self):
        if self.employee_id:
            self.identification_id = self.employee_id.identification_id
            self.nni = self.employee_id.nni
            self.birthday = self.employee_id.birthday
            self.place_of_birth = self.employee_id.place_of_birth
            self.discipline_ids = self.employee_id.discipline_ids.ids
            self.corps_id = self.employee_id.corps_id.id
            self.corps_id = self.employee_id.corps_id.id
            self.note_graduation = self.employee_id.note_graduation
            self.number_training_school = self.employee_id.number_training_school
            self.assignment_choice1 = self.employee_id.assignment_choice1.id
            self.assignment_choice2 = self.employee_id.assignment_choice2.id
            self.assignment_choice3 = self.employee_id.assignment_choice3.id
            self.assignment_choice4 = self.employee_id.assignment_choice4.id
            self.assignment_choice5 = self.employee_id.assignment_choice5.id
            self.establishment_id = self.employee_id.establishment_id.id
            self.discipline_enseig_id = self.employee_id.discipline_enseig_id.id
            self.fonction_id = self.employee_id.fonction_id.id
            self.position_id = self.employee_id.position_id.id
            self.motif_id = self.employee_id.motif_id.id
            self.place_job_id = self.employee_id.place_job_id.id

    @api.one
    @api.depends('assignment_id')
    def _get_info_assignment(self):
        if self.assignment_id.position_id:
            self.position_new_id = self.assignment_id.position_id.id
        if self.assignment_id.motif_id:
            self.motif_new_id = self.assignment_id.motif_id.id
        if self.assignment_id.start_date_affect:
            self.start_date_affect = self.assignment_id.start_date_affect

    assignment_id = fields.Many2one('hr.assignment', string='Assignment')
    assignment_reg_id = fields.Many2one('hr.assignment.regional', string='Affectation régional')
    type_id = fields.Many2one('hr.type.function', 'Type fonction', related='assignment_id.type_id')
    # champs info employe
    employee_id = fields.Many2one('hr.employee', string='Nom et prénom')
    identification_id = fields.Char('Matricule', compute='_get_info_employee')
    nni = fields.Char('NNI', compute='_get_info_employee')
    birthday = fields.Date('Date de naissance', compute='_get_info_employee')
    place_of_birth = fields.Char('Lieu de naissance', compute='_get_info_employee')
    discipline_ids = fields.Many2many('skill.discipline', compute='_get_info_employee', string='Discipline Employee')
    assignment_choice1 = fields.Many2one('nmcl.state', string='Choix 1', compute='_get_info_employee', store=True)
    assignment_choice2 = fields.Many2one('nmcl.state', string='Choix 2', compute='_get_info_employee', store=True)
    assignment_choice3 = fields.Many2one('nmcl.state', string='Choix 3', compute='_get_info_employee', store=True)
    assignment_choice4 = fields.Many2one('nmcl.state', string='Choix 4', compute='_get_info_employee',)
    assignment_choice5 = fields.Many2one('nmcl.state', string='Choix 5', compute='_get_info_employee',)
    note_graduation = fields.Float(string='Moyenne réussite', compute='_get_info_employee',)
    number_training_school = fields.Char(String='Rang', compute='_get_info_employee',)
    # champs situation actuel employe
    corps_id = fields.Many2one('hr.employee.corps', string='Corps', compute='_get_info_employee', store=True)
    establishment_id = fields.Many2one('educa.establishment', string='Etablissement', compute='_get_info_employee',
                                       store=True)
    discipline_enseig_id = fields.Many2one('skill.discipline', string='Discipline Enseigné',
                                           compute='_get_info_employee', store=True)
    fonction_id = fields.Many2one('hr.function', string='Fonction', compute='_get_info_employee', store=True)
    position_id = fields.Many2one('hr.assignment.type', string='Position', compute='_get_info_employee', store=True)
    motif_id = fields.Many2one('hr.assignment.type.motif', string='Sous position',
                               compute='_get_info_employee', store=True)
    place_job_id = fields.Many2one('hr.place.job', string='Lieu de travail actuel', compute='_get_info_employee',
                                   store=True)
    # champs nouvelle situation employe
    establishment_new_id = fields.Many2one('educa.establishment', string='Structure de rattachement',)
    discipline_enseig_new_id = fields.Many2one('skill.discipline', string='Disciplines',)
    fonction_new_id = fields.Many2one('hr.function', string='Fonction', domain="[('type_id','=', type_id)]")
    position_new_id = fields.Many2one('hr.assignment.type', string='Nouveau Position', compute='_get_info_assignment')
    motif_new_id = fields.Many2one('hr.assignment.type.motif', string='Nouveau Statut', compute='_get_info_assignment')
    place_job_new_id = fields.Many2one('hr.place.job', string='Lieu de travail')
    lieu = fields.Many2one('educa.establishment', string='Lieu affectation', domain="[('id','child_of', establishment_new_id), ('id','!=', establishment_new_id)]")
    remarque = fields.Char(string='Remarque')
    state = fields.Selection(
        [('draft', 'Draft'), ('pending_approved', 'Affectation en cours'), ('approved', 'Approuved'), ('closed', 'Closed')],
        string='State', default="draft", )
    start_date_affect = fields.Date(string='Date d\'éffet', compute='_get_info_assignment')
    end_date_affect = fields.Date(string='Date fin')
    type = fields.Selection(
        [('affectation', 'Affectation'), ('nomination', 'Nomination'), ('positionnement', 'Positionnement')],
        string='Type', related='assignment_id.type')
    type_affect = fields.Selection(
        [('prof', 'Professeur'), ('inst', 'Instituteur'), ('administratif', 'Administratif'), ('nomination', 'Nomination')],
        string='Type Affectation', related='assignment_id.type_affect')

class HrAssignmentRegional(models.Model):
    _name = "hr.assignment.regional"
    _description = "Affectation Régionale"
    _inherit = ['mail.thread']

    name = fields.Char(string='Référence', required=True, copy=False)
    date = fields.Date(string='Date', required=True)
    start_date_affect = fields.Date(string='Date d\'éffet')
    assignment_id = fields.Many2one('hr.assignment', string='Affectation')
    establishment_id = fields.Many2one('educa.establishment', string='Etablissement', required=True)
    type_affect = fields.Selection(
        [('prof', 'Professeur'), ('inst', 'Instituteur'), ('administratif', 'Administratif')],
        string='Type Affectation', )
    type_id = fields.Many2one('hr.type.function', string='Type fonction', required=True)
    lien = fields.Many2many(comodel_name="ir.attachment",
                            relation="ir_assignment_regional_rel",
                            column1="assignment_reg_id",
                            column2="attachment_id",
                            string="Lien")
    state = fields.Selection(
        [('affect', 'Affecté'), ('en_cours', 'En cours'), ('valide', 'Validé')],
        string='State', default='affect', track_visibility='onchange')
    notes = fields.Text(string='Notes')
    line_ids = fields.One2many('hr.assignment.line', 'assignment_reg_id', string='Ligne affectation')

    @api.multi
    def act_en_cours(self):
        self.state = 'en_cours'

    @api.multi
    def act_valide(self):
        if self.line_ids:
            for line in self.line_ids:
                if not line.lieu.id:
                    raise ValidationError("Merci de remplir les lieu de travail!")
                line.employee_id.lieu_id = line.lieu.id
        self.state = 'valide'

    @api.multi
    def act_remetrre_en_brouillon(self):
        self.state = 'affect'

class HrAssignmentStat(models.Model):
    _name = "hr.assignment.stat"
    _description = "Statistique Affectation"

    @api.one
    @api.depends('state_id')
    def _get_count_discipline(self):
        ar = 0
        fr = 0
        bil = 0
        if self.state_id:
            for line in self.assignment_id.line_ids:
                if line.employee_id.discipline_enseig_id.code == 'AR':
                    ar = ar + 1
                if line.employee_id.discipline_enseig_id.code == 'FR':
                    fr = fr + 1
                if line.employee_id.discipline_enseig_id.code == 'BIL':
                    bil = bil + 1
            self.count_discipline_ar = ar
            self.count_discipline_fr = fr
            self.count_discipline_bi = bil
            self.count_total = self.count_discipline_bi+self.count_discipline_fr+self.count_discipline_ar

    assignment_id = fields.Many2one('hr.assignment', string='Affectation')
    state_id = fields.Many2one('nmcl.state', string='DREN',)
    count_discipline_ar = fields.Integer(string='A', compute='_get_count_discipline', store=True)
    count_discipline_fr = fields.Integer(string='F', compute='_get_count_discipline', store=True)
    count_discipline_bi = fields.Integer(string='B', compute='_get_count_discipline', store=True)
    count_total = fields.Integer(string='Total', compute='_get_count_discipline', store=True)

class HrAssignmentType(models.Model):
    _name = "hr.assignment.type"
    _description = "Assignment Type"

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    motif_ids = fields.One2many('hr.assignment.type.motif', 'assignmen_type_id', string='Motif')

    _sql_constraints = [
        ('code_uniq', 'unique(code)',
         'Le code doit être unique.')
    ]

class HrAssignmentTypeMotif(models.Model):
    _name = "hr.assignment.type.motif"
    _description = "Assignment type motif"

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    assignmen_type_id = fields.Many2one('hr.assignment.type', 'Assignment Type')

    _sql_constraints = [
        ('code_uniq', 'unique(code)',
         'Le code doit être unique.')
    ]

class HrFunction(models.Model):
    _name = "hr.function"
    _description = "Function"

    name = fields.Char(string='Name', required=True)
    type_id = fields.Many2one('hr.type.function', 'Type fonction')

class HrTypeFunction(models.Model):
    _name = "hr.type.function"
    _description = "Type Fonction"

    name = fields.Char(string='Type Fonction', required=True)
    type = fields.Selection(
        [('prof', 'Professeur'), ('inst', 'Instituteur'), ('administratif', 'Administratif'), ('nomination', 'Nomination')],
        string='Type', )
    secondaire = fields.Boolean('Secondaire')

class ResCompany(models.Model):
    _inherit = 'res.company'

    assignment_type = fields.Selection(
        [('central', 'Central'), ('regional', 'Regional'), ('establishment', 'Establishment')],
        string='Assignment Type')

class ChangePosition(models.Model):
    _name = 'hr.change.position'
    _inherit = ['mail.thread']
    _order = "id desc"

    @api.one
    @api.depends('line_ids')
    def _get_employees(self):
        if self.line_ids:
            list = []
            for line in self.line_ids:
                list.append(line.employee_id.id)
            employees = self.env['hr.employee'].search([('id', 'in', list)]).ids
            if employees:
                self.employee_check_ids = employees

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default= lambda self: self.env['ir.sequence'].next_by_code('change.position.default.seq'))
    position_id = fields.Many2one('hr.assignment.type', string='Nouveau Position', required=True)
    motif_id = fields.Many2one('hr.assignment.type.motif', string='Nouveau statut', domain="[('assignmen_type_id','=', position_id)]", required=True)
    reference = fields.Char('Numéro Arrêté', required=True)
    date = fields.Date('Date Arrêté', required=True)
    date_effet = fields.Date('Date d\'effet', required=True)
    line_ids = fields.One2many('hr.change.position.line', 'change_position_id', string='Change Position Line')
    employee_check_ids = fields.One2many('hr.employee', compute='_get_employees')
    state = fields.Selection(
            [('draft', 'Brouillon'), ('validate', 'Valider')],
            string='State', default='draft', track_visibility='onchange')
    notes = fields.Text(string='Notes')

    @api.multi
    def act_validate(self):
        if not self.line_ids:
            raise ValidationError("Il faut séléctionner au moin un employé!")
        else:
            for line in self.line_ids:
                line.employee_id.position_id = self.position_id.id
                line.employee_id.motif_id = self.motif_id.id
            self.state = 'validate'

class HrChangePositionLine(models.Model):
    _name = 'hr.change.position.line'

    @api.one
    @api.depends('change_position_id.state')
    def _get_state(self):
        if self.change_position_id.state:
            self.state = self.change_position_id.state

    @api.one
    @api.depends('employee_id')
    def _get_info_employee(self):
        if self.employee_id:
            self.fonction_id = self.employee_id.fonction_id.id
            self.place_job_id = self.employee_id.place_job_id.id
            self.corps_id = self.employee_id.corps_id.id
            self.position_id = self.employee_id.position_id.id

    change_position_id = fields.Many2one('hr.change.position', string='Position')
    employee_id = fields.Many2one('hr.employee', string='Employé')
    identification_id = fields.Char('Matricule', related='employee_id.identification_id')
    nni = fields.Char('NNI', related='employee_id.nni')
    name = fields.Char('Nom et prénom', related='employee_id.name')
    corps_id = fields.Many2one('hr.employee.corps', string='Corps', compute='_get_info_employee', store=True)
    fonction_id = fields.Many2one('hr.function', string='Emploi', compute='_get_info_employee', store=True)
    place_job_id = fields.Many2one('hr.place.job', string='Lieu de travail', compute='_get_info_employee', store=True)
    position_id = fields.Many2one('hr.assignment.type', string='Position', compute='_get_info_employee', store=True)
    position_new_id = fields.Many2one('hr.assignment.type', string='Nouveau Position', related='change_position_id.position_id', store=True)
    motif_new_id = fields.Many2one('hr.assignment.type.motif', string='Nouveau Statut', related='change_position_id.motif_id', store=True)
    date_effet = fields.Date('Date d\'effet', related='change_position_id.date_effet', store=True)
    state = fields.Selection(
            [('draft', 'Brouillon'), ('validate', 'Valider')],
            string='State', compute='_get_state')

class HrNomination(models.Model):
    _name = 'hr.nomination'
    _inherit = ['mail.thread']
    _order = "id desc"

    @api.one
    @api.depends('line_ids')
    def _get_employees(self):
        if self.line_ids:
            list = []
            for line in self.line_ids:
                list.append(line.employee_id.id)
            employees = self.env['hr.employee'].search([('id', 'in', list)]).ids
            if employees:
                self.employee_check_ids = employees

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default=lambda self: self.env['ir.sequence'].next_by_code('nomination.default.seq'))
    reference = fields.Char('Numéro Arrêté', required=True)
    date = fields.Date('Date Arrêté', required=True)
    remarque = fields.Char('Remarque')
    line_ids = fields.One2many('hr.nomination.line', 'nomination_id', string='Nomination Line')
    employee_check_ids = fields.One2many('hr.employee', compute='_get_employees')
    state = fields.Selection(
            [('draft', 'Brouillon'), ('validate', 'Valider')],
            string='State', default='draft', track_visibility='onchange')
    notes = fields.Text(string='Notes')

    @api.multi
    def act_validate(self):
        if not self.line_ids:
            raise ValidationError("Il faut séléctionner au moin un employé!")
        else:
            for line in self.line_ids:
                if line.fonction_new_id == False or line.place_job_new_id == False or line.date_effet == False:
                    raise ValidationError("Il faut remplir tout les informations de nomination pour chaque employé avant la validation!")
                else:
                    line.employee_id.fonction_id = line.fonction_new_id.id
                    line.employee_id.place_job_id = line.place_job_new_id.id
            self.state = 'validate'

class HrNominationLine(models.Model):
    _name = 'hr.nomination.line'
    _order = "id desc"

    @api.one
    @api.depends('nomination_id.state')
    def _get_state(self):
        if self.nomination_id.state:
            self.state = self.nomination_id.state

    @api.one
    @api.depends('employee_id')
    def _get_info_employee(self):
        if self.employee_id:
            self.fonction_id = self.employee_id.fonction_id.id
            self.place_job_id = self.employee_id.place_job_id.id
            self.corps_id = self.employee_id.corps_id.id

    employee_id = fields.Many2one('hr.employee', string='Employé')
    identification_id = fields.Char('Matricule', related='employee_id.identification_id')
    nni = fields.Char('NNI', related='employee_id.nni')
    name = fields.Char('Nom et prénom', related='employee_id.name')
    fonction_id = fields.Many2one('hr.function', string='Emploi actuel', compute='_get_info_employee', store=True)
    place_job_id = fields.Many2one('hr.place.job', string='Lieu de travail actuel', compute='_get_info_employee', store=True)
    corps_id = fields.Many2one('hr.employee.corps', string='Corps', compute='_get_info_employee', store=True)
    nomination_id = fields.Many2one('hr.nomination', string='Nomination')
    fonction_new_id = fields.Many2one('hr.function', string='Nouveau Poste')
    place_job_new_id = fields.Many2one('hr.place.job', string='Nouveau Lieu de travail')
    date_effet = fields.Date('Date d\'effet',)
    state = fields.Selection(
            [('draft', 'Brouillon'), ('validate', 'Valider')],
            string='State', compute='_get_state')

class HrDepartment(models.Model):
    _name = 'hr.departement'

    name = fields.Char('Département', required=True)

class HrPlaceJob(models.Model):
    _name = 'hr.place.job'

    name = fields.Char('Lieu de travail', required=True)
    type_id = fields.Many2one('hr.type.function', 'Type fonction')
    dep_id = fields.Many2one('hr.departement', 'Département')

class EducaEtablissement(models.Model):
    _inherit = 'educa.establishment'

    @api.one
    @api.depends('assignment_etab_ids', 'assignment_lieu_ids')
    def _get_affectation(self):
        assignment_line = self.env['hr.assignment.line'].search(['|', ('lieu', '=', self.id), ('establishment_new_id', '=', self.id)])
        if assignment_line:
            self.assignment_line_ids = assignment_line

    assignment_line_ids = fields.One2many('hr.assignment.line', compute='_get_affectation', string='affectation')
    assignment_etab_ids = fields.One2many('hr.assignment.line', 'establishment_new_id', string='Affectation etablissement')
    assignment_lieu_ids = fields.One2many('hr.assignment.line', 'lieu', string='Affectation lieu travail')

