import sys

from Qt import QtGui, QtCore, QtWidgets
from Qt.QtCore import Qt

from vfxQt.style import get_palette
from vfxQt.views import (
    ComboBoxItemDelegate,
    ComboBoxItemDelegateSourceMode,
    RowTableView,
)
from vfxQt.widgets import ToggleButton, ToggleButtonColorRole


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


if __name__ == "__main__":
    palette = get_palette()
    app = QtWidgets.QApplication(sys.argv)
    app.setPalette(palette)
    # example = ExampleToggleButton()
    # example = ExampleComboBoxItemDelegate()
    sys.exit(app.exec_())
