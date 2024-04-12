import sys
from typing import Any, Dict, List

from Qt import QtCore, QtGui, QtWidgets
from Qt.QtCore import Qt


class StyledItemDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._multi_row_edit = False
        self._multi_column_edit = False

    def _setMultiEditData(self, index, value, role):
        """Set the given value at the index for the given role.
        If multi row/column editing is enabled, apply the edit
        for all selected row/columns.

        Args:
            index (QtCore.QModelIndex): The model index.
            value (Any): The value.
            role (Any): The role.
        """
        model = index.model()
        rows = set([index.row()])
        columns =set([index.column()])
        if self.multiRowEdit():
            view = self.parent()
            selection_model = view.selectionModel()
            rows.update([i.row() for i in selection_model.selectedRows()])
        if self.multiColumnEdit():
            view = self.parent()
            selection_model = view.selectionModel()
            columns.update([i.column() for i in selection_model.selectedColumns()])

        # Skip the active index as delegate editor 
        # close will trigger the paint event.
        model.blockSignals(True)
        changed_indices = []
        for row in rows:
            for column in columns:
                multi_index = model.index(row, column)
                if index != multi_index:
                    changed_indices.append(multi_index)
                model.setData(multi_index, value, role)
        model.blockSignals(False)
        for index in changed_indices:
            model.dataChanged.emit(index, index)


    def multiRowEdit(self) -> bool:
        return self._multi_row_edit

    def setMultiRowEdit(self, state: bool):
        if not isinstance(self.parent(), QtWidgets.QAbstractItemView):
            raise ValueError("To support multi row editing, the parent widget must be set to a valid view.")
        self._multi_row_edit = state

    def multiColumnEdit(self) -> bool:
        return self._multi_column_edit

    def setMultiColumnEdit(self, state: bool):
        if not isinstance(self.parent(), QtWidgets.QAbstractItemView):
            raise ValueError("To support multi column editing, the parent widget must be set to a valid view.")
        self._multi_column_edit = state


class ComboBoxItemDelegate(StyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.items = ["one", "two", "three"]
        self._showing_popup = False
        self._editor = None
        self._index = None

    def createEditor(self, parent: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex) -> QtWidgets.QWidget:
        self._showing_popup = False
        self._editor = QtWidgets.QComboBox(parent)
        self._editor.addItems(self.items)
        self._editor.currentTextChanged.connect(self.onDropDownCloseCallback)
        return self._editor

    def onDropDownCloseCallback(self):
        self.setModelData(self._editor, self._index.model(), self._index)

    def setEditorData(self, editor, index):
        self._index = index
        value = index.data(QtCore.Qt.DisplayRole)
        value_idx = max(0, self._editor.findData(value))
        editor.setCurrentIndex(value_idx)
        if not self._showing_popup:
            self._showing_popup = True
            editor.showPopup()

    def setModelData(self, editor, model, index):
        self._setMultiEditData(index, editor.currentData(Qt.DisplayRole), Qt.DisplayRole)


    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def paint(self, painter, option, index):
        text = index.data(Qt.DisplayRole)

        cb_style_option = QtWidgets.QStyleOptionComboBox()
        cb_style_option.rect = option.rect
        cb_style_option.currentText = text

        style = option.widget.style()
        style.drawComplexControl(QtWidgets.QStyle.CC_ComboBox, cb_style_option, painter)
        style.drawControl(QtWidgets.QStyle.CE_ComboBoxLabel, cb_style_option, painter)



class RowTableView(QtWidgets.QTableView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Selection
        self.setSelectionBehavior(self.SelectRows)
        self.setSelectionMode(self.ExtendedSelection)

        # Edit
        self.setEditTriggers(self.AllEditTriggers)


    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:

        if (event.button() == Qt.LeftButton):
            index = self.indexAt(event.pos())
            if (index.column() == 0):
                self.edit(index)
 
        super().mousePressEvent(event)


class ExampleListView(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        center_widget = QtWidgets.QWidget()
        self.setCentralWidget(center_widget)

        layout = QtWidgets.QVBoxLayout(center_widget)
        center_widget.setLayout(layout)

        # Table
        table_view = RowTableView()
        combobox_item_delegate = ComboBoxItemDelegate(table_view)
        combobox_item_delegate.setMultiRowEdit(True)
        table_view.setItemDelegateForColumn(0, combobox_item_delegate)

        table_model = QtGui.QStandardItemModel()
        table_view.setModel(table_model)
        table_data = [f"Item {i}" for i in range(100)]
        for row, label in enumerate(table_data):
            item_data = {}
            item_a = QtGui.QStandardItem(row)
            item_a.setBackground(Qt.green)
            item_a.setData(label, role=Qt.DisplayRole)
            item_b = QtGui.QStandardItem(row)
            item_b.setBackground(Qt.green)
            item_b.setData(label, role=Qt.DisplayRole)
            item_b.setEditable(False)
            table_model.appendRow((item_a, item_b))
        table_view.clearSelection()
        layout.addWidget(table_view)

        list_view = QtWidgets.QListView(self)
        list_view.setMouseTracking(True)
        list_view.setViewMode(QtWidgets.QListView.IconMode)
        # list_view.setItemDelegate(item_delegate)
        layout.addWidget(list_view)

        entries = ["one", "two", "three"]

        model = QtGui.QStandardItemModel()
        list_view.setModel(model)
        for i in entries:
            item_data = {}
            item = QtGui.QStandardItem(i)
            item.setData(item_data, Qt.UserRole)
            item.setSizeHint(QtCore.QSize(100, 100))
            item.setBackground(Qt.green)
            model.appendRow(item)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ex = ExampleListView()
    ex.show()
    sys.exit(app.exec_())
