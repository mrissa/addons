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
    _name = 'import.employee.line'
    _description = 'Import Employee Line'

    data_file = fields.Binary(string='Employee File', required=True,)
    filename = fields.Char()

    @api.multi
    def import_file(self):
        self.ensure_one()
        book = xlrd.open_workbook(file_contents=base64.b64decode(self.data_file))
        sheet = book.sheet_by_index(0)
        
        data_list=[]
        _logger.info("------data range(sheet.nrows)------%s",range(sheet.nrows))
        _logger.info("------data  sheet.nrows------%s",sheet.nrows)
        _logger.info("------data sheet.row------%s",sheet.row )
        for row in range(1,sheet.nrows):
            cells = sheet.row_slice(rowx=row,start_colx=0,end_colx=20)
            for cell in cells:
                _logger.info("------cell.value------%s",cell.value )
            data_list += [cells]

        active_id = self._context.get('active_id', False)
        active_model = self._context.get('active_model', False)

        if active_model == 'hr.recruitment.pv':
            RecLine = self.env['hr.employee']
            for line in data_list:
                displine = self.env['skill.discipline'].search([('code', '=', str(line[4].value))])
                _logger.info("------data_birthday-----%s", line[9].value)
                _logger.info("------data_list------%s", displine)
                new_rec=RecLine.create({
                            'recruitment_pv_id': active_id,
                            'note_graduation': line[0].value,
                            'number_training_school': line[1].value,
                            'name': line[2].value,
                            'place_of_birth': line[3].value,
                            'discipline_ids': [(4,displine.id)],
                            'nni': str(line[7].value),
                            #'birthday': line[9].value,
                        })
                traduction = self.env['ir.translation']
                _logger.info("------new_rec------%s", new_rec)
                _logger.info("------Traduction------%s", traduction)
                _logger.info("------line[10].value------%s", line[10].value)
                traduction.create({
                    'res_id': new_rec.id,
                    'name': 'hr.employee,name',
                    'lang': 'ar_SY',
                    'type': 'model',
                    'src': line[2].value,
                    'value': line[10].value,
                    'state': 'translated',
                })


class LineChoiceImport(models.TransientModel):
    _name = 'import.choice.employee.line'
    _description = 'Import Employee choice Line'

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

        if active_model == 'hr.recruitment.pv':
            for line in data_list:
                assignment_choice1 = self.env['nmcl.state'].search([('name', '=', line[1].value)])
                assignment_choice2 = self.env['nmcl.state'].search([('name', '=', line[2].value)])
                assignment_choice3 = self.env['nmcl.state'].search([('name', '=', line[3].value)])
                assignment_choice4 = self.env['nmcl.state'].search([('name', '=', line[4].value)])
                assignment_choice5 = self.env['nmcl.state'].search([('name', '=', line[5].value)])
                employee=self.env['hr.employee'].search([('nni', '=', str(line[0].value))])

                employee.update({
                    'assignment_choice1':assignment_choice1.id,
                    'assignment_choice2': assignment_choice2.id,
                    'assignment_choice3': assignment_choice3.id,
                    'assignment_choice4': assignment_choice4.id,
                    'assignment_choice5': assignment_choice5.id,
                })

class ChoiceEmployee(models.TransientModel):
    _name = 'choice.employee'
    _description = 'Choice Employee'

    @api.one
    def _get_employees(self):
        employees = self._context.get('employee_check_ids', False)
        if employees:
            self.employee_check_ids = self._context.get('employee_check_ids', False)

    employee_check_ids = fields.One2many('hr.employee', string='Employee', compute='_get_employees')
    employee_ids = fields.Many2many('hr.employee', 'employee_pv_choice_rel', 'employee_id',
                                    'choice_pv_employee_id', string='Employee',
                                    domain="[('id','not in', employee_check_ids), ('recruitment_type','=','employee')]")
    @api.multi
    def choice_employee(self):
        self.ensure_one()
        active_id = self._context.get('active_id', False)
        for val in self.employee_ids:
            val.recruitment_pv_id = active_id

