import sys
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtCore import Qt,pyqtSignal, QObject

        # for i in range(6):
        #     self.top_channel_cb.addItem('Item {0}'.format(str(i)))
        #     self.top_channel_cb.setItemChecked(i, False)

class CheckableComboBox(QComboBox):
	def __init__(self,parent=None):
		super().__init__(parent)
		self._changed = False

		self.view().pressed.connect(self.handleItemPressed)

	contentChanged = pyqtSignal()

	def setItemsChecked(self,chChk):
		for ix,b in enumerate(chChk):
			if(ix<self.count()):
				self.setItemChecked( ix, b)


	def setItemChecked(self, index, checked=False):
		item = self.model().item(index, self.modelColumn()) # QStandardItem object

		if checked:
			item.setCheckState(Qt.Checked)
		else:
			item.setCheckState(Qt.Unchecked)

	def handleItemPressed(self, index):
		item = self.model().itemFromIndex(index)

		if item.checkState() == Qt.Checked:
			item.setCheckState(Qt.Unchecked)
		else:
			item.setCheckState(Qt.Checked)
		self._changed = True
		self.contentChanged.emit()


	def hidePopup(self):
		if not self._changed:
			super().hidePopup()
		self._changed = False

	def itemChecked(self, index):
		item = self.model().item(index, self.modelColumn())
		return item.checkState() == Qt.Checked

	def itemCheckedList(self):
		lst = []
		for i in range(self.count()):
			lst.append(self.itemChecked(i))
		return lst