from PyQt6.QtWidgets import QDialog
from PyQt6.QtCore import Qt
from Views.Widgets.DialogGrid import DialogGrid
from Views.Localization import _
from ProjectTypes import *
from pprint import pprint
from abc import ABC, abstractmethod, ABCMeta

class QtABCMeta(type(QDialog), ABCMeta):
    pass

class ProductDlg(QDialog,  metaclass=QtABCMeta):
	def __init__(self, products: list) -> None:
		super().__init__()
		self.setWindowModality(Qt.WindowModality.ApplicationModal)
		self.setFixedWidth(600)
		self.setMinimumHeight(400)
		self._products = products
		# self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowMaximizeButtonHint)
		self._dlgGrid = DialogGrid()
		self._drawProductField(_("dlg.name"))
		self._wgtCount = self._dlgGrid.addSpinBox(_("dlg.count"))
		self._wgtNote = self._dlgGrid.addNote(_("dlg.note"))
		self._bbox = self._dlgGrid.addButtonBox(True, acceptedFunc = self.accept, rejectedFunc=self.reject)
		self.setLayout(self._dlgGrid.getGrid())
		self._initValues()

	def accept(self) -> None:
		if len(self.getProduct()) == 0:
			self.setMsg('Введіть назву продукту!')
		elif self.getCount() == 0:
			self.setMsg('Вага не може мати нульове значення!')
		else:
			super().accept()

	def setMsg(self, msg: str) -> None:
		self._dlgGrid.setMsg(msg)
		self.adjustSize()

	@abstractmethod
	def _drawProductField(self, name) -> None:
		pass

	@abstractmethod
	def _initValues(self) -> None:
		pass

	def reject(self) -> None:
		super().reject()

	def getProduct(self) -> str:
		return ""

	def getCount(self) -> int:
		return self._wgtCount.value()

	def getNote(self) -> str:
		return self._wgtNote.toPlainText().strip()

	def getProductsList(self) -> list:
		res = []
		for product in self._products:
			res.append(product.getName())
		return res

class AddProductDlg(ProductDlg):
	def __init__(self, products: list) -> None:
		super().__init__(products)

	def _initValues(self) -> None:
		self.setWindowTitle(_("title.receipt"))

	def _drawProductField(self, name: str) -> None:
		self._productName = self._dlgGrid.addEditBox(name)
		self._productName.addItems(self.getProductsList())

	def getProduct(self) -> str:
		return self._productName.currentText().strip()

class SubtractProductDlg(ProductDlg):
	def __init__(self, products: list) -> None:
		super().__init__(products)

	def _initValues(self) -> None:
		self.setWindowTitle(_("title.submit"))

	def _drawProductField(self, name: str) -> None:
		self._productName = self._dlgGrid.addEditBox(name)
		self._productName.addItems(self.getProductsList())

	def getProduct(self) -> str:
		return self._productName.currentText().strip()

	def accept(self) -> None:
		present = False
		for item in self._products:
			if self.getProduct() == item.getName():
				present = True
			if self.getProduct() == item.getName() and self.getCount() > item.getBalance():
				self.setMsg(_("msg.missing"))
				return
		if not  present:
			self.setMsg(_("msg.missing"))
			return
		super().accept()

class EditProductDlg(ProductDlg):
	def __init__(self, products: list, action: {}) -> None:
		self._action = action
		super().__init__(products)

	def accept(self) -> None:
		if self.getProduct() == self._action.getName()\
			and self.getCount() == -self._action.getCount()\
			and self.getNote() == self._action.getNote():
			self.setMsg(_("msg.nochanges", txt=_("btn.cancel")))
			return
		elif self.getProduct() == self._action.getName():
			for item in self._products:
				if (self._action.getName() == item.getName()
					  and self._action.getCount() - self.getSign() * self.getCount() > item.getBalance()):
					self.setMsg(_("msg.missing"))
					return
		super().accept()

	def getSign(self) -> int:
		if self._action.getCount() < 0:
			return -1
		return 1

	def _initValues(self) -> None:
		self.setWindowTitle(_("title.edit"))
		self._wgtCount.setValue(self._action.getCount())
		self._wgtNote.setText(self._action.getNote())

	def _drawProductField(self, name: str) -> None:
		self._productName = self._dlgGrid.addLineEdit(name, self._action.getName())

	def getProduct(self) -> str:
		return self._productName.text().strip()

class DelProductDlg(ProductDlg):
	def __init__(self, products: list, action: Action) -> None:
		self._action = action
		super().__init__(products)

	def _initValues(self) -> None:
		self.setWindowTitle(_("title.delete"))
		self._wgtCount.setValue(abs(self._action.getCount()))
		self._wgtNote.setText(self._action.getNote())
		self._bbox.setBtnOkText(_("btn.delete"))
		self._setEnabledAll(False)

	def _drawProductField(self, name: str) -> None:
		self._productName = self._dlgGrid.addLineEdit(name, self._action.getName())

	def _setEnabledAll(self, enabled: bool=True) -> None:
		self._productName.setEnabled(enabled)
		self._wgtCount.setEnabled(enabled)
		self._wgtNote.setEnabled(enabled)

	def getProduct(self) -> str:
		return self._productName.text().strip()