class ChoicePv(models.TransientModel):
    _name = 'choice.pv'
    _description = 'Choice PV'

    @api.one
    def _get_info(self):
        pv = self._context.get('pv_check_ids', False)
        corps_id = self._context.get('corps_id', False)
        date = self._context.get('date', False)
        new_graduates = self._context.get('new_graduates', False)
        pv_treat_ids = self._context.get('pv_treat_ids', False)
        recruitment_pv_type = self._context.get('recruitment_pv_type', False)
        if pv_treat_ids:
            self.pv_treat_ids = self._context.get('pv_treat_ids', False)
        if pv:
            self.pv_check_ids = self._context.get('pv_check_ids', False)
        if corps_id:
            self.corps_id = self._context.get('corps_id', False)
        if date:
            self.date = self._context.get('date', False)
        if new_graduates:
            self.new_graduates = self._context.get('new_graduates', False)
        if recruitment_pv_type:
            self.recruitment_pv_type = self._context.get('recruitment_pv_type', False)

    date = fields.Date('Date', compute='_get_info')
    pv_check_ids = fields.One2many('hr.recruitment.pv', string='PV/NS', compute='_get_info')
    pv_treat_ids = fields.One2many('hr.recruitment.pv', string='PV/NS', compute='_get_info')
    corps_id = fields.Many2one('hr.employee.corps', string='Corps', compute='_get_info')
    new_graduates = fields.Boolean(string='Nouveaux diplômés', compute='_get_info')
    recruitment_pv_type = fields.Selection([('direct', 'Direct'), ('training_school', 'Training school'), ('titularisation', 'Titularisation')], string='Type Recrutement', compute='_get_info')
    pv_ids = fields.Many2many('hr.recruitment.pv', 'pv_choice_rel', 'pv_id',
                                    'choice_pv_id', string='PV',
                                    domain="[('id','not in', pv_check_ids),('corps_id','=',corps_id),('new_graduates','=',new_graduates), ('state','=', 'validate'), ('recruitment_pv_type','=', recruitment_pv_type), ('date','<=', date)]")
    @api.multi
    def choice_pv(self):
        self.ensure_one()
        active_id = self._context.get('active_id', False)
        active_model = self._context.get('active_model', False)
        lines = []
        for val in self.pv_ids:
            line_item = {
                'pv_id': val.id,
            }
            lines += [line_item]
        if active_model == 'hr.recruitment.exit':
            rec = self.env['hr.recruitment.exit'].search([('id', '=', active_id)])
            rec.update({'line_ids': lines})
        if active_model == 'hr.recruitment.entry':
            rec = self.env['hr.recruitment.entry'].search([('id', '=', active_id)])
            rec.update({'line_ids': lines})

class LinePNPImport(models.TransientModel):
    _name = 'import.employee.pnp.line'
    _description = 'Import Employee Line'

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
            cells = sheet.row_slice(rowx=row, start_colx=0, end_colx=9)
            for cell in cells:
                _logger.info("------cell.value------%s", cell.value)
            data_list += [cells]

        active_id = self._context.get('active_id', False)
        active_model = self._context.get('active_model', False)
        gender = ''
        if active_model == 'hr.recruitment.on.demand':
            RecLine = self.env['hr.employee']
            for line in data_list:
                _logger.info("------data_list-line-----%s", line[2].value)
                if line[2].value == 'H':
                    gender = 'male'
                if line[2].value == 'F':
                    gender = 'female'
                RecLine.create({
                    'recruitment_demande_id': active_id,
                    'identification_id': str(line[0].value),
                    'name': line[1].value,
                    'gender': gender,
                    # 'birthday': line[3].value,
                    'place_of_birth': line[4].value,
                    'nni': str(line[5].value),
                })
