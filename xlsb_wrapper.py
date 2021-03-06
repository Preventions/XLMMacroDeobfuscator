from excel_wrapper import ExcelWrapper
from pyxlsb2 import open_workbook
from pyxlsb2.formula import Formula
import os
from boundsheet import *

class XLSBWrapper(ExcelWrapper):
    def __init__(self, xlsb_doc_path):
        self._xlsb_workbook = open_workbook(xlsb_doc_path)
        self._macrosheets = None
        self._defined_names = None

    def get_defined_names(self):
        names = {}
        for key,val in self._xlsb_workbook.defined_names.items():
            names[key.lower()] = key.lower(), val.formula
        return names

    def get_defined_name(self, name, full_match=True):
        result = []
        if name in self.get_defined_names():
            result.append(self.get_defined_names()[name])
        return result

    def load_cells(self, boundsheet):
        with self._xlsb_workbook.get_sheet_by_name(boundsheet.name) as sheet:
            for row in sheet:
                for cell in row:
                    tmp_cell = Cell()
                    tmp_cell.row = cell.row_num + 1
                    tmp_cell.column = Cell.convert_to_column_name(cell.col+1)

                    tmp_cell.value = cell.value
                    tmp_cell.sheet = boundsheet
                    formula_str = Formula.parse(cell.formula)
                    if formula_str._tokens:
                        try:
                            tmp_cell.formula = '='+formula_str.stringify(self._xlsb_workbook)
                        except NotImplementedError as exp:
                            print('ERROR({}) {}'.format(exp, str(cell)))
                        except Exception:
                            print('ERROR ' + str(cell))
                    if tmp_cell.value is not None or tmp_cell.formula is not None:
                        boundsheet.cells[tmp_cell.get_local_address()] = tmp_cell

    def get_macrosheets(self):
        if self._macrosheets is None:
            self._macrosheets = {}
            for xlsb_sheet in self._xlsb_workbook.sheets:
                if xlsb_sheet.type == 'macrosheet':
                    with self._xlsb_workbook.get_sheet_by_name(xlsb_sheet.name) as sheet:
                        macrosheet = Boundsheet(xlsb_sheet.name, 'macrosheet')
                        self.load_cells(macrosheet)
                        self._macrosheets[macrosheet.name] = macrosheet

                #self.load_cells(macrosheet, workbook)
                #self._macrosheets[workbook.name] = macrosheet

        return self._macrosheets


if __name__ == '__main__':

    # path = r"tmp\xlsb\179ef8970e996201815025c1390c88e1ab2ea59733e1c38ec5dbed9326d7242a"
    path = r"tmp\xlsb\[CONVERTED]01558388b33abe05f25afb6e96b0c899221fe75b037c088fa60fe8bbf668f606.xlsb"

    path = os.path.abspath(path)
    excel_doc = XLSBWrapper(path)

    macrosheets = excel_doc.get_macrosheets()

    auto_open_labels = excel_doc.get_defined_name('auto_open', full_match=False)
    for label in auto_open_labels:
        print('auto_open: {}->{}'.format(label[0], label[1]))

    for macrosheet_name in macrosheets:
        print('SHEET: {}\t{}'.format(macrosheets[macrosheet_name].name,
                                     macrosheets[macrosheet_name].type))
        for formula_loc, info in macrosheets[macrosheet_name].cells.items():
            if info.formula is not None:
                print('{}\t{}\t{}'.format(formula_loc, info.formula, info.value))

        for formula_loc, info in macrosheets[macrosheet_name].cells.items():
            if info.formula is None:
                print('{}\t{}\t{}'.format(formula_loc, info.formula, info.value))

