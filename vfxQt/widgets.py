import sys
from Qt import QtWidgets, QtGui, QtCore
from Qt.QtCore import Qt

from vfxQt.utils import fit, blend


class ToggleButton(QtWidgets.QSlider):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.setStyleSheet(
            "QSlider::handle { background: black; width: 25px; }"
        )

        # State
        self._toggle_state = False
        self._toggle_ani_state = 0.0
        self._toggle_ani_prop = QtCore.QPropertyAnimation(self, b"toggleAnimationValue")
        self._toggle_ani_prop.setEasingCurve(QtCore.QEasingCurve.Type.OutBounce)

        # Style
        self.toggle_radius_factor = 0.9
        self.toggle_time = 0.25
        self.toggle_on_color = QtGui.QColor.fromHsvF(0,0,0.95, 1.0)
        self.toggle_off_color = QtGui.QColor.fromHsvF(0,0,0.6, 1.0)
        self.border_on_color = QtGui.QColor.fromHsvF(0,0,0.95, 1.0)
        self.border_off_color = QtGui.QColor.fromHsvF(0,0,0.6, 1.0)
        self.background_on_color = QtGui.QColor.fromHsvF(0.3,1,0.85, 1.0)
        self.background_off_color = QtGui.QColor.fromHsvF(0.3,0,0.3, 1.0)

        self.setOrientation(Qt.Horizontal)

        # Animation
        #self.setCheckable(True)
        #self.clicked.connect(self.onValueChanged)

    def getToggleAnimationValue(self):
        return self._toggle_ani_state

    def setToggleAnimationValue(self, value):
        self._toggle_ani_state = value
        self.setValue(value)
        self.update()

    def onValueChanged(self, value):
        #self._toggle_ani_timer.setInterval()
        #self._toggle_ani_timer.start()
        self._toggle_state = True if value > 50.0 else False
        self._toggle_ani_prop.setStartValue(100-value)
        self._toggle_ani_prop.setEndValue(value)
        self._toggle_ani_prop.setDuration(self.toggle_time * 1000.0)
        #self._toggle_ani_prop.start()

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

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseReleaseEvent(event)

        rect = self.rect()
        pos = event.pos()
        if self.orientation() == Qt.Orientation.Horizontal:
            value = pos.x() > (rect.width() * 0.5)
        else:
            value = pos.x() > (rect.height() * 0.5)
        self.setToggled(value)
        print(value)


    def paintEvent(self, event):
        """Paint the slider toggle and background.
        Args:
            event(QtGui.QPaintEvent): The paint event.
        """
        super().paintEvent(event)
        return
        # Value
        value = self.getToggleAnimationValue() / 100.0

        # Style
        tgl_on_hsv = self.toggle_on_color.getHsv()
        tgl_off_hsv = self.toggle_off_color.getHsv()
        tgl_color = QtGui.QColor.fromHsv(
            blend(tgl_off_hsv[0], tgl_on_hsv[0], value),
            blend(tgl_off_hsv[1], tgl_on_hsv[1], value),
            blend(tgl_off_hsv[2], tgl_on_hsv[2], value)
        )

        brd_on_hsv = self.border_on_color.getHsv()
        brd_off_hsv = self.border_off_color.getHsv()
        brd_color = QtGui.QColor.fromHsv(
            blend(brd_off_hsv[0], brd_on_hsv[0], value),
            blend(brd_off_hsv[1], brd_on_hsv[1], value),
            blend(brd_off_hsv[2], brd_on_hsv[2], value)
        )

        bg_on_hsv = self.background_on_color.getHsv()
        bg_off_hsv = self.background_off_color.getHsv()
        bg_color = QtGui.QColor.fromHsv(
            blend(bg_off_hsv[0], bg_on_hsv[0], value),
            blend(bg_off_hsv[1], bg_on_hsv[1], value),
            blend(bg_off_hsv[2], bg_on_hsv[2], value)
        )

        # Size
        widget_rect = self.rect()
        redraw_rect = event.rect()
        region_rect = event.region().boundingRect()

        orientation = self.orientation()
        length = widget_rect.width()
        radius = widget_rect.height() * 0.5
        slider_line = QtCore.QLineF(radius, radius, length - radius, radius)
        if orientation == Qt.Orientation.Vertical:
            length = widget_rect.height()
            radius = widget_rect.width() * 0.5
            slider_line = QtCore.QLineF(radius, radius, radius, length - radius)
        toggle_center = slider_line.pointAt(value)
        toggle_rect = QtCore.QRect(toggle_center.x() - radius,
                                   toggle_center.y() - radius,
                                   radius, radius)

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
        path.addRoundedRect(widget_rect, radius, radius)
        painter.fillPath(path, brush)
        painter.restore()
                
        # Background border
        painter.save()
        pen = QtGui.QPen(brd_color)
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawPath(path);    
        painter.restore()

        # Toggle
        painter.save()
        brush = QtGui.QBrush(tgl_color)
        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(toggle_center,
                            radius * self.toggle_radius_factor,
                            radius * self.toggle_radius_factor)
        painter.restore()

        # Paint end
        painter.end() 

    # Signals
    toggleValueChanged = QtCore.Signal(bool)

    # Properties
    toggleAnimationValue = QtCore.Property(float, getToggleAnimationValue, setToggleAnimationValue)


class Example(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        mySlider = ToggleButton(self)
        mySlider.setFixedSize(200, 100)

        self.setWindowTitle("Checkbox Example")
        self.show()

    def changeValue(self, value):
        print(value)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())