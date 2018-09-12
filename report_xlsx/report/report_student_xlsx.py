# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from xlrd import open_workbook
from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)
from os.path import expanduser
home = expanduser("~/")
def _getOutCell(outSheet, colIndex, rowIndex):
    """ HACK: Extract the internal xlwt cell representation. """
    row = outSheet._Worksheet__rows.get(rowIndex)
    if not row: return None

    cell = row._Row__cells.get(colIndex)
    return cell

def setOutCell(outSheet, col, row, value):
    """ Change cell value without changing formatting. """
    # HACK to retain cell style.
    previousCell = _getOutCell(outSheet, col, row)
    # END HACK, PART I

    outSheet.write(row, col, value)

    # HACK, PART II
    if previousCell:
        newCell = _getOutCell(outSheet, col, row)
        if newCell:
            newCell.xf_idx = previousCell.xf_idx
            # _logger.info('___________ newCell.xf_idx__________: %s',newCell.xf_idx)
    # END HACK

def word_border_range(sheet, nrow, ncol, nrows, ncols):
    '''See word_border(sheet, token) description.'''
    # Rows Selection
    nrow_index = nrow
    while nrow_index < nrows - 1 and sheet.cell(nrow_index, ncol).value != '':
        nrow_index += 1
        if sheet.cell(nrow_index, ncol).value == '' :
            nrow_final = nrow_index - 1
        elif nrow_index == nrows - 1:
            nrow_final = nrow_index - 1
    # print('this is down row : ', nrow_index)

    # Cols Selection
    ncol_index = ncol
    while ncol_index < ncols - 1 and sheet.cell(nrow, ncol_index).value != '':
        ncol_index += 1
        if sheet.cell(nrow, ncol_index).value == '':
            ncol_final = ncol_index - 1
        elif ncol_index == ncols - 1:
            ncol_final = ncol_index - 1
    # print('this is right row : ', ncol_index)
    return(range(nrow, nrow_final), range(ncol, ncol_final+1))

def word_border(sheet, token):
    '''Returns ranges of rows & cols of the related indexed array (tuple).'''
    n_pass = 0
    word_border = None
    token = str(token)

    nrows = sheet.nrows
    ncols = sheet.ncols
    for nrow in range(nrows):
        for ncol in range(ncols):
            if token in str(sheet.cell(nrow, ncol).value):
                n_pass += 1
                try:
                    n_pass < 2
                except:
                    print("Error word index occurence")
                else:
                    word_border_range_result = word_border_range(sheet, nrow+1, ncol, nrows, ncols)
                    return(word_border_range_result)

def student_female_count(student_ids):
    female_count = 0
    for student in student_ids:
        if student.gender_id.name == 'Female':
            female_count+=1
    return(female_count)

def insert_cycle_row(wssheet, cycle, nrow, ncols):
    setOutCell(wssheet, ncols[0], nrow, cycle.name)
    setOutCell(wssheet, ncols[1], nrow, '1')
    setOutCell(wssheet, ncols[2], nrow, len(cycle.student_ids))
    setOutCell(wssheet, ncols[3], nrow, student_female_count(cycle.student_ids))
    setOutCell(wssheet, ncols[4], nrow, 'X')
    setOutCell(wssheet, ncols[5], nrow, 'X')
    return True

def purge_cycle_row(wssheet, nrow, ncols):
    for ncol in range(ncols[0], ncols[-1]+1):
        setOutCell(wssheet, ncol, nrow, '')

class StudentXlsx(models.AbstractModel):
    _name = 'report.report_xlsx.student_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    def generate_xlsx_report(self, workbook, data, students):
        for obj in students:
            name_worksheet= 'Report_'+str(obj.name)
            sheet = workbook.add_worksheet(name_worksheet)
            bold = workbook.add_format({'bold': True})
            sheet.write(0, 0, obj.name, bold)
            sheet.write(0, 0, obj.establishment_id.name, bold)

    def generate_xlsx_sheet(self, wssheet, data, students):
        for obj in students:
            cycles = students.pool.__getitem__('res.student.cycle')
            setOutCell(wssheet, 5, 6, 'Mrissa')
            setOutCell(wssheet,8, 7, obj.name)
            setOutCell(wssheet,9, 8, obj.establishment_id.name)

    def cycle_index_search(self, read_sheet, token):
        '''Returns the range of rows & cols of indexed xls array.'''
        (rows, cols) = word_border(read_sheet, token)
        return(rows, cols)

    def generate_cycle_sheet(self, wssheet, read_sheet, students, token):
        '''Generate cycle related row'''
        _logger.info('*_________ generate_cycle_sheet : students __________ %s', students)
        nrows, ncols = self.cycle_index_search(read_sheet, token)
        for obj in students:
            cycles = obj.cycle_ids # Cycles of student
            ################# Cell Operation #################
            cycle_of_sheet_array = [] # To load existant Cycles on wssheet, meant for cycles that are present in the template
            nrow = nrows[0] # First row of the cycle edit
            check_cycle_exist = False
            cycle_index = 0 # Used to generate different rows with cycle values
            if len(nrows) < len(cycles):
                _logger.info('You have too many cycles, we cannot display all of them')

            for nrow in nrows:
                if cycle_index < len(cycles):
                    insert_cycle_row(wssheet, cycles[cycle_index], nrow, ncols)
                    cycle_index += 1
                else:
                    purge_cycle_row(wssheet, nrow, ncols)
        return True
