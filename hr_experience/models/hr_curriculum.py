# -*- coding: utf-8 -*-
# Copyright 2013 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

class HrCurriculum(models.Model):
    _name = 'hr.curriculum'
    _description = "Employee's Curriculum"

    @api.one
    def get_num(self):
        experience_ids = self.search([('employee_id', '=', self.id)])
        self.experience_count = len(experience_ids) + 1

    name = fields.Char('Name', required=True, translate=True)
    employee_id = fields.Many2one('hr.employee',
                                  string='Employee',
                                  required=True)
    start_date = fields.Date('Start date')
    end_date = fields.Date('End date')
    description = fields.Text('Description', translate=True)
    partner_id = fields.Many2one('res.partner',
                                 'Partner',
                                 help="Employer, School, University, "
                                      "Certification Authority")
    location = fields.Char('Location', help="Location", translate=True)
    expire = fields.Boolean('Expire', help="Expire", default=True)
    type_occupation = fields.Selection([('ouvrier', 'Ouvrier'),
                                        ('contremaitre', 'Contremaitre'),
                                        ('ingenieur', 'Ingenieur'),
                                        ('autre', 'Autre')],
                                       'Type Occupation')
    type_emploi = fields.Selection([('mi_temps', 'Mi-temps'),
                                    ('plein_temps', 'Plein temps')],
                                   'Type Emploi')
    experience_count = fields.Integer('Numero', compute='get_num')
