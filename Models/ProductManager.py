from Models.DBManager import DBManager
from ProjectTypes import *
from pprint import pprint
import re

class ProductMngr:
	def __init__(self) -> None:
		self._db = DBManager()
		self._products = list()
		self._actions = dict()
		self._filter = Filter(0)
		self.reloadAll()
		#temp debug shows
		print("Products (ProductMngr.py __init__()):")
		for item in self._products:
			print(f"{item}")
		# print("Actions (ProductMngr.py __init__()):")
		# for key, item in self._actions.items():
		# 	print(f"   {item}")

	def getProducts(self) -> list:
		return self._products

	def getActionsList(self) -> list:
		res = list()
		for key, val in self._actions.items():
			res.append(val)
		return res

	def getActionsIdList(self) -> list:
		res = list()
		for key, val in self._actions.items():
			res.append(key)
		return res

	def getActions(self):
		return self._actions

	def getActionById(self, action_id: int) -> Action:
		return self._actions[action_id]

	def getLogs(self) -> []:
		return self._db.getLogs(self._filter)

	def getLogsStr(self) -> str:
		list = self._db.getLogs(self._filter)
		result = '\n'.join([f"{index + 1}. [{item[1]}] -> {item[0]}" for index, item in enumerate(list)])
		result = re.sub('<.*?>', '', result)
		return  result

	def addProduct(self, name: str) -> int:
		productId = self._db.newProduct(name)
		self.reloadProducts()
		return productId

	def getBalanceByProductId(self, product_id) -> float:
		res = None
		for product in self._products:
			if product.getId() == product_id:
				res = product.getBalance()
		return res

	def reloadAll(self) -> None:
		self.reloadProducts()
		self.reloadActions()

	def reloadProducts(self) -> None:
		self._products.clear()
		self._products = self._db.getProducts()

	def reloadActions(self) -> None:
		self._actions.clear()
		self._actions = self._db.getActions(self._filter)

	def addAction(self, product: str, count: int, note: str) -> None:
		productId = self.addProduct(product)
		balance = self.getBalanceByProductId(productId) + count
		self._db.newAction(productId, count, note)
		if count > 0:
			msg = f'отримано <span style="text-decoration: underline">{product}</span> '\
				f'кількістю <span style="text-decoration: underline">{count}</span> шт.'
		else:
			msg = f'передано в роботу <span style="text-decoration: underline">{product}</span> ' \
			      f'кількістю <span style="text-decoration: underline">{-count}</span> шт.'
		msg += f' -> залишок: <span style="text-decoration: underline">{balance}</span> шт.'
		self._db.newLogMsg(productId, msg)
		self.reloadAll()

	def delAction(self, action: Action) -> None:
		self._db.delActionById(action.getId(), action.getProductId())
		balance = self.getBalanceByProductId(action.getProductId()) - action.getCount()
		msg = f'видалено переміщення <span style="text-decoration: underline">{action.getName()}</span> '\
				f'кількістю <span style="text-decoration: underline">{abs(action.getCount())}</span> шт '\
				f'-> залишок: <span style="text-decoration: underline">{balance}</span> шт'
		self._db.newLogMsg(action.getProductId(), msg)
		self.reloadAll()

	def editAction(self,
	             original_action: Action,
	             product: str,
	             count: int,
	             note: str
	             ) -> None:
		if product != original_action.getName():
			self._db.updateProduct(product, original_action.getProductId())
		if count != original_action.getCount() or note != original_action.getNote():
			self._db.updateAction(original_action.getId(), original_action.getProductId(), count, note)
		balance = self.getBalanceByProductId(original_action.getProductId()) + (count - original_action.getCount())
		msg = f'відредаговано переміщення <span style="text-decoration: underline">{original_action.getName()}</span> '\
				f'-> залишок: <span style="text-decoration: underline">{balance:.2f}</span> кг'
		#f'вагою <span style="text-decoration: underline">{abs(action.getCount()):.2f}</span>, кг'
		self._db.newLogMsg(original_action.getProductId(), msg)
		self.reloadAll()

	def setFilterID(self, product_id: int) -> None:
		self._filter.setProductId(product_id)
		self.reloadActions()

	def setFilterPeriod(self, begin: str, end: str) -> None:
		self._filter.setBeginDate(begin)
		self._filter.setEndDate(end)

	def setFilterLimit(self, limit: int) -> None:
		self._filter.setLimit(limit)

	def filterClear(self) -> None:
		self._filter.clear()

	def saveTheme(self, theme: Theme) -> None:
		self._db.setTheme(theme)

	def getTheme(self) -> Theme:
		return  self._db.getTheme()