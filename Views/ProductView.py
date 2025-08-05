from typing import List
from PyQt6 import QtGui, QtCore
import Views.Widgets.CustomWidgets as CustomWidgets
from Views.Localization import _
from ProjectTypes import *
from pprint import pprint

class ProductTable(CustomWidgets.Table):
	def __init__(self, products: List[Action]) -> None:
		super().__init__()
		self._components = products
		self.loadData(self._components)

	def loadData(self, components: List[Action]) -> None:
		""" load and reload data """
		self._components = components
		sti = TableModel(self._components)
		self.reset()
		sti.clear()
		sti.setHorizontalHeaderLabels([_('table.name'), _('table.left'), 'id'])
		sti.setRowCount(len(self._components))
		proxy_model = CustomSortFilterProxyModel()
		proxy_model.setSourceModel(sti)
		self.setModel(proxy_model)
		self.setDimensions()

	def setDimensions(self) -> None:
		self.setColumnWidth(0, 160)
		self.setColumnWidth(1, 120)
		self.setColumnHidden(2, True)
		self.setFixedWidth(298)

	def getSelectedRowId(self) -> int:
		index = self.currentIndex()
		NewIndex = self.model().index(index.row(), 2)
		return self.model().data(NewIndex)

class TableModel(QtGui.QStandardItemModel):
	def __init__(self, data: [Action]) -> None:
		super(TableModel, self).__init__()
		self._data = data

	def data(self, index, role=QtCore.Qt.ItemDataRole.DisplayRole) :
		if not index.isValid():
			return None
		if role == QtCore.Qt.ItemDataRole.TextAlignmentRole: # and index.column() != 1
			return QtCore.Qt.AlignmentFlag.AlignCenter
		if role == QtCore.Qt.ItemDataRole.DisplayRole:
			match index.column():
				case 0:
					return self._data[index.row()].getName()
				case 1:
					return f"{self._data[index.row()].getBalance():.2f}"
				case 2:
					return self._data[index.row()].getId()
		return None

	def reloadData(self, data) -> None:
		self._data = data

class CustomSortFilterProxyModel(QtCore.QSortFilterProxyModel):
	def lessThan(self, left_index, right_index) -> bool:
		left_data = self.sourceModel().data(left_index, QtCore.Qt.ItemDataRole.DisplayRole)
		right_data = self.sourceModel().data(right_index, QtCore.Qt.ItemDataRole.DisplayRole)
		if left_data is None and right_data is None:
			return False
		elif left_data is None:
			return True
		elif right_data is None:
			return False
		elif left_index.column() == 1:
			left_data = float(left_data)
			right_data = float(right_data)
		return left_data < right_data
