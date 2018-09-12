# -*- coding: utf-8 -*-
import base64
from odoo import api, fields, models, _
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

class EmployeeAssignment(models.TransientModel):
    _name = 'employee.assignment'
    _description = 'Choice Employee'

    @api.one
    def _get_employees(self):
        employees = self._context.get('employee_check_ids', False)
        if employees:
            self.employee_check_ids = self._context.get('employee_check_ids', False)

    employee_check_ids = fields.One2many('hr.employee', string='Employee', compute='_get_employees')
    employee_ids = fields.Many2many('hr.employee', 'employee_assignment_choice_rel', 'employee_id',
                                    'choice_employee_id', string='Employee', domain="[('id','not in', employee_check_ids)]")

    @api.multi
    def choice_employee(self):
        self.ensure_one()
        active_id = self._context.get('active_id', False)
        active_model = self._context.get('active_model', False)
        lines = []
        for val in self.employee_ids:
            line_item = {
                'employee_id': val.id,
            }
            lines += [line_item]
        if active_model == 'hr.assignment':
            rec = self.env['hr.assignment'].search([('id', '=', active_id)])
        rec.update({'line_ids': lines})


class EmployeeAffectation(models.TransientModel):
    _name = 'employee.xcel.affectation'
    _description = 'Affectation Employee'

    data_file = fields.Binary(string='Employee File', required=True, )
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
        for row in range(1, sheet.nrows):
            cells = sheet.row_slice(rowx=row, start_colx=0, end_colx=6)
            for cell in cells:
                _logger.info("------cell.value------%s", cell.value)
            data_list += [cells]

        active_id = self._context.get('active_id', False)
        active_model = self._context.get('active_model', False)

        if active_model == 'hr.assignment':
            for line in data_list:
                employee = self.env['hr.employee'].search([('nni', '=', str(line[0].value))])
                assig_line = self.env['hr.assignment.line'].search([('employee_id', '=', employee.id), ('assignment_id', '=', active_id)])
                fonction = self.env['hr.function'].search([('name', '=', line[1].value)], limit=1)
                etablissement = self.env['educa.establishment'].search([('name', '=', line[2].value)], limit=1)
                if assig_line.type_affect != 'administratif':
                    assig_line.update({
                        'fonction_new_id': fonction.id,
                        'establishment_new_id': etablissement.id,
                        'remarque': line[3].value,
                    })
                else:
                    lieu = self.env['educa.establishment'].search([('name', '=', line[3].value)])
                    assig_line.update({
                        'fonction_new_id': fonction.id,
                        'establishment_new_id': etablissement.id,
                        'lieu': lieu.id,
                        'remarque': line[4].value,
                    })
        if active_model == 'hr.assignment.regional':
            for line in data_list:
                employee = self.env['hr.employee'].search([('nni', '=', str(line[0].value))])
                assig_line = self.env['hr.assignment.line'].search([('employee_id', '=', employee.id), ('assignment_reg_id', '=', active_id)])
                lieu = self.env['educa.establishment'].search([('name', '=', line[1].value)], limit=1)
                assig_line.update({
                    'lieu': lieu.id,
                })