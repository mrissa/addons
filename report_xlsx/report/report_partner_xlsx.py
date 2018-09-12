# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import xlwt 
from odoo import models
import logging
import datetime
_logger = logging.getLogger(__name__)

def text_cleanup(line):
    for char in line:
        if char in " ?.!/;:":
            line = line.replace(char,'')
    return line
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
 
 

class establishmentXlsx(models.AbstractModel):
    _name = 'report.report_xlsx.establishment_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def cycle_index_search(self, read_sheet, token):
        '''Returns the range of rows & cols of indexed xls array.'''
        (rows, cols) = word_border(read_sheet, token)
        return(rows, cols)
   
    def insert_cycle_row(self,wssheet, cycle, nrow, ncols):
        
        setOutCell(wssheet, ncols[0], nrow, cycle.name)
        setOutCell(wssheet, ncols[1], nrow, cycle.section_number)
        setOutCell(wssheet, ncols[2], nrow, cycle.inscriptions_count)
        setOutCell(wssheet, ncols[3], nrow, cycle.inscriptions_female)
        setOutCell(wssheet, ncols[4], nrow, cycle.redoubles_count)
        setOutCell(wssheet, ncols[5], nrow, cycle.redouble_fille_count)
        
#         setOutCell(wssheet, ncols[6], nrow, cycle.generate_displine())
        
    
    def purge_cycle_row(self,wssheet, nrow, ncols):
        for ncol in range(ncols[0], ncols[-1]+1):
            setOutCell(wssheet, ncol, nrow, '')
    
    def insert_structs_row(self,wssheet, struct, nrow, ncols):
        _logger.info("---------------insert_structs_row-----------------%s :  ",struct)

        setOutCell(wssheet, ncols[0], nrow, struct.name)
        setOutCell(wssheet, ncols[1], nrow, struct.section_number)
    
    def generate_xlsx_sheet(self, wssheet,read_sheet, data, obj):
            
            dic={}
            click='http://www.google.com'
            wssheet.write(8,8,xlwt.Formula('HYPERLINK("%s";"Link")' % click)) 
            
            dic["id_etab"]=obj.etablissement_id.id or " "
            dic["annee"]="%s-%s" %(obj.year_start,obj.year_end) or " "
            setOutCell(wssheet,2, 1, obj.etablissement_id.state_id.name or 'n/a')
            dic["state_id"]= obj.etablissement_id.state_id.name or " "
            setOutCell(wssheet,2, 2, obj.etablissement_id.town_id.name or 'n/a')
            dic["town_id"]= obj.etablissement_id.town_id.name or " "
            setOutCell(wssheet,2, 3, obj.etablissement_id.name or 'n/a')
            dic["etablissement_id"]= obj.etablissement_id.name or " "
            setOutCell(wssheet,2, 4, obj.etablissement_id.number_id or 'n/a')
            setOutCell(wssheet,11, 1, "%s-%s" %(obj.year_start,obj.year_end) or 'n/a')
            setOutCell(wssheet,11, 2, datetime.datetime.now())
            setOutCell(wssheet,11, 3, obj.etablissement_id.classroom_count or 'n/a')
            setOutCell(wssheet,11, 4, obj.etablissement_id.classroom_conform_count or 'n/a')
            setOutCell(wssheet,11, 5, obj.etablissement_id.classroom_not_conform_count or 'n/a')
            
            if obj.etablissement_id.classroom_count > 0:
                pourcen_util_salle= round(obj.etablissement_id.classroom_not_conform_count/obj.etablissement_id.classroom_count, 2)
            else:
                pourcen_util_salle=0
            setOutCell(wssheet,17, 9, pourcen_util_salle or '0%')

            setOutCell(wssheet,16, 3, obj.etablissement_id.phone or 'n/a')
            setOutCell(wssheet,16, 4, obj.etablissement_id.fax or 'n/a')
            token = 'Niv' # Indexed world to locate the cycle array
            self.generate_cycle_table(wssheet, read_sheet, obj,dic, token)
            token = 'Niveau'
            self.generate_struct_table(wssheet, read_sheet, obj,dic)
            
             
            return dic
        
    def generate_cycle_table(self, wssheet, read_sheet, obj,dic, token):
        '''Generate cycle related row'''
        nrows, ncols = self.cycle_index_search(read_sheet, token)
        cycles = obj.line_ids 
        cycle_of_sheet_array = [] # To load existant Cycles on wssheet, meant for cycles that are present in the template
        nrow = nrows[0] # First row of the cycle edit
        check_cycle_exist = False
        cycle_index = 0 # Used to generate different rows with cycle values
        totinsc=0
        totfille=0
        totsec=0
        totredoub=0
        totfredoub=0
        if len(nrows) < len(cycles):
            _logger.info('You have too many cycles, we cannot display all of them')
        cycls=[]
        
        for nrow in nrows:
            if cycle_index < len(cycles):
                self.insert_cycle_row(wssheet, cycles[cycle_index], nrow, ncols)
                totinsc += cycles[cycle_index].inscriptions_count
                totfille +=cycles[cycle_index].inscriptions_female
                totsec += cycles[cycle_index].section_number
                totredoub += cycles[cycle_index].redoubles_count
                totfredoub += cycles[cycle_index].redouble_fille_count
                
                  
                
                xcyle=[]
                xcyle.append(cycles[cycle_index].name)
                xcyle.append( cycles[cycle_index].inscriptions_count)
                xcyle.append( cycles[cycle_index].section_number)
                cycls.append(xcyle)
                cycle_index += 1
                
            else:
                self.purge_cycle_row(wssheet, nrow, ncols)
        
        setOutCell(wssheet, ncols[1], nrows[-1]+1,totsec)
        setOutCell(wssheet, ncols[2], nrows[-1]+1,totinsc )
        setOutCell(wssheet, ncols[3],  nrows[-1]+1, totfille)
        setOutCell(wssheet, ncols[4],  nrows[-1]+1, totredoub)
        setOutCell(wssheet, ncols[5],  nrows[-1]+1, totfredoub)
        dic["totinsc"]= totinsc or " "
        dic["totfille"]= totfille or " "
        dic["totsec"]= totsec or " "
        dic["cycles"]= cycls or ""
          
        if totinsc > 0:
            pourcen_fille= round(totfille/totinsc, 2)
        else:
            pourcen_fille=0
        if totredoub > 0:
            pourcen_r_fille= round(totfredoub/totredoub, 2)
        else:
            pourcen_r_fille=0
        setOutCell(wssheet, ncols[5],  26, pourcen_fille    )
        setOutCell(wssheet, ncols[5],  27, pourcen_r_fille    )
           
        return True
    def generate_struct_table(self, wssheet, read_sheet, obj,dic):
        '''Generate cycle related row'''
        nrows= range(35, 54)
        ncols=range(2, 12)
        structs = obj.line_ids 
        _logger.info("---------------structs-----------------%s : ",structs)
        nrow = nrows[0] # First row of the cycle edit
        check_struct_exist = False
        struct_index = 0 # Used to generate different rows with cycle values
         
        if len(nrows) < len(structs):
            _logger.info('You have too many structs, we cannot display all of them')
        
        for nrow in nrows:
            if struct_index < len(structs):
                self.insert_structs_row(wssheet, structs[struct_index], nrow, ncols)
                struct_index += 1
                
