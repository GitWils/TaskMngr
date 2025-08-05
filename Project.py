from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtPrintSupport import QPrintDialog, QPrinter
from PyQt6.QtGui import QTextDocument
from PyQt6.QtWidgets import QTabWidget, QDialog, QStyleFactory

import Views.Dialogs.ProductDlg as Dialogs
import Views.ProductView as ProductView
import Views.ActionView as ActionView
import Views.Widgets.CustomWidgets as CustomWidgets
from Views.Localization import _
from Views.Dialogs.PrintDlg import PrintDlg
from Views.Widgets.ProductsTable import ProductsTable
from Views.Widgets.Logger import Logger
from Models.ProductManager import ProductMngr
from Decorators import Timing
from ProjectTypes import Theme

from pprint import pprint

class Settings:
    def __init__(self, theme: Theme = Theme.OS) -> None:
        self._theme = theme

    def setTheme(self, theme: Theme, dialog: QDialog = None) -> None:
        self._theme = theme
        if dialog and self._theme == Theme.OS:
            Settings.setOSTheme(dialog)
        elif dialog and self._theme == Theme.Dark:
            Settings.setDarkTheme(dialog)

    def getTheme(self) -> Theme:
        return self._theme

    @staticmethod
    def setDarkTheme(dialog: QtWidgets) -> None:
        with open("style.css", "r") as file:
            dialog.setStyleSheet(file.read())

    @staticmethod
    def setOSTheme(dialog: QtWidgets) -> None:
        dialog.setStyleSheet("")
        dialog.setStyle(QStyleFactory.create("Windows"))

