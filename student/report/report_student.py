 # -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


import time

from odoo import api, fields, models


class ReportStudent(models.AbstractModel):
    _name = 'report.student.report_student'

    @api.model
    def get_report_values(self, docids, data=None):
        docs = self.env['stud.student'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'stud.student',
            'docs': docs,
            'time': time,
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

