import sys
from Qt import QtWidgets, QtGui, QtCore
from Qt.QtCore import Qt

class ImageItemDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex) -> None:
        # super().paint(painter, option, index)
        print("here")
        print(option)


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
        list_view.setItemDelegate(item_delegate)
        layout.addWidget(list_view)

        entries = ['one', 'two', 'three']

        model = QtGui.QStandardItemModel()
        list_view.setModel(model)
        for i in entries:
            item = QtGui.QStandardItem(i)
            item.setSizeHint(QtCore.QSize(100,100))
            item.setBackground(Qt.green)
            model.appendRow(item)

        self.show()



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ex = ExampleListView()
    sys.exit(app.exec_())
