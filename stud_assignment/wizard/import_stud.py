# -*- coding: utf-8 -*-
import base64
from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class StudentAssignment(models.TransientModel):
    _name = 'student.assignment'
    _description = 'Choice registration'

    registration_ids = fields.Many2many('stud.inscription', 'stud_assignment_choice_rel', 'inscription_id',
                                    'choice_stud_id', string='Registrations', domain="[('state','=','draft')]")

    @api.multi
    def choice_registration(self):
        self.ensure_one()
        active_id = self._context.get('active_id', False)
        rec = self.env['stud.assignment'].search([('id', '=', active_id)])
        lines = []
        for val in self.registration_ids:
            line_item = {
                'assignment_id': rec.id,
            }
            lines += [line_item]
        rec.update({'line_ids': lines})