class Project(QtWidgets.QWidget, Settings):
    """ widget fills main window"""
    def __init__(self) -> None:
        super().__init__()
        self._productMngr = ProductMngr()
        self._actionTable = None
        self._productTable = None
        self._editBtn = None
        self._delBtn = None
        self._logArea = Logger()

        self.initMenu()
        self.setTheme(self._productMngr.getTheme())

    def initMenu(self) -> None:
        centralLayout = QtWidgets.QVBoxLayout()
        self.setLayout(centralLayout)
        lblLog = QtWidgets.QLabel(_('lbl.logs'))
        # lblLog.clicked.connect(self.pringLogs)
        centralLayout.addWidget(self._initTabs())
        centralLayout.addWidget(lblLog)
        centralLayout.addWidget(self._logArea, Qt.AlignmentFlag.AlignBottom)
        self._logArea.showContent(self._productMngr.getLogs())

    def printActions(self) -> None:
        dialog = PrintDlg()
        self.setTheme(self.getTheme(), dialog)
        dialog.move(self._getInitPos(dialog.width()))
        result = dialog.exec()
        if result:
            printer = QPrinter()
            print_dialog = QPrintDialog(printer, self)
            print_dialog.setWindowTitle("Прінтер")
            print_dialog.setObjectName('printer')
            if print_dialog.exec() == QPrintDialog.DialogCode.Accepted:
                document = QTextDocument()
                self._productMngr.setFilterPeriod(dialog.getBeginDateStr(), dialog.getEndDateStr())
                self._productMngr.setFilterLimit(dialog.getLimit())
                document.setPlainText(self._productMngr.getLogsStr())
                document.print(printer)
                self._productMngr.filterClear()

    def _initTabs(self) -> QTabWidget:
        tabs = QtWidgets.QTabWidget()
        tabs.addTab(self.createProductsTab(), _("menu.products"))
        tabs.addTab(QtWidgets.QLabel("Тут могла бути ваша реклама"), _("menu.report"))
        tabs.setCurrentIndex(0)
        return tabs

    @Timing
    def createProductsTab(self) -> ProductsTable:
        """ products tab contents creation """
        self._productTable = ProductView.ProductTable(self._productMngr.getProducts())
        self._actionTable = ActionView.ActionTable(self._productMngr.getActionsList())
        tab = ProductsTable(self._productTable, self._actionTable)
        tab.addButton(self.addActionBtn, CustomWidgets.DlgMode.Add, True, _("tooltip.add"))
        subBtn = tab.addButton(self.subtractActionBtn, CustomWidgets.DlgMode.Sub, True, _("tooltip.pickup"))
        self._editBtn = tab.addButton(self.editActionBtn, CustomWidgets.DlgMode.Edit, False, _("tooltip.edit"))
        self._delBtn = tab.addButton(self.delActionBtn, CustomWidgets.DlgMode.Del, False, _("tooltip.del"))
        self._productTable.clicked.connect(self.showActions)
        self._actionTable.clicked.connect(self.setEditBtnsStatus)
        self._actionTable.doubleClicked.connect(self.editActionBtn)
        return tab

    def showActions(self) -> None:
        """ showing table with product actions """
        self._productMngr.setFilterID(self._productTable.getSelectedRowId())
        self.reloadTables()
        self.activateBtns(False)

    def setEditBtnsStatus(self) -> None:
        self.activateBtns(not self._actionTable.isBlockedRow(self._actionTable.getSelectedRowId()))

    def _getInitPos(self, width: int=0) -> QPoint:
        """ calculation the starting position point of dialog"""
        dlgPos = self.mapToGlobal(self.pos())
        dlgPos.setX(dlgPos.x() - width//2 + self.width()//2)
        dlgPos.setY(dlgPos.y() + self.height()//2 - 250)
        return dlgPos

    def addActionBtn(self) -> None:
        """ if the add action button was clicked """
        dialog = Dialogs.AddProductDlg(self._productMngr.getProducts())
        dialog.move(self._getInitPos(dialog.width()))
        self.setTheme(self.getTheme(), dialog)
        result = dialog.exec()
        if result:
            self._productMngr.addAction(dialog.getProduct(), dialog.getCount(), dialog.getNote())
            self._logArea.showContent(self._productMngr.getLogs())
            self.reloadTables()

    def subtractActionBtn(self) -> None:
        """ if subtract action button was clicked """
        dialog = Dialogs.SubtractProductDlg(self._productMngr.getProducts())
        self.setTheme(self.getTheme(), dialog)
        dialog.move(self._getInitPos(dialog.width()))
        result = dialog.exec()
        if result:
            self._productMngr.addAction(dialog.getProduct(), -dialog.getCount(), dialog.getNote())
            self._logArea.showContent(self._productMngr.getLogs())
            self.reloadTables()

    def editActionBtn(self) -> None:
        """ if edit action button was clicked """
        selectedActionID = self._actionTable.getSelectedRowId()
        if selectedActionID and not self._actionTable.isBlockedRow(selectedActionID):
            currentAction = self._productMngr.getActionById(self._actionTable.getSelectedRowId())
            dialog = Dialogs.EditProductDlg(self._productMngr.getProducts(), self._productMngr.getActionById(selectedActionID))
            self.setTheme(self.getTheme(), dialog)
            dialog.move(self._getInitPos(dialog.width()))
            result = dialog.exec()
            if result:
                self._productMngr.editAction(currentAction,
                                             dialog.getProduct(),
                                             dialog.getSign() * dialog.getCount(),
                                             dialog.getNote()
                                           )
                self._logArea.showContent(self._productMngr.getLogs())
                self.reloadTables()

    def delActionBtn(self) -> None:
        """ if delete action button was clicked """
        if self._actionTable.getSelectedRowId():
            currentAction = self._productMngr.getActionById(self._actionTable.getSelectedRowId())
            dialog = Dialogs.DelProductDlg(self._productMngr.getProducts(), currentAction)
            self.setTheme(self.getTheme(), dialog)
            dialog.move(self._getInitPos(dialog.width()))
            result = dialog.exec()
            if result:
                self._productMngr.delAction(currentAction)
                self._logArea.showContent(self._productMngr.getLogs())
                self.reloadTables()

    def activateBtns(self, status: bool) -> None:
        self._editBtn.setActive(status)
        self._delBtn.setActive(status)

    def reloadTables(self) -> None:
        self._actionTable.loadData(self._productMngr.getActionsList())
        self._productTable.loadData(self._productMngr.getProducts())

    def setTheme(self, theme: Theme, dialog: QDialog = None):
        self._productMngr.saveTheme(theme)
        super().setTheme(theme, dialog)

    def getTheme(self) -> Theme:
        return self._productMngr.getTheme()