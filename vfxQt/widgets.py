import sys
from Qt import QtWidgets, QtGui, QtCore
from Qt.QtCore import Qt

from vfxQt.utils import fit, blend


class ToggleButtonColorRole:
    backgroundOn = 0
    backgroundOff = 1
    backgroundDisabled = 2
    toggleOn = 3
    toggleOff = 4
    toggleDisabled = 5
    border = 6

class ToggleButton(QtWidgets.QSlider):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # Base
        self.setSingleStep(100)
        self.setTickInterval(100)

        # State
        self._toggle_state = False
        self._toggle_ani_state = 0.0
        self._toggle_ani_prop = QtCore.QPropertyAnimation(self, b"toggleAnimationValue")
        self._toggle_ani_prop.setEasingCurve(QtCore.QEasingCurve.Type.OutBounce)
        # This drives the handle selection area,
        # disable the paintEvent to see the effect
        self._stylesheet_template_horizontal = """
            QSlider::groove:horizontal {
                border-radius: None;
                height: 100%;
                margin: 0px;
            }
            QSlider::handle:horizontal {
                background-color: rgb(85, 170, 255);
                border: none;
                width: ||width||px;
                height: 100%;
            }
        """
        self._stylesheet_template_vertical = """
            QSlider::groove:vertical {
                border-radius: None;
                width: 100%;
                margin: 0px;
            }
            QSlider::handle:vertical {
                background-color: rgb(85, 170, 255);
                border: none;
                width: 100%;
                height: ||height||px;
            }
        """

        # Style
        self._colors = {
            ToggleButtonColorRole.backgroundOn: QtGui.QColor.fromHsvF(0.3, 1, 0.85, 1.0),
            ToggleButtonColorRole.backgroundOff: QtGui.QColor.fromHsvF(0.3, 0, 0.3, 1.0),
            ToggleButtonColorRole.backgroundDisabled: QtGui.QColor.fromHsvF(0.3, 0, 0.2, 1.0),
            ToggleButtonColorRole.toggleOn: QtGui.QColor.fromHsvF(0, 0, 0.95, 1.0),
            ToggleButtonColorRole.toggleOff: QtGui.QColor.fromHsvF(0, 0, 0.6, 1.0),
            ToggleButtonColorRole.toggleDisabled: QtGui.QColor.fromHsvF(0, 0, 0.5, 1.0),
            ToggleButtonColorRole.border: QtGui.QColor.fromHsvF(0, 0, 0.95, 1.0)
        }
        self._toggle_radius_percentage = 0.9
        self._toggle_time = 0.25
        self._border_width = 0
 
        """ Palette
        palette = QtWidgets.QApplication.instance().palette()
        self._colors.update({
            ToggleButtonColorRole.backgroundOn: palette.color(palette.Highlight),
            ToggleButtonColorRole.backgroundOff: palette.color(palette.Mid),
            ToggleButtonColorRole.toggleOn: palette.color(palette.Light),
            ToggleButtonColorRole.toggleOff: palette.color(palette.Midlight),
        })
        """

        # Animation
        self.toggleValueChanged.connect(self.onToggleAnimationTrigger)

    def toggleRadiusPercentage(self) -> float:
        """Get the toggle radius percentage.
        Returns:
            float: The percentage.
        """
        return self._toggle_radius_percentage

    def setToggleRadiusPercentage(self, value: float):
        """Set the toggled radius percentage.
        Args:
            value (float): The percentage.
        """
        self._toggle_radius_percentage = max(0, min(value, 1))

    def toggleAnimationTime(self) -> float:
        """Get the toggle animation blend time.
        Returns:
            float: The time in seconds.
        """
        return self._toggle_time

    def setToggleAnimationTime(self, value: float):
        """Set the toggled animation blend time.
        Args:
            value (float): The time in seconds.
        """
        self._toggle_time = value

    def borderWidth(self) -> int:
        """Get the button border width.
        Returns:
            int: The width.
        """
        return self._border_width

    def setBorderWidth(self, value: int):
        """Set the button border width
        Args:
            value (int): The width.
        """
        self._border_width = value


    def color(self, role: int):
        """Get the toggle colors.
        Args:
            role (int): The color role.
        Returns:
            QtGui.QColor: The color.
        """
        return self._colors.get(role, None)

    def setColor(self, role: int, color: QtGui.QColor):
        """Configure the toggle colors.
        Args:
            role (int): The color role.
            color (QtGui.QColor): The color.
        Returns:
            bool: The success state.
        """
        if role in self._colors:
            self._colors[role] = color
            return True
        else:
            return False
 
    def getToggleAnimationValue(self):
        """Get the toggle animation value.
        Returns:
            int: The value.
        """
        return self._toggle_ani_state

    def setToggleAnimationValue(self, value):
        """Set the toggle animation value.
        Args:
            int: The value.
        """
        self._toggle_ani_state = value
        self.setValue(value)
        self.repaint()

    def onToggleAnimationTrigger(self):
        """Trigger the toggle animation."""
        value = self.toggled()
        self._toggle_ani_prop.setStartValue(self.value())
        self._toggle_ani_prop.setEndValue(value * 100.0)
        self._toggle_ani_prop.setDuration(self._toggle_time * 1000.0)
        self._toggle_ani_prop.start()

    def toggled(self) -> bool:
        """Get the toggled state.
        Returns:
            bool: The toggle state.
        """
        return bool(self._toggle_state)

    def setToggled(self, value: bool):
        """Set the toggled state.
        Args:
            value (bool): The value.
        """
        value = True if value >= 0.5 else False
        if value != self._toggle_state:
            self._toggle_state = value
            self.toggleValueChanged.emit(value)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        super().resizeEvent(event)
        # Orientation
        size = event.size()
        if size.width() > size.height():
            stylesheet = self._stylesheet_template_horizontal.replace(
                "||width||", str(self.height())
            )
            self.setOrientation(Qt.Horizontal)
        else:
            stylesheet = self._stylesheet_template_vertical.replace(
                "||height||", str(self.width())
            )
            self.setOrientation(Qt.Vertical)
        # Stylesheet (drives handle selection area)
        self.setStyleSheet(stylesheet)

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        # Disable scroll
        pass

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        """The mouse press event.
        Args:
            event(QtGui.QMouseEvent): The event.
        """
        style_option = QtWidgets.QStyleOptionSlider()
        self.initStyleOption(style_option)
        pressed_ctrl = self.style().hitTestComplexControl(
            QtWidgets.QStyle.CC_Slider, style_option, event.pos(), self
        )
        if pressed_ctrl != QtWidgets.QStyle.SC_SliderGroove:
            # Only trigger event for direct handle selections.
            super().mousePressEvent(event)
        self._toggle_ani_prop.stop()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        """The mouse release event.
        Args:
            event(QtGui.QMouseEvent): The event.
        """
        # super().mouseReleaseEvent(event)
        rect = self.rect()
        pos = event.localPos()
        if self.orientation() == Qt.Orientation.Horizontal:
            value = pos.x() > (rect.width() * 0.5)
        else:
            value = pos.y() < (rect.height() * 0.5)

        toggled = self.toggled()
        if value != toggled:
            # Handle value changed animation
            self.setToggled(value)
        else:
            # Handle animation back to current value
            self.onToggleAnimationTrigger()

    def paintEvent(self, event):
        """Paint the slider toggle and background.
        Args:
            event(QtGui.QPaintEvent): The event.
        """
        # super().paintEvent(event)

        # Value
        value = self.value() / 100.0

        # Style

        if self.isEnabled():
            tgl_on_hsv = self._colors[ToggleButtonColorRole.toggleOn].getHsv()
            tgl_off_hsv = self._colors[ToggleButtonColorRole.toggleOff].getHsv()
            tgl_color = QtGui.QColor.fromHsv(
                blend(tgl_off_hsv[0], tgl_on_hsv[0], value),
                blend(tgl_off_hsv[1], tgl_on_hsv[1], value),
                blend(tgl_off_hsv[2], tgl_on_hsv[2], value),
            )
            bg_on_hsv = self._colors[ToggleButtonColorRole.backgroundOn].getHsv()
            bg_off_hsv = self._colors[ToggleButtonColorRole.backgroundOff].getHsv()
            bg_color = QtGui.QColor.fromHsv(
                blend(bg_off_hsv[0], bg_on_hsv[0], value),
                blend(bg_off_hsv[1], bg_on_hsv[1], value),
                blend(bg_off_hsv[2], bg_on_hsv[2], value),
            )
        else:
            tgl_color = self._colors[ToggleButtonColorRole.toggleDisabled]
            bg_color = self._colors[ToggleButtonColorRole.backgroundDisabled]
        brd_color = self._colors[ToggleButtonColorRole.border]

        # Size
        shrink = 50
        widget_rect = self.rect()
        roi_rect = widget_rect.adjusted(5, 5, -5, -5)
        redraw_rect = event.rect()
        region_rect = event.region().boundingRect()

        orientation = self.orientation()
        length = roi_rect.width()
        radius = roi_rect.height() * 0.5
        slider_line = QtCore.QLineF(radius, radius, length - radius, radius)
        if orientation == Qt.Orientation.Vertical:
            value = 1.0 - value
            length = roi_rect.height()
            radius = roi_rect.width() * 0.5
            slider_line = QtCore.QLineF(radius, radius, radius, length - radius)
        slider_line.translate(roi_rect.topLeft())
        toggle_center = slider_line.pointAt(value)
        toggle_rect = QtCore.QRect(
            toggle_center.x() - radius, toggle_center.y() - radius, radius, radius
        )

        # Paint start
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # Background
        painter.save()
        painter.setPen(Qt.NoPen)
        brush = QtGui.QBrush(bg_color)
        painter.setBrush(brush)
        path = QtGui.QPainterPath()
        path.addRoundedRect(roi_rect, radius, radius)
        painter.fillPath(path, brush)
        painter.restore()

        # Background border
        painter.save()
        pen = QtGui.QPen(brd_color)
        pen.setWidth(self._border_width)
        painter.setPen(pen)
        painter.drawPath(path)
        painter.restore()

        # Toggle
        painter.save()
        brush = QtGui.QBrush(tgl_color)
        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(
            toggle_center,
            radius * self._toggle_radius_percentage,
            radius * self._toggle_radius_percentage,
        )
        painter.restore()

        # Paint end
        painter.end()

    # Signals
    toggleValueChanged = QtCore.Signal(bool)

    # Properties
    toggleAnimationValue = QtCore.Property(
        float, getToggleAnimationValue, setToggleAnimationValue
    )


class Example(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        center_widget = QtWidgets.QWidget()
        self.setCentralWidget(center_widget)

        layout = QtWidgets.QVBoxLayout(center_widget)
        center_widget.setLayout(layout)

        self.toggle_horizontal_button = ToggleButton()
        self.toggle_horizontal_button.setFixedSize(200, 50)
        layout.addWidget(self.toggle_horizontal_button)

        self.toggle_vertical_button = ToggleButton()
        self.toggle_vertical_button.setFixedSize(50, 100)
        self.toggle_vertical_button.setBorderWidth(5)
        self.toggle_vertical_button.setColor(ToggleButtonColorRole.border, Qt.black)
        layout.addWidget(self.toggle_vertical_button)

        self.toggle_disabled_button = ToggleButton()
        self.toggle_disabled_button.setFixedSize(100, 50)
        self.toggle_disabled_button.setEnabled(False)
        layout.addWidget(self.toggle_disabled_button)

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
    app = QtWidgets.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
