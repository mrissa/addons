# -*- coding: utf-8 -*-
import base64
from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class StudentAssignment(models.TransientModel):
    _name = 'insc.affectation'
    _description = 'Choice student Inscription'

    inscription_ids = fields.Many2many('stud.inscription', 'inscription_assignment_choice_rel', 'inscription_id',
                                    'choice_inscription_id', string='inscriptions', )

    @api.multi
    def choice_insc(self):
        self.ensure_one()
        active_id = self._context.get('active_id', False)
        rec = self.env['stud.affectation'].search([('id', '=', active_id)])
        lines = []
        for val in self.inscription_ids:
            line_item = {
                'student_id':val.student_id.id,
                'scholarly_id':val.scholarly_id.id,
                'sec_pedago_id':val.sec_pedago_id.id,
                'state':'inscrit'
            }
            lines += [line_item]
        rec.update({'line_ids': lines})
