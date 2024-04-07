import sys

from Qt import QtGui, QtWidgets
from Qt.QtCore import Qt

from vfxQt.widgets import ToggleButton, ToggleButtonColorRole
from vfxQt.style import get_palette

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


if __name__ == "__main__":
    palette = get_palette()
    app = QtWidgets.QApplication(sys.argv)
    app.setPalette(palette)
    ex = ExampleToggleButton()
    sys.exit(app.exec_())
