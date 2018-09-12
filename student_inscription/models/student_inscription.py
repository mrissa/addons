# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)

class StudInscription(models.Model):
    _name = "stud.inscription"
    _description = "Student Inscription"
    _inherit = ['mail.thread']
    _order = "scholarly_id asc"

    @api.one
    @api.depends('student_id.nni','scholarly_id.name')
    def _get_name(self):
        if self.student_id and self.scholarly_id:
            self.name = str(self.student_id.nni)+'/'+str(self.scholarly_id.name)

    name = fields.Char(string="Code inscription", compute='_get_name', readonly=True)
    student_id = fields.Many2one('stud.student', "Student", required=True)
    note = fields.Float(string="Note")
    notes = fields.Text(string="Notes", translate=True)
    scholarly_id = fields.Many2one('year.scholarly', string='Scolarity Year', )
    establishment_id = fields.Many2one('educa.establishment', string='Establishment')
    etabli_origine = fields.Many2one('educa.establishment', string='établissement d\'origine')
    date_inscp = fields.Date(string="Date inscription")
    structure = fields.Char(string="Structure Globale")
    type = fields.Selection(
        [('first_inscription_competition', 'First registration after competition'),
         ('first_request_inscription', 'First Application Registration'), ('transfert', 'Transfer'),
         ('reinscription', 'Reinstatement')], 'Type',
        readonly=True)
    state = fields.Selection(
        [('draft', 'Brouillon'), ('inscrit', 'Inscrit'), ('transfert', 'En Transfert'), ('abandonner', 'Abandonner'),
         ('exclu', 'Exclu'), ('admis', 'Admis'), ('redoublant', 'Redoublant')], 'State',
        readonly=True, default='draft')
    year_line_id = fields.Many2one('year.scholarly.line', string='Structure d\'inscription')

    _sql_constraints = [
        ('inscription_uniq', 'unique(student_id,scholarly_id,establishment_id)',
         'The Student must be unique registration per scholarly year per establishment.'),
    ]

    @api.multi
    def act_transfert(self):
        self.student_id.state_inscription = 'transferer'
        self.state = 'transferer'

    @api.multi
    def act_exclu(self):
        self.student_id.state='inactif'
        self.student_id.state_inscription = 'exclu'
        self.state = 'exclu'

    @api.multi
    def act_abandonner(self):
        self.student_id.state = 'inactif'
        self.student_id.state_inscription = 'abandonner'
        self.state = 'abandonner'

    @api.multi
    def act_inscrit(self):
        self.student_id.state_inscription = 'inscrit'
        self.state = 'inscrit'

    @api.multi
    def act_admis(self):
        if self.note == 0.0:
            raise ValidationError(_("Il faut remplir le champ Note"))
        else:
            self.student_id.state = 'not_affect'
            self.student_id.state_inscription= 'admis'
            self.state = 'admis'

    @api.multi
    def act_redoublant(self):
        if self.note == 0.0:
            raise ValidationError(_("Il faut remplir le champ Note"))
        else:
            self.student_id.state = 'not_affect'
            self.state = 'redoublant'

class StudStudent(models.Model):
    _inherit = 'stud.student'

    @api.multi
    def _inscription_count(self):
        for each in self:
            inscription_ids = self.env['stud.inscription'].search([('student_id', '=', each.id)])
            each.inscriptions_count = len(inscription_ids)

    @api.multi
    def inscription_view(self):
        self.ensure_one()
        domain = [
            ('student_id', '=', self.id)]
        return {
            'name': _('Inscripion Scolaire'),
            'domain': domain,
            'res_model': 'stud.inscription',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                           Click to Create for New Inscription
                        </p>'''),
            'limit': 80,
        }

    inscription_ids = fields.One2many('stud.inscription', 'student_id', 'Stud Inscription')
    inscriptions_count = fields.Integer(compute='_inscription_count', string='Stud Inscription')
