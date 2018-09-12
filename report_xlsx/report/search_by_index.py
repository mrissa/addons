from xlrd import open_workbook
import logging
_logger = logging.getLogger(__name__)

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
    return(range(nrow, nrow_final+1), range(ncol, ncol_final+1))

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
