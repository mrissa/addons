# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from io import BytesIO
import os
import sys
from odoo import models
from xlrd import open_workbook # http://pypi.python.org/pypi/xlrd
from xlutils.styles import Styles
import xlutils.copy
import logging
_logger = logging.getLogger(__name__)

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
    # END HACK
def text_cleanup(line):
    for char in line:
        if char in " ?.!/;:":
            line = line.replace(char,'')
    return line
def get_sheet_by_name(book, name):
    """Get a sheet by name from xlwt.Workbook, a strangely missing method.
    Returns None if no sheet with the given name is present.
    """
    # Note, we have to use exceptions for flow control because the
    # xlwt API is broken and gives us no other choice.
    try:
        for idx in itertools.count():
            sheet = book.get_sheet(idx)
            if sheet.name == name:
                return sheet
    except IndexError:
        return None
#################
class ReportXlsxAbstract(models.AbstractModel):
    _name = 'report.report_xlsx.abstract'
    
    def create_xlsx_report(self, docids, data):
        objs = self.env[self.env.context.get('active_model')].browse(docids)
        #############################################
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        if sys.platform == 'linux':
            xlfile=str(path)+"/template/temp3.xls"
            xlfiletemp2=str(path)+"/template/temp3.xls"
            xlfiles=str(path)+"/template/templateZ.xls"
        elif sys.platform in ['windows', 'win32']:
            xlfile=str(path)+"\\template\\temp3.xls"
            xlfiletemp2=str(path)+"\\template\\temp3.xls"
            xlfiles=str(path)+"\\template\\templateZ.xls"
        _logger.info('________________ xlfile _________________ %s', xlfile)
        _logger.info('________________ OS _________________ %s', sys.platform)

        sheets = []
        res={}
        resobjs=[]
        inBook =  open_workbook(xlfile, formatting_info=True)
        temp2book =  open_workbook(xlfiletemp2, formatting_info=True)
        modell=self.env.context.get('active_model')
        
        if objs.niveau=='central':
            drens= self.env['year.scholarly'].search([('parent_id', '=', objs.id)])
            etablissements=objs.etablissement_ids
            if len(etablissements) >=1:
                outBook = xlutils.copy.copy(inBook)
                sheet=inBook.sheet_by_index(1)
                sheet2=inBook.sheet_by_index(2)
                wilayasheet =outBook.get_sheet(sheet2.name)
                wilayasheet.set_name('Wilaya')
                sheets.append(wilayasheet)
                for dren in  drens:
                    outBookk = xlutils.copy.copy(inBook)
                    wfsheet =outBookk.get_sheet(sheet.name)
                    wfsheet.set_name(str(text_cleanup(dren.name)))
                    sheets.append(wfsheet)
                
                
            for obj in etablissements:
                numberOfSheets=inBook.nsheets
                outBook = xlutils.copy.copy(inBook)
                sheet=inBook.sheet_by_index(0)
                wssheet =outBook.get_sheet(sheet.name)
                wssheet.set_name(str(text_cleanup(obj.name)))
                sheets.append(wssheet)
        
        if objs.niveau=='dren':
           
            etablissements=objs.etablissement_ids
            if len(etablissements) >=1:
                outBook = xlutils.copy.copy(inBook)
                sheet=inBook.sheet_by_index(1)
                sheet2=inBook.sheet_by_index(2)
                wilayasheet =outBook.get_sheet(sheet2.name)
                wilayasheet.set_name('Wilaya')
                sheets.append(wilayasheet)
                
                wfsheet =outBook.get_sheet(sheet.name)
                wfsheet.set_name(str(text_cleanup(objs.name)))
                sheets.append(wfsheet)
                
                
            for obj in etablissements:
                numberOfSheets=inBook.nsheets
                outBook = xlutils.copy.copy(inBook)
                sheet=inBook.sheet_by_index(0)
                wssheet =outBook.get_sheet(sheet.name)
                wssheet.set_name(str(text_cleanup(obj.name)))
                sheets.append(wssheet)
    #            
                read_sheet = open_workbook(xlfile, formatting_info=True, on_demand=True).sheet_by_index(0)
                read_fsheet = open_workbook(xlfile, formatting_info=True, on_demand=True).sheet_by_index(1) 
        
        if objs.niveau=='etablissement':
            if len(objs) >=2:
                outBook = xlutils.copy.copy(inBook)
                sheet=inBook.sheet_by_index(1)
                wfsheet =outBook.get_sheet(sheet.name)
                wfsheet.set_name('DREN')
    #             worksheet = outBook.add_sheet(str(text_cleanup(obj.establishment_id.name)), cell_overwrite_ok=False)
                sheets.append(wfsheet)
                
            for obj in objs:
                numberOfSheets=inBook.nsheets
                outBook = xlutils.copy.copy(inBook)
                sheet=inBook.sheet_by_index(0)
                wssheet =outBook.get_sheet(sheet.name)
                wssheet.set_name(str(text_cleanup(obj.etablissement_id.name)))
                sheets.append(wssheet)
    #            
                read_sheet = open_workbook(xlfile, formatting_info=True, on_demand=True).sheet_by_index(0)
                read_fsheet = open_workbook(xlfile, formatting_info=True, on_demand=True).sheet_by_index(1) # Meant only to read some cases, requires xlrd.copy
              
        
        outBook._Workbook__worksheets = sheets
        outBook.save(xlfiles)
        tempBook =  open_workbook(xlfiles, formatting_info=True)
        oBook = xlutils.copy.copy(tempBook)
        
        if objs.niveau=='etablissement':
            for obj in objs:
                sheet=tempBook.sheet_by_name(str(text_cleanup(obj.etablissement_id.name)))
                ssheet =oBook.get_sheet(sheet.name)
                res = self.generate_xlsx_sheet(ssheet,read_sheet, data, obj)
                resobjs.append(res)
            if len(objs) >=2:
                fheet=tempBook.sheet_by_name('DREN')
                fsheet =oBook.get_sheet(fheet.name)
                self.generate_dren_sheet(fsheet,read_fsheet,resobjs, data, objs)
                
        if objs.niveau=='dren':
             
            etablissements= self.env['year.scholarly'].search([('parent_id', '=', objs.id)])
            _logger.info('________________ etablissements _________________ %s', etablissements)
            if len(etablissements) >=1:
                for obj in etablissements:
                    sheet=tempBook.sheet_by_name(str(text_cleanup(obj.etablissement_id.name)))
                    ssheet =oBook.get_sheet(sheet.name)
                    res = self.generate_xlsx_sheet(ssheet,read_sheet, data, obj)
                    resobjs.append(res)
                if len(etablissements) >=1:
                    fheet=tempBook.sheet_by_name(str(text_cleanup(objs.name)))
                    fsheet =oBook.get_sheet(fheet.name)
                    self.generate_dren_sheet(fsheet,read_fsheet,resobjs, data, etablissements)
                    
                    wilayaheet=tempBook.sheet_by_name('Wilaya')
                    wilayasheet =oBook.get_sheet(wilayaheet.name)
                    self.generate_wilaya_sheet(wilayasheet,read_fsheet,objs, data, etablissements)
                    
        file_data = BytesIO()
        oBook.save(file_data)
        
        file_data.seek(0)
        return file_data.read(), 'xlsx'

    def get_workbook_options(self):
        return {}

    def generate_xlsx_report(self, workbook, data, objs):
        raise NotImplementedError()
    def generate_xlsx_sheet(self, wssheet, data, obj):
        raise NotImplementedError()