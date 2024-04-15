import os
import sys

from Qt import QtCore, QtGui, QtWidgets
from Qt.QtCore import Qt

from vfxQt.media import getImageCache
from vfxQt.style import get_palette
from vfxQt.views import (
    ComboBoxItemDelegate,
    ComboBoxItemDelegateSourceMode,
    HtmlItemDelegate,
    ImageItemDelegate,
    RowTableView,
)
from vfxQt.widgets import FoldArea, ToggleButton, ToggleButtonColorRole


class ExampleToggleButton(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        center_widget = QtWidgets.QWidget()
        self.setCentralWidget(center_widget)

        layout = QtWidgets.QVBoxLayout(center_widget)
        center_widget.setLayout(layout)

        # ToggleButton
        self.toggle_horizontal_button = ToggleButton(Qt.Horizontal)
        self.toggle_horizontal_button.setMinimumSize(200, 50)
        layout.addWidget(self.toggle_horizontal_button)

        # Stylized ToggleButton
        toggle_gradient = QtGui.QRadialGradient(0, 0, 1)
        toggle_gradient.setColorAt(0, QtGui.QColor.fromHsvF(0, 0, 1, 0.1))
        toggle_gradient.setColorAt(0.79, QtGui.QColor.fromHsvF(0, 0, 0.2, 0.05))
        toggle_gradient.setColorAt(0.8, QtGui.QColor.fromHsvF(0, 0, 1, 0.25))
        toggle_gradient.setColorAt(1, QtGui.QColor.fromHsvF(0, 0, 1, 0.0))
        toggle_gradient = QtGui.QLinearGradient(0, 0, 1, 0)
        toggle_gradient.setColorAt(0, QtGui.QColor.fromHsvF(0, 0, 1, 0.0))
        toggle_gradient.setColorAt(0.3, QtGui.QColor.fromHsvF(0, 0, 1, 0.25))
        toggle_gradient.setColorAt(0.35, QtGui.QColor.fromHsvF(0, 0, 0.2, 0.05))
        toggle_gradient.setColorAt(1, QtGui.QColor.fromHsvF(0, 0, 0, 0.0))
        self.toggle_vertical_button = ToggleButton()
        self.toggle_vertical_button.setMinimumSize(50, 100)
        self.toggle_vertical_button.setColor(
            ToggleButtonColorRole.toggleGradient, toggle_gradient
        )
        self.toggle_vertical_button.setBorderWidth(2)
        self.toggle_vertical_button.setBackgroundRadiusPercentage(0.5)
        self.toggle_vertical_button.setColor(
            ToggleButtonColorRole.border, QtGui.QColor.fromHsvF(0, 0, 0.6)
        )
        layout.addWidget(self.toggle_vertical_button)

        # Disabled ToggleButton
        self.toggle_disabled_button = ToggleButton()
        self.toggle_disabled_button.setFixedSize(100, 50)
        self.toggle_disabled_button.setEnabled(False)
        self.toggle_disabled_button.setToggleRadiusPercentage(0.5)
        self.toggle_disabled_button.setBackgroundRadiusPercentage(0.25)
        layout.addWidget(self.toggle_disabled_button)

        # Toggle ToggleButton
        self.push_button = QtWidgets.QPushButton("Push Me")
        self.push_button.setCheckable(True)
        self.push_button.clicked.connect(self.onPushButtonClicked)
        layout.addWidget(self.push_button)

        self.show()

    def onPushButtonClicked(self, value):
        self.toggle_horizontal_button.setToggled(self.push_button.isChecked())
        self.toggle_vertical_button.setToggled(self.push_button.isChecked())
        self.toggle_disabled_button.setToggled(self.push_button.isChecked())



class ExampleFoldArea(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        center_widget = QtWidgets.QWidget()
        self.setCentralWidget(center_widget)

        layout = QtWidgets.QVBoxLayout(center_widget)
        layout.setAlignment(Qt.AlignTop)
        center_widget.setLayout(layout)

        toggle_button = ToggleButton(self)
        toggle_button.toggleValueChanged.connect(self.onToggleValueChanged)
        toggle_button.setBackgroundRadiusPercentage(0.5)
        toggle_button.setFixedSize(50, 25)
        layout.addWidget(toggle_button)

        self.fold_area = FoldArea(self)
        self.fold_area.setToggleAnimationEasingCurve(QtCore.QEasingCurve.Type.OutBounce)
        self.fold_area.setToggleAnimationTime(500)

        fold_layout = self.fold_area.layout()
        fold_layout.addWidget(QtWidgets.QLabel("Some Text in Section"))
        fold_layout.addWidget(QtWidgets.QPushButton("Button in Section"))
        layout.addWidget(self.fold_area)

        self.show()

    def onToggleValueChanged(self, value):
        self.fold_area.setToggled(value)


class ExampleComboBoxItemDelegate(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        center_widget = QtWidgets.QWidget()
        self.setCentralWidget(center_widget)

        layout = QtWidgets.QVBoxLayout(center_widget)
        center_widget.setLayout(layout)

        # Combobox Delegate
        table_view = RowTableView()

        items_style_a = ["one", "two", "three"]
        items_style_b = [
            ("One Label", "one"),
            ("Two Label", "two"),
            ("Three Label", "three"),
        ]

        def item_style_c_func(index):
            row = index.row()
            items = []
            for i in range(row + 1):
                items.append((f"Idx {i}", f"idx_{i}"))
            return items

        items_style_c = ("Idx 0", "idx_0")

        combobox_item_delegate_style_a = ComboBoxItemDelegate(table_view)
        combobox_item_delegate_style_a.setMultiRowEdit(True)
        combobox_item_delegate_style_a.setItemsSourceRole(Qt.UserRole)
        table_view.setItemDelegateForColumn(1, combobox_item_delegate_style_a)

        combobox_item_delegate_style_b = ComboBoxItemDelegate(table_view)
        combobox_item_delegate_style_b.setMultiRowEdit(True)
        combobox_item_delegate_style_b.setItemValueRole(Qt.UserRole)
        combobox_item_delegate_style_b.setItemsSourceRole(Qt.UserRole + 1)
        table_view.setItemDelegateForColumn(2, combobox_item_delegate_style_b)

        combobox_item_delegate_style_c = ComboBoxItemDelegate(table_view)
        combobox_item_delegate_style_c.setMultiRowEdit(True)
        combobox_item_delegate_style_c.setItemValueRole(Qt.UserRole)
        combobox_item_delegate_style_c.setItemsSourceMode(
            ComboBoxItemDelegateSourceMode.func
        )
        combobox_item_delegate_style_c.setItemsSourceFunction(item_style_c_func)
        table_view.setItemDelegateForColumn(3, combobox_item_delegate_style_c)

        table_model = QtGui.QStandardItemModel()
        table_view.setModel(table_model)

        for row in range(100):
            item_label = QtGui.QStandardItem(row)
            item_label.setData(f"Label {row}", role=Qt.DisplayRole)
            item_label.setEditable(False)

            item_style_a = QtGui.QStandardItem(row)
            item_style_a.setBackground(Qt.green)
            item_style_a.setData(items_style_a[0], role=Qt.DisplayRole)
            item_style_a.setData(items_style_a, role=Qt.UserRole)

            item_style_b = QtGui.QStandardItem(row)
            item_style_b.setBackground(Qt.blue)
            item_style_b.setData(items_style_b[0][0], role=Qt.DisplayRole)
            item_style_b.setData(items_style_b[0][1], role=Qt.UserRole)
            item_style_b.setData(items_style_b, role=Qt.UserRole + 1)

            item_style_c = QtGui.QStandardItem(row)
            item_style_c.setBackground(Qt.blue)
            item_style_c.setData(items_style_c[0], role=Qt.DisplayRole)
            item_style_c.setData(items_style_c[1], role=Qt.UserRole)

            table_model.appendRow(
                (item_label, item_style_a, item_style_b, item_style_c)
            )

        layout.addWidget(table_view)

        # Show
        self.resize(800, 400)
        self.show()


class ExampleHtmlItemDelegate(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        center_widget = QtWidgets.QWidget()
        self.setCentralWidget(center_widget)

        layout = QtWidgets.QVBoxLayout(center_widget)
        center_widget.setLayout(layout)

        # Html Delegate
        list_view = QtWidgets.QListView(self)
        list_view.setMouseTracking(True)
        list_view.setViewMode(QtWidgets.QListView.IconMode)
        layout.addWidget(list_view)

        html_item_delegate = HtmlItemDelegate(list_view)
        html_item_delegate.setItemValueRole(Qt.UserRole)
        list_view.setItemDelegate(html_item_delegate)

        html = """
        <html>
            <body>
                <h3>HTML Example Heading</h3>
                <p>HTML Example Paragraph A</p>
                <p>HTML Example Paragraph B</p>
            </body>
        </html>
        """

        html = """
        <div width=100%, height=100%>
            <p style="color:blue">HTML Example Paragraph A</p>
            <p>HTML Example Paragraph B</p>
        </div>
        """

        model = QtGui.QStandardItemModel()
        list_view.setModel(model)
        for i in range(10):
            item = QtGui.QStandardItem(i)
            item.setData("", Qt.DisplayRole)
            item.setData(html, Qt.UserRole)
            item.setSizeHint(QtCore.QSize(100, 100))
            item.setEditable(False)
            item.setBackground(Qt.green)
            model.appendRow(item)

        # Show
        self.resize(800, 400)
        self.show()


class ExampleImageItemDelegate(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        center_widget = QtWidgets.QWidget()
        self.setCentralWidget(center_widget)

        layout = QtWidgets.QVBoxLayout(center_widget)
        center_widget.setLayout(layout)

        # Cache
        media_dir_path = os.path.join(
            os.path.dirname(os.path.os.path.dirname(__file__)), "media"
        )
        image_cache = getImageCache()
        image_cache.addSearchPath(media_dir_path)

        # Image Delegate
        list_view = QtWidgets.QListView(self)
        list_view.setMouseTracking(True)
        list_view.setViewMode(QtWidgets.QListView.IconMode)
        layout.addWidget(list_view)

        image_item_delegate = ImageItemDelegate(list_view)
        image_item_delegate.setImageCache(image_cache)
        image_item_delegate.repaintNeeded.connect(self.queueUpdate)
        list_view.setItemDelegate(image_item_delegate)

        import random

        image_resource_name = "loading_dual_ring.svg"
        # image_resource_name = "loading_gear_0.png"

        model = QtGui.QStandardItemModel()
        list_view.setModel(model)
        for i in range(1000):
            item = QtGui.QStandardItem()
            item.setData(random.randrange(1, 10), Qt.UserRole)
            item.setData(image_resource_name, Qt.UserRole + 1)
            item.setSizeHint(QtCore.QSize(100, 100))
            item.setSelectable(False)
            model.appendRow(item)

        self.list_model = model
        self.list_view = list_view

        # Show
        self.resize(800, 400)
        self.show()

    def queueUpdate(self, index):
        value = index.data(Qt.UserRole)
        self.list_model.setData(index, value - 0.0005, Qt.UserRole)

        self.list_view.update(index)


if __name__ == "__main__":
    palette = get_palette()
    app = QtWidgets.QApplication(sys.argv)
    app.setPalette(palette)
    example = None
    # example = ExampleToggleButton()
    example = ExampleFoldArea()
    # example = ExampleComboBoxItemDelegate()
    # example = ExampleHtmlItemDelegate()
    # example = ExampleImageItemDelegate()
    if not example:
        raise Exception("No example selected!")
    sys.exit(app.exec_())
