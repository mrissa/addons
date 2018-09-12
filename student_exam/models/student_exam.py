# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo import tools, _

class StudExam(models.Model):
    _name = "stud.exam"
    _description = "Exams"
    _inherit = ['mail.thread']

    name = fields.Char(string="Code", required=True)
    establishment_id = fields.Many2one('educa.establishment', string='Etablissement', required=True)
    section_id = fields.Many2one('educa.pedagogical.section', string='Section Pedagogique',
                                        domain="[('establishment_id', '=', establishment_id)]", required=True)
    line_ids = fields.One2many('exam.line', 'exam_id', string='Resultat')
    note = fields.Char(string="Description")
    state = fields.Selection(
        [('draft', 'Brouillon'), ('validate', 'Validate')], 'State',
        readonly=True, default='draft')

    @api.multi
    def act_validate(self):
        self.state = 'validate'

class ExamLine(models.Model):
    _name = "exam.line"
    _description = "Resultat Examens"

    exam_id = fields.Many2one('stud.exam', string='Examen')
    inscription_id = fields.Many2one('stud.inscription', string='Inscription',
                                     required=True)
    student_id = fields.Many2one('stud.student', string='Eleve', related='inscription_id.student_id')
    note = fields.Float('Note Exam')
    appreciation = fields.Selection([
        ('felicitation', 'Felicitation'),
        ('encouragement', 'Encouragement'),
        ('tableau_honneur', 'Tableau Honneur'),
        ('encouragement', 'Encouragement'),
        ('passable', 'Passable'),
        ('insuffisant', 'Insuffisant'),
        ('renvoi', 'Renvoi')
    ],)

class StudStudent(models.Model):
    _inherit = 'stud.student'

    @api.multi
    def _examen_count(self):
        for each in self:
            exam_ids = self.env['exam.line'].search([('student_id', '=', each.id)])
            each.exam_count = len(exam_ids)

    @api.multi
    def examen_view(self):
        self.ensure_one()
        domain = [
            ('student_id', '=', self.id)]
        return {
            'name': _('Examens'),
            'domain': domain,
            'res_model': 'exam.line',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                                       Click to Create Exam
                                    </p>'''),
            'limit': 80,
        }

    exam_count = fields.Integer(compute='_examen_count', string='Exams')