from Qt import QtCore, QtGui, QtWidgets
from Qt.QtCore import Qt

from vfxQt.utils import blend
from vfxQt.views import TagView, TagItemDelegate


class ToggleButtonColorRole:
    backgroundOn = 0
    backgroundOff = 1
    backgroundDisabled = 2
    toggleOn = 3
    toggleOff = 4
    toggleDisabled = 5
    toggleGradient = 6
    border = 7


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
            ToggleButtonColorRole.backgroundOn: QtGui.QColor.fromHsvF(
                0.3, 1, 0.85, 1.0
            ),
            ToggleButtonColorRole.backgroundOff: QtGui.QColor.fromHsvF(
                0.3, 0, 0.3, 1.0
            ),
            ToggleButtonColorRole.backgroundDisabled: QtGui.QColor.fromHsvF(
                0.3, 0, 0.25, 1.0
            ),
            ToggleButtonColorRole.toggleOn: QtGui.QColor.fromHsvF(0, 0, 0.95, 1.0),
            ToggleButtonColorRole.toggleOff: QtGui.QColor.fromHsvF(0, 0, 0.6, 1.0),
            ToggleButtonColorRole.toggleDisabled: QtGui.QColor.fromHsvF(0, 0, 0.5, 1.0),
            ToggleButtonColorRole.toggleGradient: None,
            ToggleButtonColorRole.border: QtGui.QColor.fromHsvF(0, 0, 0.95, 1.0),
        }
        self._toggle_radius_percentage = 0.9
        self._toggle_time = 0.25 * 1000.0
        self._background_radius_percentage = 1.0
        self._border_width_percentage = 0

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
            float: The time in milliseconds.
        """
        return self._toggle_time

    def setToggleAnimationTime(self, value: float):
        """Set the toggled animation blend time.
        Args:
            value (float): The time in milliseconds.
        """
        self._toggle_time = value

    def backgroundRadiusPercentage(self) -> float:
        """Get the toggle radius percentage.
        Returns:
            float: The percentage.
        """
        return self._background_radius_percentage

    def setBackgroundRadiusPercentage(self, value: float):
        """Set the toggled radius percentage.
        Args:
            value (float): The percentage.
        """
        self._background_radius_percentage = max(0, min(value, 1))

    def borderWidthPercentage(self) -> float:
        """Get the button border width.
        Returns:
            float: The width.
        """
        return self._border_width_percentage

    def setBorderWidthPercentage(self, value: float):
        """Set the button border width
        Args:
            value (float): The width.
        """
        self._border_width_percentage = value

    def color(self, role: int):
        """Get the toggle color.
        Args:
            role (int): The color role.
        Returns:
            QtGui.QColor: The color.
        """
        return self._colors.get(role, None)

    def setColor(self, role: int, color: QtGui.QColor):
        """Set the toggle color.
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
        self.update()

    def onToggleAnimationTrigger(self, value):
        """Trigger the toggle animation."""
        self._toggle_ani_prop.setStartValue(self.value())
        self._toggle_ani_prop.setEndValue(value * 100.0)
        self._toggle_ani_prop.setDuration(self._toggle_time)
        self._toggle_ani_prop.start()

    def toggled(self) -> bool:
        """Get the toggled state.
        Returns:
            bool: The toggle state.
        """
        return bool(self._toggle_state)

    def setToggled(self, value: bool):
        """Set the toggled state.
        We also emit a
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
            self.onToggleAnimationTrigger(value)

    def keyReleaseEvent(self, event: QtGui.QKeyEvent):
        """The keyboard release event.
        Args:
            event(QtGui.QKeyEvent): The event.
        """
        # We interpret any key event as a toggle.
        self.setToggled(1 - self.toggled())

    def paintEvent(self, event):
        """Paint the slider toggle and background.
        Args:
            event(QtGui.QPaintEvent): The event.
        """
        # super().paintEvent(event)

        # Value
        value = self.value() / 99.0

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
        tgl_gradient = self._colors[ToggleButtonColorRole.toggleGradient]
        border_color = self._colors[ToggleButtonColorRole.border]

        # Size
        widget_rect = self.rect()
        # redraw_rect = event.rect()
        # region_rect = event.region().boundingRect()

        border_width = min(widget_rect.size().toTuple()) * self._border_width_percentage
        border_width_half = border_width * 0.5
        roi_rect = widget_rect.adjusted(
            border_width_half, border_width_half, -border_width_half, -border_width_half
        )
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
        tgl_center = slider_line.pointAt(value)
        tgl_rect = QtCore.QRect(
            tgl_center.x() - radius, tgl_center.y() - radius, radius * 2, radius * 2
        )
        bg_shrink = min(roi_rect.size().toTuple()) * (1-self._background_radius_percentage) * 0.5
        bg_rect = roi_rect.adjusted(bg_shrink, bg_shrink, -bg_shrink, -bg_shrink) 
        bg_radius = self._background_radius_percentage * radius

        # Paint start
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # Background
        painter.save()
        painter.setPen(Qt.NoPen)
        brush = QtGui.QBrush(bg_color)
        painter.setBrush(brush)
        bg_path = QtGui.QPainterPath()
        bg_path.addRoundedRect(bg_rect, bg_radius, bg_radius)
        painter.fillPath(bg_path, brush)
        painter.restore()

        # Background border
        if border_width > 0:
            painter.save()
            pen = QtGui.QPen(border_color)
            pen.setWidth(border_width)
            painter.setPen(pen)
            painter.drawPath(bg_path)
            painter.restore()

        # Toggle
        painter.save()
        brush = QtGui.QBrush(tgl_color)
        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(
            tgl_center,
            radius * self._toggle_radius_percentage,
            radius * self._toggle_radius_percentage,
        )
        painter.restore()
        if tgl_gradient:
            painter.save()
            painter.setPen(Qt.NoPen)
            if isinstance(tgl_gradient, QtGui.QLinearGradient):
                tgl_top_center_pt = QtCore.QPoint(tgl_rect.left(), tgl_rect.top())
                tgl_bottom_center_pt = QtCore.QPoint(tgl_rect.left(), tgl_rect.bottom())
                tgl_gradient.setStart(tgl_top_center_pt)
                tgl_gradient.setFinalStop(tgl_bottom_center_pt)
                brush = QtGui.QBrush(tgl_gradient)
                painter.setBrush(brush)
                painter.drawEllipse(
                    tgl_center,
                    radius * self._toggle_radius_percentage,
                    radius * self._toggle_radius_percentage,
                )
            elif isinstance(tgl_gradient, QtGui.QRadialGradient):
                tgl_gradient.setCenter(tgl_center)
                tgl_gradient.setFocalPoint(tgl_center)
                tgl_gradient.setRadius(radius)
                brush = QtGui.QBrush(tgl_gradient)
                painter.setBrush(brush)
                painter.drawEllipse(
                    tgl_center,
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


class FoldArea(QtWidgets.QScrollArea):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # Layout (This is user overridable)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

        # Style
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.setMaximumHeight(0)
        self.setMinimumHeight(0)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)

        # State
        self._toggle_state = False
        self._toggle_ani_state = 0.0
        self._toggle_ani_prop = QtCore.QPropertyAnimation(self, b"maximumHeight")
        self._toggle_time = 0.25 * 1000.0
        self._toggle_ani_easing_curve = QtCore.QEasingCurve.Type.Linear

        # Animation
        self.toggleValueChanged.connect(self.onToggleAnimationTrigger)

    def toggleAnimationTime(self) -> float:
        """Get the toggle animation blend time.
        Returns:
            float: The time in milliseconds.
        """
        return self._toggle_time

    def setToggleAnimationTime(self, value: float):
        """Set the toggled animation blend time.
        Args:
            value (float): The time in milliseconds.
        """
        self._toggle_time = value

    def toggleAnimationEasingCurve(self) -> QtCore.QEasingCurve.Type:
        """Get the toggled animation easing curve type.
        Returns:
            QtCore.QEasingCurve.Type: The easing curve type.
        """
        return self._toggle_ani_easing_curve

    def setToggleAnimationEasingCurve(self, value: QtCore.QEasingCurve.Type):
        """Set the toggled animation easing curve type.
        Args:
            value (QtCore.QEasingCurve.Type): The easing curve type.
        """
        self._toggle_ani_easing_curve = value

    def onToggleAnimationTrigger(self, value):
        """Trigger the toggle animation."""
        content_height = self.layout().sizeHint().height()
        ani_value_start = 0 if value else content_height
        ani_value_end = content_height if value else 0
        self._toggle_ani_prop.setStartValue(ani_value_start)
        self._toggle_ani_prop.setEndValue(ani_value_end)
        self._toggle_ani_prop.setDuration(self._toggle_time)
        self._toggle_ani_prop.setEasingCurve(self._toggle_ani_easing_curve)
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

    # Signals
    toggleValueChanged = QtCore.Signal(bool)


class FoldSection(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        layout = QtWidgets.QGridLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self._section_toggle_button = QtWidgets.QToolButton(self)
        self._section_toggle_button.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self._section_toggle_button.setAutoRaise(True)
        self._section_toggle_button.setArrowType(Qt.RightArrow)
        self._section_toggle_button.setCheckable(True)
        self._section_toggle_button.setStyleSheet("QToolButton {border: none;}")
        layout.addWidget(self._section_toggle_button, 0, 0, 1, 1, Qt.AlignLeft)

        self._section_line = QtWidgets.QFrame(self)
        self._section_line.setFrameShape(QtWidgets.QFrame.HLine)
        self._section_line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self._section_line.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum
        )
        layout.addWidget(self._section_line, 0, 1, 1, 1)

        self._content_area = FoldArea(self)
        self._content_area.setToggled(False)
        layout.addWidget(self._content_area, 1, 0, 1, 3)

        # State
        self._section_custom_toggle_button = None
        self._section_custom_toggle_button_toggle_signal_name = None
        self._section_custom_toggle_button_toggle_state_method_name = None
        self._toggle_state = False

        # Animation
        self._section_toggle_button.clicked.connect(self.onToggled)
        self.toggleValueChanged.connect(self.onToggleAnimationTrigger)

    def getFoldArea(self):
        """Get the fold area.
        Returns:
            FoldArea: The fold area.
        """
        return self._content_area

    def getFoldAreaLayout(self):
        """Get the fold area layout.
        Returns:
            QtWidgets.QLayout: The layout.
        """
        return self._content_area.layout()

    def getCustomToggleButton(self):
        """Get the custom toggle button (if set).
        Returns:
            QtWidgets.QWidget: The widget (or None).
        """
        return self._section_custom_toggle_button

    def setCustomToggleButton(
        self,
        widget: QtWidgets.QWidget,
        toggle_signal_name: str,
        toggle_checked_state_method_name: str,
    ):
        """Set a the custom toggle button.
        Args:
            widget (QtWidgets.QWidget): The widget.
            toggle_signal_name (str): The signal name that changes on check state change.
            toggle_checked_state_method_name (str): The method to query the check state from.
        """
        # Disable native button
        self._section_toggle_button.clicked.disconnect(self.onToggled)
        self._section_toggle_button.hide()

        # Store state
        self._section_custom_toggle_button = widget
        self._section_custom_toggle_button_toggle_signal_name = toggle_signal_name
        self._section_custom_toggle_button_toggle_state_method_name = (
            toggle_checked_state_method_name
        )

        # Add
        self._section_custom_toggle_button.setParent(self)
        getattr(
            self._section_custom_toggle_button,
            self._section_custom_toggle_button_toggle_signal_name,
        ).connect(self.onToggled)
        self.layout().addWidget(
            self._section_custom_toggle_button, 0, 0, 1, 1, Qt.AlignLeft
        )

    def clearCustomToggleButton(self):
        """Remove the custom toggle button."""
        if self._section_custom_toggle_button is None:
            return
        # Remove
        self.layout().addWidget(self._section_toggle_button, 0, 0, 1, 1, Qt.AlignLeft)
        getattr(
            self._section_custom_toggle_button,
            self._section_custom_toggle_button_toggle_signal_name,
        ).disconnect(self.onToggled)
        self._section_custom_toggle_button.setParent(None)
        del self._section_custom_toggle_button

        # Clear state
        self._section_custom_toggle_button = None
        self._section_custom_toggle_button_toggle_signal_name = None
        self._section_custom_toggle_button_toggle_state_method_name = None

        # Enable native button
        self._section_toggle_button.setChecked(self._toggle_state)
        self._section_toggle_button.clicked.connect(self.onToggled)
        self._section_toggle_button.show()

    def onToggled(self):
        if self._section_custom_toggle_button is None:
            value = self._section_toggle_button.isChecked()
        else:
            value = getattr(
                self._section_custom_toggle_button,
                self._section_custom_toggle_button_toggle_state_method_name,
            )()
        self.setToggled(value)

    def onToggleAnimationTrigger(self, value):
        """Trigger the toggle animation."""
        self._section_toggle_button.setArrowType(
            Qt.DownArrow if value else Qt.RightArrow
        )
        self._content_area.setToggled(value)

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

    # Signals
    toggleValueChanged = QtCore.Signal(bool)


class TagListWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # Layout
        self.setLayout(QtWidgets.QVBoxLayout())

        self._model = QtGui.QStandardItemModel(parent=self)
        self._view = TagView(parent=self)
        self._view.setModel(self._model)
        self._delegate = self._view.itemDelegate()

        self.layout().addWidget(self._view)

    def getModel(self) -> TagItemDelegate:
        """Same as self._model, we alias this to make it
        easier to publicly access the model to customize it.
        Returns:
            TagItemDelegate: The tag item delegate.
        """
        return self._model

    def getView(self) -> TagItemDelegate:
        """Same as self._model, we alias this to make it
        easier to publicly access the model to customize it.
        Returns:
            TagItemDelegate: The tag item delegate.
        """
        return self._view

    def getItemDelegate(self) -> TagItemDelegate:
        """Same as self._view.itemDelegate(), we alias this to make it
        easier to publicly access the delegate to customize it.
        Returns:
            TagItemDelegate: The tag item delegate.
        """
        return self._delegate


if __name__ == "__main__":
    pass