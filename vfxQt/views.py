import sys
from enum import Enum
from typing import Any, Dict, List

from Qt import QtCore, QtGui, QtWidgets
from Qt.QtCore import Qt

from vfxQt.style import get_palette

##############################
# Interfaces
##############################


class StyledItemDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._multi_row_edit = False
        self._multi_column_edit = False

    def _setMultiEditData(self, index: QtCore.QModelIndex, value: Any, role: int):
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
        columns = set([index.column()])
        if self.multiRowEdit():
            view = self.parent()
            selection_model = view.selectionModel()
            rows.update([i.row() for i in selection_model.selectedRows()])
        if self.multiColumnEdit():
            view = self.parent()
            selection_model = view.selectionModel()
            columns.update([i.column() for i in selection_model.selectedColumns()])
        for row in sorted(rows):
            for column in sorted(columns):
                multi_index = model.index(row, column)
                if self.validateEditData(multi_index, value, role):
                    self.setEditData(multi_index, value, role)

    def validateEditData(self, index: QtCore.QModelIndex, value: Any, role: int):
        """Validate the given value before writing it.
        Args:
            index (QtCore.QModelIndex): The model index.
            value (Any): The value.
            role (Any): The role.
        Returns:
            bool: Set the value if true, ignore the edit if false.
        """
        return True

    def setEditData(self, index: QtCore.QModelIndex, value: Any, role: int):
        """Apply the edit to the model.
        This method allows us to override how the data gets
        injected back into the model.
        Args:
            index (QtCore.QModelIndex): The model index.
            value (Any): The value.
            role (Any): The role.
        """
        index.model().setData(index, value, role)

    def multiRowEdit(self) -> bool:
        """Get the multi row edit enabled state.
        Returns:
            bool: The state.
        """
        return self._multi_row_edit

    def setMultiRowEdit(self, state: bool):
        """Set the multi row edit enabled state.
        Args:
            state (bool): The state.
        """
        if not isinstance(self.parent(), QtWidgets.QAbstractItemView):
            raise ValueError(
                "To support multi row editing, the parent widget must be set to a valid view."
            )
        self._multi_row_edit = state

    def multiColumnEdit(self) -> bool:
        """Get the multi column edit enabled state.
        Returns:
            bool: The state.
        """
        return self._multi_column_edit

    def setMultiColumnEdit(self, state: bool):
        """Set the multi column edit enabled state.
        Args:
            state (bool): The state.
        """
        if not isinstance(self.parent(), QtWidgets.QAbstractItemView):
            raise ValueError(
                "To support multi column editing, the parent widget must be set to a valid view."
            )
        self._multi_column_edit = state


##############################
# Delegates
##############################


class ComboBoxItemDelegateSourceMode(Enum):
    role = "role"
    func = "func"


