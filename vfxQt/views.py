import sys
from enum import Enum
from typing import Any

from Qt import QtCore, QtGui, QtSvg, QtWidgets
from Qt.QtCore import Qt

from vfxQt.utils import rect_scale_from_center

##############################
# Interface/Abstract
##############################


class StyledItemDelegate(QtWidgets.QStyledItemDelegate):
    def paint(
        self,
        painter: QtGui.QPainter,
        option: QtWidgets.QStyleOptionViewItem,
        index: QtCore.QModelIndex,
    ) -> None:
        """Boilerplate paint code.
        Args:
            painter (QtGui.QPainter): The painter.
            option (QtWidgets.QStyleOptionViewItem): The style option.
            index (QtCore.QModelIndex): The model index.
        """

        """ Base code to add custom paint code to.
        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        style_option = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(style_option, index)
        style = option.widget.style()
        style.drawControl(QtWidgets.QStyle.CE_ItemViewItem, style_option, painter)
        painter.restore()
        """

        """ Base code to debug drawing rect.
        painter.save()
        pen = QtGui.QPen(Qt.blue)
        pen.setStyle(Qt.DotLine)
        painter.setPen(pen)
        painter.drawRect(icon_rect)
        painter.restore()
        """

        super().paint(painter, option, index)


class MultiEditItemDelegate(StyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._multi_row_edit = False
        self._multi_column_edit = False

    def validateData(self, index: QtCore.QModelIndex, value: Any, role: int):
        """Validate the given value before writing it.
        Args:
            index (QtCore.QModelIndex): The model index.
            value (Any): The value.
            role (Any): The role.
        Returns:
            bool: Set the value if true, ignore the edit if false.
        """
        return True

    def setData(self, index: QtCore.QModelIndex, value: Any, role: int):
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

    def setMultiEditData(self, index: QtCore.QModelIndex, value: Any, role: int):
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
                if self.validateData(multi_index, value, role):
                    self.setData(multi_index, value, role)


##############################
# Delegates
##############################


class ComboBoxItemDelegateSourceMode(Enum):
    role = "role"
    func = "func"


class ComboBoxItemDelegate(MultiEditItemDelegate):
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

    def validateData(self, index: QtCore.QModelIndex, value: Any, role: int):
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

    def setData(self, index: QtCore.QModelIndex, value: Any, role: int):
        """Apply the edit to the model.
        Args:
            index (QtCore.QModelIndex): The model index.
            value (Any): The value.
            role (Any): The role.
        """
        if role == self._item_value_role:
            super().setData(index, value, role)
            # This propagates the label of the current item to the multi edit item.
            # As a condition of how this widget works, we expect each index to
            # have the same label for each value. Indices can still have varying
            # items, only the label must match the value per item.
            if role != Qt.DisplayRole:
                super().setData(index, self._items_value_label[value], Qt.DisplayRole)

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
        self.setMultiEditData(
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
        painter.save()

        text = index.data(Qt.DisplayRole)

        cb_style_option = QtWidgets.QStyleOptionComboBox()
        cb_style_option.rect = option.rect
        cb_style_option.currentText = text

        style = option.widget.style()
        style.drawComplexControl(QtWidgets.QStyle.CC_ComboBox, cb_style_option, painter)
        style.drawControl(QtWidgets.QStyle.CE_ComboBoxLabel, cb_style_option, painter)

        painter.restore()


class HtmlItemDelegate(MultiEditItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._html_doc = QtGui.QTextDocument(parent=self)
        self._html_doc.setDocumentMargin(0)
        self._html_doc_options = QtGui.QTextOption()
        self._html_doc_options.setWrapMode(
            self._html_doc_options.WrapAtWordBoundaryOrAnywhere
        )
        self._html_doc.setDefaultTextOption(self._html_doc_options)

        self._item_value_role = Qt.DisplayRole

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

    def paint(
        self,
        painter: QtGui.QPainter,
        option: QtWidgets.QStyleOptionViewItem,
        index: QtCore.QModelIndex,
    ) -> None:
        """Paint the item.
        Args:
            painter (QtGui.QPainter): The painter.
            option (QtWidgets.QStyleOptionViewItem): The style option.
            index (QtCore.QModelIndex): The model index.
        """

        painter.save()
        # style_option = QtWidgets.QStyleOptionViewItem(option)
        # self.initStyleOption(style_option, index)
        # style_option.text = ""
        # style = option.widget.style()
        # style.drawControl(QtWidgets.QStyle.CE_ItemViewItem, style_option, painter)

        rect = option.rect
        html = index.data(self._item_value_role)

        painter.translate(rect.topLeft())
        clip_rect = QtCore.QRectF(0.0, 0.0, float(rect.width()), float(rect.height()))
        self._html_doc.setHtml(html)
        self._html_doc.setTextWidth(rect.width())
        self._html_doc.setPageSize(rect.size())
        self._html_doc.drawContents(painter, clip_rect)

        painter.restore()


class ImageItemDelegate(MultiEditItemDelegate):
    repaintNeeded = QtCore.Signal(QtCore.QModelIndex, name="repaintNeeded")

    def __init__(self, parent=None):
        super().__init__(parent)

    def getImageCache(self):
        return self._image_cache

    def setImageCache(self, cache):
        self._image_cache = cache

    def paint(
        self,
        painter: QtGui.QPainter,
        option: QtWidgets.QStyleOptionViewItem,
        index: QtCore.QModelIndex,
    ) -> None:
        """Paint the item
        Args:
            painter (QtGui.QPainter): The painter.
            option (QtWidgets.QStyleOptionViewItem): The style option.
            index (QtCore.QModelIndex): The model index.
        """
        # super().paint(painter, option, index)
        if not self._image_cache:
            print(
                "No image cached specified, ignoring {} paint method.".format(
                    self.__class__.__name__
                )
            )
            return

        rect = option.rect

        display_time_out = index.data(Qt.UserRole)
        image_resource_name = index.data(Qt.UserRole + 1)
        image_resource = self._image_cache.getResource(image_resource_name, track=False)
        if image_resource:
            if isinstance(image_resource, QtSvg.QSvgRenderer):
                if display_time_out > 0:
                    painter.save()
                    painter.translate(rect.topLeft())
                    image_resource.setViewBox(option.rect)
                    image_resource.render(painter, option.rect)
                    painter.restore()
                    self.repaintNeeded.emit(index)
            elif isinstance(image_resource, QtGui.QPixmap):
                painter.save()
                painter.setRenderHint(QtGui.QPainter.Antialiasing)
                painter.drawPixmap(rect, image_resource)
                painter.restore()

        return
        image = ""

        painter.save()
        # style_option = QtWidgets.QStyleOptionViewItem(option)
        # self.initStyleOption(style_option, index)
        # style_option.text = ""
        # style = option.widget.style()
        # style.drawControl(QtWidgets.QStyle.CE_ItemViewItem, style_option, painter)

        rect = option.rect
        html = index.data(self._item_value_role)

        painter.translate(rect.topLeft())
        clip_rect = QtCore.QRectF(0.0, 0.0, float(rect.width()), float(rect.height()))
        self._html_doc.setHtml(html)
        self._html_doc.setTextWidth(rect.width())
        self._html_doc.setPageSize(rect.size())
        self._html_doc.drawContents(painter, clip_rect)

        painter.restore()


class TagItemColorRole:
    # Background
    background = 0
    backgroundDisabled = 1
    backgroundHover = 2
    backgroundSelected = 3
    backgroundChecked = 4
    # Border
    border = 5
    borderGradient = 6
    borderDisabled = 7
    borderHover = 8
    borderSelected = 9
    borderChecked = 10
    # Label
    label = 11
    labelDisabled = 12
    labelHover = 13
    labelSelected = 14
    labelChecked = 15


class TagItemIconRole:
    unchecked = 0
    checked = 1


class TagItemDelegate(MultiEditItemDelegate):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # Style
        self._font_point_size_percentage = 0.8

        self._border_pen = QtGui.QPen()
        self._border_pen.setStyle(Qt.PenStyle.SolidLine)
        self._border_width_percentage = 0.1

        self._bg_brush = QtGui.QBrush(Qt.BrushStyle.SolidPattern)

        self._icon_alignment = Qt.AlignLeft
        self._icon_scale = 0.9

        self._label_pen = QtGui.QPen()

        # Example Style
        # self._colors = {
        #     TagItemColorRole.background: QtGui.QColor(229, 239, 254),
        #     TagItemColorRole.backgroundDisabled: QtGui.QColor(229, 239, 254),
        #     TagItemColorRole.backgroundHover: QtGui.QColor(60, 125, 240),
        #     TagItemColorRole.backgroundSelected: QtGui.QColor(60, 125, 240),
        #     TagItemColorRole.backgroundChecked: QtGui.QColor(60, 125, 240),
        #     TagItemColorRole.border: QtGui.QColor(132, 173, 245),
        #     TagItemColorRole.borderGradient: None,
        #     TagItemColorRole.borderDisabled: QtGui.QColor(132, 173, 245),
        #     TagItemColorRole.borderHover: QtGui.QColor(255, 255, 255),
        #     TagItemColorRole.borderSelected: QtGui.QColor(132, 173, 245),
        #     TagItemColorRole.borderChecked: QtGui.QColor(132, 173, 245),
        #     TagItemColorRole.label: QtGui.QColor(64, 127, 240),
        #     TagItemColorRole.labelDisabled: QtGui.QColor(64, 127, 240),
        #     TagItemColorRole.labelHover: QtGui.QColor(229, 239, 254),
        #     TagItemColorRole.labelSelected: QtGui.QColor(229, 239, 254),
        #     TagItemColorRole.labelChecked: QtGui.QColor(229, 239, 254),
        # }

        self._colors = {
            TagItemColorRole.background: QtGui.QColor(235, 235, 235),
            TagItemColorRole.backgroundDisabled: QtGui.QColor(235, 235, 235),
            TagItemColorRole.backgroundHover: QtGui.QColor(235, 235, 235),
            TagItemColorRole.backgroundSelected: QtGui.QColor(0, 225, 255),
            TagItemColorRole.backgroundChecked: QtGui.QColor(0, 200, 255),
            TagItemColorRole.border: QtGui.QColor(235, 235, 235, 0),
            TagItemColorRole.borderGradient: None,
            TagItemColorRole.borderDisabled: QtGui.QColor(235, 235, 235, 0),
            TagItemColorRole.borderHover: QtGui.QColor(235, 0, 0, 255),
            TagItemColorRole.borderSelected: QtGui.QColor(235, 0, 0, 255),
            TagItemColorRole.borderChecked: QtGui.QColor(235, 0, 0, 255),
            TagItemColorRole.label: QtGui.QColor(125, 125, 125),
            TagItemColorRole.labelDisabled: QtGui.QColor(125, 125, 125),
            TagItemColorRole.labelHover: QtGui.QColor(255, 255, 255),
            TagItemColorRole.labelSelected: QtGui.QColor(255, 255, 255),
            TagItemColorRole.labelChecked: QtGui.QColor(255, 255, 255),
        }

        style = QtWidgets.QApplication.style()
        self._icons = {
            TagItemIconRole.unchecked: style.standardIcon(
                QtWidgets.QStyle.SP_DialogApplyButton
            ),
            TagItemIconRole.checked: style.standardIcon(
                QtWidgets.QStyle.SP_DialogCancelButton
            ),
        }

        border_gradient = QtGui.QLinearGradient(0, 0, 1, 0)
        border_gradient.setColorAt(0, QtGui.QColor.fromHsvF(0, 1, 1, 1.0))
        border_gradient.setColorAt(0.5, QtGui.QColor.fromHsvF(0.5, 1, 1, 1.0))
        border_gradient.setColorAt(1, QtGui.QColor.fromHsvF(0, 1, 1, 1.0))
        border_gradient = None

    def backgroundBrush(self) -> QtGui.QBrush:
        """Get the background brush.
        Returns:
            QtGui.QBrush: The pen.
        """
        return self._bg_brush

    def setBackgroundBrush(self, brush: QtGui.QBrush):
        """Set the background brush.
        Args:
            pen (QtGui.QBrush): The pen.
        """
        self._bg_brush = brush

    def borderPen(self) -> QtGui.QPen:
        """Get the border pen.
        Returns:
            QtGui.QPen: The pen.
        """
        return self._border_pen

    def setBorderPen(self, pen: QtGui.QPen):
        """Set the border pen.
        Args:
            pen (QtGui.QPen): The pen.
        """
        self._border_pen = pen

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
        self._border_width_percentage = min(max(0, value * 0.5), 0.5)

    def iconAlignment(self) -> Qt.Alignment:
        """Get the icon alignment.
        Returns:
            Qt.Alignment: The alignment.
        """
        return self._icon_alignment

    def setIconAlignment(self, alignment: Qt.Alignment):
        """Set the icon alignment.
        Args:
            value (Qt.Alignment): The alignment.
        """
        if alignment not in (Qt.AlignLeft, Qt.AlignRight):
            raise Exception(
                "Invalid alignment specified! Only 'Qt.AlignLeft'/'Qt.AlignRight' are allowed"
            )
        self._icon_alignment = alignment

    def iconScale(self) -> float:
        """Get the icon scale.
        Returns:
            float: The icon scale.
        """
        return self._icon_scale

    def setIconScale(self, value: float):
        """Set the icon scale.
        Args:
            value (float): The icon scale.
        """
        self._icon_scale = value

    def labelPen(self) -> QtGui.QPen:
        """Get the label pen.
        Returns:
            QtGui.QPen: The pen.
        """
        return self._label_pen

    def setLabelPen(self, pen: QtGui.QPen):
        """Set the label pen.
        Args:
            pen (QtGui.QPen): The pen.
        """
        self._label_pen = pen

    def color(self, role: int):
        """Get the tag colors.
        Args:
            role (int): The color role.
        Returns:
            QtGui.QColor: The color.
        """
        return self._colors.get(role, None)

    def setColor(self, role: int, color: QtGui.QColor) -> bool:
        """Set the tag color.
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

    def icon(self, role: int):
        """Get the tag icons.
        Args:
            role (int): The icon role.
        Returns:
            QtGui.QIcon: The icon.
        """
        return self._colors.get(role, None)

    def setIcon(self, role: int, icon: QtGui.QIcon) -> bool:
        """Set the tag icons.
        Args:
            role (int): The color role.
            color (QtGui.QIcon): The color.
        Returns:
            bool: The success state.
        """
        if role in self._icons:
            self._icons[role] = icon
            return True
        else:
            return False

    def getIconRect(self, index, rect) -> QtCore.QRect:
        """Get the icon rectangle.
        Args:
            index (QtCore.QModelIndex): The index.
            rect (QtCore.QRect): The rect.
        Returns:
            QtGui.QRect: The rectangle.
        """
        # icon = index.data(Qt.DecorationRole)
        # if not icon:
        #    return None

        bg_rect = rect
        border_width = min(bg_rect.size().toTuple()) * self._border_width_percentage
        inner_rect = bg_rect.adjusted(
            border_width,
            border_width,
            -border_width,
            -border_width,
        )

        text_rect_height = inner_rect.height()
        if self._icon_alignment == Qt.AlignLeft:
            icon_rect = QtCore.QRect(
                inner_rect.left(), inner_rect.top(), text_rect_height, text_rect_height
            )
        elif self._icon_alignment == Qt.AlignRight:
            icon_rect = QtCore.QRect(
                inner_rect.right() - text_rect_height,
                inner_rect.top(),
                text_rect_height,
                text_rect_height,
            )
        icon_rect = rect_scale_from_center(
            icon_rect, self._icon_scale, self._icon_scale
        )
        return icon_rect

    def sizeHint(
        self, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex
    ) -> QtCore.QSize:
        """Calculate the size based on the item text.
        Args:
            option (QtWidgets.QStyleOptionViewItem): The style option.
            index (QtCore.QModelIndex): The model index.
        """
        text = index.data(Qt.DisplayRole)

        # Height
        size_hint = index.data(Qt.SizeHintRole)
        size_height = size_hint.height() if size_hint else option.fontMetrics.height()
        # Width based on content
        font = option.font
        font.setPointSizeF(font.pointSizeF() * self._font_point_size_percentage)
        font_metrics = QtGui.QFontMetrics(font)
        size_width = font_metrics.horizontalAdvance(text)
        # Add padding for round border
        size_width += size_height

        size = QtCore.QSize(size_width, size_height)
        return size

    def paint(
        self,
        painter: QtGui.QPainter,
        option: QtWidgets.QStyleOptionViewItem,
        index: QtCore.QModelIndex,
    ) -> None:
        """Paint the tag item
        Args:
            painter (QtGui.QPainter): The painter.
            option (QtWidgets.QStyleOptionViewItem): The style option.
            index (QtCore.QModelIndex): The model index.
        """

        # Style
        is_checked = index.data(Qt.CheckStateRole) == Qt.Checked
        is_hover = option.state & QtWidgets.QStyle.State_MouseOver
        is_selected = option.state & QtWidgets.QStyle.State_Selected

        label_text = index.data(Qt.DisplayRole)
        icon = index.data(Qt.DecorationRole)

        if is_hover:
            bg_color = self._colors[TagItemColorRole.backgroundHover]
            border_color = self._colors[TagItemColorRole.borderHover]
            label_color = self._colors[TagItemColorRole.labelHover]
        elif is_selected:
            bg_color = self._colors[TagItemColorRole.backgroundSelected]
            border_color = self._colors[TagItemColorRole.borderSelected]
            label_color = self._colors[TagItemColorRole.labelSelected]
        elif is_checked:
            bg_color = self._colors[TagItemColorRole.backgroundChecked]
            border_color = self._colors[TagItemColorRole.borderChecked]
            label_color = self._colors[TagItemColorRole.labelChecked]
        else:
            bg_color = self._colors[TagItemColorRole.background]
            border_color = self._colors[TagItemColorRole.border]
            label_color = self._colors[TagItemColorRole.label]
        border_gradient = self._colors[TagItemColorRole.borderGradient]

        if is_checked:
            bg_color = self._colors[TagItemColorRole.backgroundChecked]
            label_color = self._colors[TagItemColorRole.labelChecked]

        if not icon:
            if is_checked:
                icon = self._icons[TagItemIconRole.checked]
            else:
                icon = self._icons[TagItemIconRole.unchecked]

        # Draw areas
        rect = option.rect

        bg_rect = rect
        bg_radius = bg_rect.height() * 0.5

        border_width = min(bg_rect.size().toTuple()) * self._border_width_percentage
        border_width_half = border_width * 0.5
        border_rect = bg_rect.adjusted(
            border_width_half, border_width_half, -border_width_half, -border_width_half
        )
        border_radius = border_rect.height() * 0.5

        text_rect = bg_rect.adjusted(
            border_width,
            border_width,
            -border_width,
            -border_width,
        )
        text_font_scale = 1.0

        icon_rect = self.getIconRect(index, rect)
        if icon:
            text_font_scale = text_rect.width()
            if self._icon_alignment == Qt.AlignLeft:
                text_rect.setLeft(icon_rect.right())
            elif self._icon_alignment == Qt.AlignRight:
                text_rect.setRight(icon_rect.left())
            text_font_scale = text_rect.width() / text_font_scale

        # Paint start
        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # Background
        painter.save()
        self._bg_brush.setColor(bg_color)
        bg_path = QtGui.QPainterPath()
        bg_path.addRoundedRect(bg_rect, bg_radius, bg_radius)
        painter.setBrush(self._bg_brush)
        painter.fillPath(bg_path, self._bg_brush)
        painter.restore()

        # Background border
        if border_width > 0:
            painter.save()
            border_path = QtGui.QPainterPath()
            border_path.addRoundedRect(border_rect, border_radius, border_radius)
            self._border_pen.setColor(border_color)
            self._border_pen.setWidth(border_width)
            painter.setPen(self._border_pen)
            painter.drawPath(border_path)
            painter.restore()
            if border_gradient:
                painter.save()
                if isinstance(border_gradient, QtGui.QLinearGradient):
                    border_rect_left = QtCore.QPoint(rect.left(), rect.center().y())
                    border_rect_right = QtCore.QPoint(rect.right(), rect.center().y())
                    border_gradient.setStart(border_rect_left)
                    border_gradient.setFinalStop(border_rect_right)
                    self._border_pen.setBrush(border_gradient)
                    painter.setPen(self._border_pen)
                    painter.drawPath(bg_path)
                painter.restore()

        # Icon
        if icon:
            painter.save()
            icon.paint(painter, icon_rect)
            painter.restore()

        # Label
        painter.save()
        font = painter.font()
        font.setPointSizeF(
            font.pointSizeF() * text_font_scale * self._font_point_size_percentage
        )
        self._label_pen.setColor(label_color)
        painter.setPen(self._label_pen)
        painter.setFont(font)
        painter.drawText(text_rect, Qt.AlignCenter, label_text)
        painter.restore()

        # Paint end
        painter.restore()


##############################
# Views
##############################


class RowTableView(QtWidgets.QTableView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Selection
        self.setSelectionBehavior(self.SelectRows)
        self.setSelectionMode(self.ExtendedSelection)

        # Edit
        self.setEditTriggers(self.AllEditTriggers)


class ListView(QtWidgets.QListView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def updateGeometry(self) -> None:
        self._

        return super().updateGeometry()
        """
        if(ui->listWidget->count()>0){
            float i = ui->listWidget->viewport()->width() /(330+ui->listWidget->spacing());
            float iw  = i*330;
            float r = ui->listWidget->viewport()->width()-iw;
            float even_dist_w = (r/i)-5;
            ui->listWidget->setGridSize(QSize(330+even_dist_w,162));
        }
        """


class TagView(QtWidgets.QListView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Selection
        self.setSelectionBehavior(self.SelectRows)
        self.setSelectionMode(self.ExtendedSelection)
        self.setMouseTracking(True)
        # Edit
        self.setEditTriggers(self.AllEditTriggers)
        # Layout
        self.setViewMode(QtWidgets.QListView.IconMode)
        self.setSpacing(5)
        # Delegate
        self._delegate = TagItemDelegate(self)
        self._delegate.setMultiRowEdit(True)
        self.setItemDelegate(self._delegate)
        self.setResizeMode(QtWidgets.QListView.Adjust)

    def getTagItemDelegate(self) -> TagItemDelegate:
        """Same as self.itemDelegate(), we alias this to make it
        clear that this is a specific delegate designed to work with
        the TagView list view.
        Returns:
            TagItemDelegate: The tag item delegate.
        """
        return self._delegate

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        delegate: TagItemDelegate = self.itemDelegate()
        if not isinstance(delegate, TagItemDelegate):
            return super().mouseReleaseEvent(event)

        mouse_pos = event.pos()
        index = self.indexAt(mouse_pos)
        if not index:
            return super().mouseReleaseEvent(event)

        rect = self.visualRect(index)

        icon_rect = delegate.getIconRect(index, rect)
        if not icon_rect:
            return super().mouseReleaseEvent(event)
        if icon_rect.contains(mouse_pos):
            model = index.model()
            check_state = model.data(index, Qt.CheckStateRole)
            check_state = Qt.Checked if check_state == Qt.Unchecked else Qt.Unchecked
            delegate.setMultiEditData(index, check_state, Qt.CheckStateRole)
            print("Checked", index, check_state)
            event.accept()
        else:
            return super().mouseReleaseEvent(event)