#             else:
#                 self.purge_cycle_row(wssheet, nrow, ncols)
        
        return True
    
    
    def insert_cycle_dren_row(self,fsheet, resobjs, data, objs, nrows, ncols):
        
        nrow = nrows[0]
        index = 0
        filesCycles={'1AS': 3,'2AS': 5,'3AS': 7,'4AS': 9,'5A0': 11,'5C0': 13,'5D0': 15,'5O0': 17,'5LM': 19,'5SN': 21,'5M': 23,'6A0': 25,'6D0': 27,'6O0': 29,'6SN': 31,'6LO': 33,'7A0': 35,'7C0': 37,'7D0': 39,'7O0': 41,'7LO': 43,'7LM': 45,'7SN': 47,'7M':49}
        
        if len(nrows) < len(objs):
            _logger.info('You have too many lines, we cannot display all of them')
        for nrow in nrows:
            if index < len(objs):
                res= resobjs[index]
                _logger.info("---------------res-----------------%s : ",res)
                setOutCell(fsheet, 1, nrow, str(res['etablissement_id']))
                index += 1
                objcycle= res['cycles']
                for ncol in filesCycles:
                    for x in objcycle:
                        if x[0] ==ncol :
                            ncol1=filesCycles[ncol]
                            ncol2=filesCycles[ncol]+1
                            setOutCell(fsheet, ncol1, nrow,x[2] )
                            setOutCell(fsheet, ncol2, nrow, x[1])
                    
        
        
        
    def generate_dren_sheet(self,fsheet,read_fsheet,resobjs, data, objs):
        
        nrows= range(4, 30)
        ncols=range(2, 48)
       
       
        self.insert_cycle_dren_row(fsheet, resobjs, data, objs, nrows, ncols)
        return True
    
    def generate_wilaya_sheet(self,wilayasheet,read_fsheet,objs, data, etablissements):
        index=0
        nrow=1
        for obj in objs:
            if index < len(objs):
                ii=''+str(text_cleanup(obj.name))
                linkk = 'HYPERLINK("#\''+ str(ii) + '\'!A1", "'+str(obj.name)+'")'
                setOutCell(wilayasheet, 0, index+1,xlwt.Formula(linkk) )
                for etab in etablissements:
                    if nrow < len(etablissements):
                        i=''+str(text_cleanup(etab.etablissement_id.name))
                        link = 'HYPERLINK("#\''+ str(i) + '\'!A1", "'+str(etab.etablissement_id.name)+'")'
                        setOutCell(wilayasheet,2, nrow,xlwt.Formula(link))
                        nrow += 1
                index += 1
                
        
        
        