class ComboBoxItemDelegate(StyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._item_value_role = Qt.DisplayRole
        self._items_source_mode = ComboBoxItemDelegateSourceMode.role
        self._items_source_role = Qt.UserRole
        self._items_source_func = lambda i: []
        self._items_value_label = {}

        self._showing_popup = False
        self._editor = None
        self._index = None

    def validateEditData(self, index: QtCore.QModelIndex, value: Any, role: int):
        """Validate the given value before writing it.
        Args:
            index (QtCore.QModelIndex): The model index.
            value (Any): The value.
            role (Any): The role.
        Returns:
            bool: Set the value if true, ignore the edit if false.
        """
        if role == self._item_value_role:
            items = [i[-1] for i in self.getItems(index)]
            return value in items
        return True

    def setEditData(self, index: QtCore.QModelIndex, value: Any, role: int):
        """Apply the edit to the model.
        Args:
            index (QtCore.QModelIndex): The model index.
            value (Any): The value.
            role (Any): The role.
        """
        if role == self._item_value_role:
            super().setEditData(index, value, role)
            # This propagates the label of the current item to the multi edit item.
            # As a condition of how this widget works, we expect each index to
            # have the same label for each value. Indices can still have varying
            # items, only the label must match the value.
            if role != Qt.DisplayRole:
                super().setEditData(
                    index, self._items_value_label[value], Qt.DisplayRole
                )

    def getItemValueRole(self):
        """Get the item value role.
        Args:
            int: The role.
        """
        return self._item_value_role

    def setItemValueRole(self, role: int):
        """Set the item value role.
        Args:
            role (int): The role.
        """
        self._item_value_role = role

    def getItems(self, index: QtCore.QModelIndex):
        """Get the items based on the source mode.
        Args:
            index (QtCore.QModelIndex): The model index.
        Returns:
            list[str]: The items. This optionally also accepts the sources
                       to return a list of [(icon, label, value),
                       (label, value)] tuples.
        """
        if self._items_source_mode == ComboBoxItemDelegateSourceMode.role:
            raw_items = index.data(self._items_source_role) or []
        elif self._items_source_mode == ComboBoxItemDelegateSourceMode.func:
            raw_items = self._items_source_func(index) or []
        items = []
        for item in raw_items:
            if isinstance(item, tuple):
                items.append(item)
            else:
                items.append((item, item))
        return items

    def getItemsSourceMode(self):
        """Get the item source mode.
        Returns:
            ComboBoxItemDelegateSourceMode: The mode.
        """
        return self._items_source_mode

    def setItemsSourceMode(self, mode: ComboBoxItemDelegateSourceMode):
        """Set the item source mode.
        Args:
            mode (ComboBoxItemDelegateSourceMode): The mode.
        """
        self._items_source_mode = mode

    def getItemsSourceRole(self):
        """Get the item source role.
        Args:
            int: The role.
        """
        return self._items_source_role

    def setItemsSourceRole(self, role: int):
        """Set the item source role.
        Args:
            role (int): The role.
        """
        self._items_source_role = role

    def getItemsSourceFunction(self):
        """Get the item source function.
        The function when called has the
        active index as its input arg.
        Args:
            role (func): The callable function.
        """
        return self._items_source_func

    def setItemsSourceFunction(self, func: Any):
        """Set the item source function.
        The function when called has the
        active index as its input arg.
        Args:
            role (func): The callable function.
        """
        self._items_source_func = func

    def onDropDownCloseCallback(self):
        """The combobox dropdown close callback."""
        self.setModelData(self._editor, self._index.model(), self._index)

    def createEditor(
        self,
        parent: QtWidgets.QWidget,
        option: QtWidgets.QStyleOptionViewItem,
        index: QtCore.QModelIndex,
    ) -> QtWidgets.QWidget:
        """Create the editor data.
        Args:
            parent (QtWidgets.QWidget): The parent widget.
            option (QtWidgets.QStyleOptionViewItem): The style option.
            index (QtCore.QModelIndex): The model index.
        Returns:
            QtWidgets.QWidget: The editor widget.
        """
        self._showing_popup = False
        self._items_value_label.clear()
        self._editor = QtWidgets.QComboBox(parent)
        for item in self.getItems(index):
            self._items_value_label[item[-1]] = item[-2]
            self._editor.addItem(*item)
        self._editor.currentTextChanged.connect(self.onDropDownCloseCallback)
        return self._editor

    def setEditorData(self, editor: QtWidgets.QWidget, index: QtCore.QModelIndex):
        """Set the editor data.
        Args:
            editor (QtWidgets.QWidget): The widget.
            index (QtCore.QModelIndex): The model index.
        """
        self._index = index
        value = index.data(self._item_value_role)
        value_idx = max(0, self._editor.findData(value, Qt.UserRole))
        editor.blockSignals(True)
        editor.setCurrentIndex(value_idx)
        editor.blockSignals(False)
        if not self._showing_popup:
            self._showing_popup = True
            editor.showPopup()

    def setModelData(
        self,
        editor: QtWidgets.QWidget,
        model: QtCore.QAbstractItemModel,
        index: QtCore.QModelIndex,
    ) -> None:
        """Set the model data.
        Args:
            editor (QtWidgets.QWidget): The widget.
            model (QtCore.QAbstractItemModel): The item model.
            index (QtCore.QModelIndex): The model index.
        """
        self._setMultiEditData(
            index, editor.currentData(Qt.UserRole), self._item_value_role
        )

    def paint(
        self,
        painter: QtGui.QPainter,
        option: QtWidgets.QStyleOptionViewItem,
        index: QtCore.QModelIndex,
    ) -> None:
        """Paint the combobox.
        Args:
            painter (QtGui.QPainter): The painter.
            option (QtWidgets.QStyleOptionViewItem): The style option.
            index (QtCore.QModelIndex): The model index.
        """
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



if __name__ == "__main__":
    palette = get_palette()
    app = QtWidgets.QApplication(sys.argv)
    app.setPalette(palette)
    example = ExampleListView()

    sys.exit(app.exec_())
