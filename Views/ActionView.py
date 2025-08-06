from PyQt6 import QtGui, QtCore, QtWidgets
import Views.Widgets.CustomWidgets as CustomWidgets
from Views.Localization import _
from ProjectTypes import Action
from datetime import datetime

from pprint import pprint

class ActionTable(CustomWidgets.Table):
	def __init__(self, components: {Action} = None) -> None:
		super().__init__()
		self._components = components
		self.loadData(self._components)

	def loadData(self, components: {Action}) -> None:
		""" load and reload data """
		self._components = components
		sti = TableModel(self._components)
		self.reset()
		sti.clear()
		sti.setHorizontalHeaderLabels([_("table.name"), _("table.count"), _("table.date"), _("table.note"), 'id'])
		sti.setRowCount(len(self._components))
		proxy_model = CustomSortFilterProxyModel()
		proxy_model.setSourceModel(sti)
		self.setModel(proxy_model)
		self.setDimensions()

	def setDimensions(self) -> None:
		self.setColumnWidth(0, 200)
		self.setColumnWidth(1, 120)
		self.setColumnWidth(2, 140)
		self.setColumnWidth(3, 256)
		self.setColumnHidden(4, True)
		self.setMinimumWidth(500)
		header = self.horizontalHeader()
		header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeMode.Stretch)
		# header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

	def getSelectedRowId(self) -> int:
		index = self.currentIndex()
		NewIndex = self.model().index(index.row(), 4)
		return self.model().data(NewIndex)

	def isBlockedRow(self, component_id: int) -> bool:
		for component in self._components:
			if component.getId() == component_id:
				return component.isBlocked()
		return True

class TableModel(QtGui.QStandardItemModel):
	def __init__(self, data :{Action}):
		super(TableModel, self).__init__()
		self._data = data

	def data(self, index, role=QtCore.Qt.ItemDataRole.DisplayRole):
		if not index.isValid():
			return None
		if role == QtCore.Qt.ItemDataRole.TextAlignmentRole: # and index.column() != 1
			return QtCore.Qt.AlignmentFlag.AlignCenter
		if role == QtCore.Qt.ItemDataRole.DisplayRole:
			match index.column():
				case 0:
					return self._data[index.row()].getName()
				case 1:
					return f"{self._data[index.row()].getCount()}"
				case 2:
					return self._data[index.row()].getDate()
					# return self._data[index.row()].getDate().strftime("%d.%m.%y")
				case 3:
					return self._data[index.row()].getNote()
				case 4:
					return self._data[index.row()].getId()
		if role == QtCore.Qt.ItemDataRole.BackgroundRole and index.column() == 1:
			val = int(self._data[index.row()].getCount())
			if val < 0:
				return QtGui.QColor('#caa')
			elif val > 0:
				return QtGui.QColor('#aca')
		return None

	def reloadData(self, data):
		self._data = data

class CustomSortFilterProxyModel(QtCore.QSortFilterProxyModel):
	def lessThan(self, left_index, right_index):
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
		elif left_index.column() == 2:
			left_data = datetime.strptime(left_data, "%H:%M %d.%m.%Y")
			right_data = datetime.strptime(right_data, "%H:%M %d.%m.%Y")
		return left_data < right_data
