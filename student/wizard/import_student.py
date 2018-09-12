# -*- coding: utf-8 -*-
import base64
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import itertools
from datetime import datetime
from odoo.osv import osv
import logging
_logger = logging.getLogger(__name__)

try:
    import xlrd
    try:
        from xlrd import xlsx
    except ImportError:
        xlsx = None
except ImportError:
    xlrd = xlsx = None

class LineImport(models.TransientModel):
    _name = 'import.student.line'
    _description = 'Import Student Line'

    data_file = fields.Binary(string='Student File', required=True,)
    filename = fields.Char()

    @api.multi
    def import_file(self):
        self.ensure_one()
        book = xlrd.open_workbook(file_contents=base64.b64decode(self.data_file))
        sheet = book.sheet_by_index(0)

        data_list = []
        _logger.info("------data range(sheet.nrows)------%s", range(sheet.nrows))
        _logger.info("------data  sheet.nrows------%s", sheet.nrows)
        _logger.info("------data sheet.row------%s", sheet.row)
        for row in range(0, sheet.nrows):
            cells = sheet.row_slice(rowx=row, start_colx=0, end_colx=9)
            for cell in cells:
                _logger.info("------cell.value------%s", cell.value)
            data_list += [cells]

        active_id = self._context.get('active_id', False)
        active_model = self._context.get('active_model', False)

        if active_model == 'stud.student.pv':
            RecLine = self.env['stud.student']
            for line in data_list:
                _logger.info("------data_list-line-----%s", line[0].value)
                _logger.info("------data_list------%s", line)

                for line in data_list:
                    if line[2].value == 'G':
                        gender = 'male'
                    if line[2].value == 'F':
                        gender = 'female'
                    RecLine.create({
                        'pv_id': active_id,
                        'identification_id': line[0].value,
                        'nni': line[1].value,
                        'name': line[3].value,
                        'gender': gender,
                        'place_birth': line[4].value,
                    })
