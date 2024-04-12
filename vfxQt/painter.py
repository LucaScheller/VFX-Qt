import sys
from typing import Any, Dict, List

from Qt import QtCore, QtGui, QtWidgets
from Qt.QtCore import Qt


class ImageItemDelegate(QtWidgets.QStyledItemDelegate):
    def paint(
        self,
        painter: QtGui.QPainter,
        option: QtWidgets.QStyleOptionViewItem,
        index: QtCore.QModelIndex,
    ) -> None:
        # super().paint(painter, option, index)

        print("here")
        print(option)


class Model(QtCore.QAbstractItemModel):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    ####################
    # Header Data
    ####################
    def headerData(
        self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole
    ) -> Any:
        return super().headerData(section, orientation, role)

    def setHeaderData(
        self,
        section: int,
        orientation: Qt.Orientation,
        value: Any,
        role: Qt.ItemDataRole = ...,
    ) -> bool:
        return super().setHeaderData(section, orientation, value, role)

    ####################
    # Item Data
    ####################
    def data(self, index: QtCore.QModelIndex, role: Qt.ItemDataRole) -> Any:
        return super().data(index, role)

    def setData(
        self, index: QtCore.QModelIndex, value: Any, role: Qt.ItemDataRole
    ) -> bool:
        return super().setData(index, value, role)

    def itemData(self, index: QtCore.QModelIndex) -> Dict[int, Any]:
        return super().itemData(index)

    def clearItemData(self, index: QtCore.QModelIndex):
        pass

    def flags(self, index: QtCore.QModelIndex):
        """-> Qt.ItemFlags | Qt.ItemFlag"""
        return super().flags(index)

    def roleNames(self) -> Dict[int, QtCore.QByteArray]:
        return super().roleNames()

    ####################
    # Lazy Loading
    ####################
    def canFetchMore(self, parent: QtCore.QModelIndex) -> bool:
        return super().canFetchMore(parent)

    def fetchMore(self, parent: QtCore.QModelIndex) -> None:
        return super().fetchMore(parent)

    ####################
    # Hierarchy
    ####################
    def hasIndex(self, row: int, column: int, parent: QtCore.QModelIndex) -> bool:
        return super().hasIndex(row, column, parent)

    def index(
        self, row: int, column: int, parent: QtCore.QModelIndex
    ) -> QtCore.QModelIndex:
        return super().index(row, column, parent)

    def parent(self, parent: QtCore.QModelIndex) -> bool:
        return super().parent(parent)

    def setParent(self, parent: QtCore.QObject) -> None:
        return super().setParent(parent)

    def hasChildren(self, parent: QtCore.QModelIndex) -> bool:
        return super().hasChildren(parent)

    def rowCount(self, parent: QtCore.QModelIndex) -> int:
        return super().rowCount(parent)

    def columnCount(self, parent: QtCore.QModelIndex) -> int:
        return super().columnCount(parent)

    def sibling(
        self, row: int, column: int, idx: QtCore.QModelIndex
    ) -> QtCore.QModelIndex:
        return super().sibling(row, column, idx)

    def buddy(self, index: QtCore.QModelIndex) -> QtCore.QModelIndex:
        return super().buddy(index)

    ####################
    # Hierarchy Edit
    ####################

    def sort(self, column: int, order: Qt.SortOrder = ...) -> None:
        return super().sort(column, order)

    def insertRows(self, row: int, count: int, parent: QtCore.QModelIndex) -> bool:
        self.beginInsertRows(parent, row, row + count)
        for row_offset_idx in range(count):
            # TODO Insert
            continue
        self.endInsertRows()

    def removeRows(
        self, row: int, count: int, parent: QtCore.QModelIndex = ...
    ) -> bool:
        self.beginRemoveRows(parent, row, row + count)
        for row_offset_idx in range(count):
            # TODO Insert
            continue
        self.endRemoveRows()

    def insertColumns(
        self, column: int, count: int, parent: QtCore.QModelIndex
    ) -> bool:
        self.beginInsertColumns(parent, column, column + count)
        for col_offset_idx in range(count):
            # TODO Insert
            continue
        self.endInsertColumns()

    def removeColumns(
        self, column: int, count: int, parent: QtCore.QModelIndex = ...
    ) -> bool:
        self.beginRemoveColumns(parent, column, column + count)
        for col_offset_idx in range(count):
            # TODO Insert
            continue
        self.endRemoveColumns()

    def moveRows(
        self,
        sourceParent: QtCore.QModelIndex,
        sourceRow: int,
        count: int,
        destinationParent: QtCore.QModelIndex,
        destinationChild: int,
    ) -> bool:
        self.beginMoveRows(
            sourceParent,
            sourceRow,
            sourceRow + count,
            destinationParent,
            destinationChild,
        )
        for row_offset_idx in range(count):
            # TODO Insert
            continue
        self.endMoveRows()

    def moveColumns(
        self,
        sourceParent: QtCore.QModelIndex,
        sourceColumn: int,
        count: int,
        destinationParent: QtCore.QModelIndex,
        destinationChild: int,
    ) -> bool:
        self.beginMoveRows(
            sourceParent,
            sourceColumn,
            sourceColumn + count,
            destinationParent,
            destinationChild,
        )
        for col_offset_idx in range(count):
            # TODO Insert
            continue
        self.endMoveRows()

    ####################
    # Drag'n'Drop
    ####################
    def supportedDragActions(self):
        # -> Qt.DropActions | Qt.DropAction
        return super().supportedDragActions()

    def supportedDropActions(self):
        # -> Qt.DropActions | Qt.DropAction
        return super().supportedDropActions()

    def canDropMimeData(
        self,
        data: QtCore.QMimeData,
        action: Qt.DropAction,
        row: int,
        column: int,
        parent: QtCore.QModelIndex,
    ) -> bool:
        return super().canDropMimeData(data, action, row, column, parent)

    def dropMimeData(
        self,
        data: QtCore.QMimeData,
        action: Qt.DropAction,
        row: int,
        column: int,
        parent: QtCore.QModelIndex,
    ) -> bool:
        return super().dropMimeData(data, action, row, column, parent)

    def mimeData(self, indexes: list[QtCore.QModelIndex]) -> QtCore.QMimeData:
        pass

    def mimeTypes(self) -> List[str]:
        return super().mimeTypes()

    ####################
    # Search
    ####################
    def match(
        self,
        start: QtCore.QModelIndex,
        role: Qt.ItemDataRole,
        value: Any,
        hits: int,
        flags: Qt.MatchFlags,
    ) -> List[int]:
        return super().match(start, role, value, hits, flags)


class ExampleListView(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        center_widget = QtWidgets.QWidget()
        self.setCentralWidget(center_widget)

        layout = QtWidgets.QVBoxLayout(center_widget)
        center_widget.setLayout(layout)

        item_delegate = ImageItemDelegate()
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
