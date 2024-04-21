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
                if self.validateData(multi_index, value, role):
                    self.setData(multi_index, value, role)

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


class TagItemDelegate(StyledItemDelegate):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._font_point_size_percentage = 0.6

    def sizeHint(
        self, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex
    ) -> QtCore.QSize:
        label = index.data(Qt.DisplayRole)

        # Height
        size_hint = index.data(Qt.SizeHintRole)
        size_height = size_hint.height() if size_hint else option.fontMetrics.height()
        # Width based on content
        font = option.font
        font.setPointSizeF(font.pointSizeF() * self._font_point_size_percentage)
        font_metrics = QtGui.QFontMetrics(font)
        size_width = font_metrics.horizontalAdvance(label)
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
        """Boilerplate paint code.
        Args:
            painter (QtGui.QPainter): The painter.
            option (QtWidgets.QStyleOptionViewItem): The style option.
            index (QtCore.QModelIndex): The model index.
        """
        # painter.save()
        # style_option = QtWidgets.QStyleOptionViewItem(option)
        # self.initStyleOption(style_option, index)
        # style = option.widget.style()
        # style.drawControl(QtWidgets.QStyle.CE_ItemViewItem, style_option, painter)
        # painter.restore()

        # Style
        """
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
        brd_color = self._colors[ToggleButtonColorRole.border]
        """

        label_text = index.data(Qt.DisplayRole)
        label_color = QtGui.QColor.fromRgb(85, 143, 241, 255)
        label_color_hover = QtGui.QColor.fromRgb(255, 255, 255, 255)
        icon = index.data(Qt.DecorationRole)
        icon_alignment = Qt.AlignRight
        icon_scale = 0.75

        style = option.widget.style()
        icon = style.standardIcon(QtWidgets.QStyle.SP_MessageBoxInformation)

        bg_color = QtGui.QColor.fromRgb(229, 239, 254, 255)
        bg_gradient = QtGui.QColor.fromHsvF(0.0, 0, 0.85, 1.0)
        bg_color_hover = QtGui.QColor.fromRgb(60, 125, 240, 255)
        border_color = QtGui.QColor.fromHsvF(0.0, 1, 0.85, 1.0)
        border_gradient = None

        border_width_percentage = 0.1

        if option.state & QtWidgets.QStyle.State_MouseOver:
            bg_color = bg_color_hover
            label_color = label_color_hover

        # Draw areas
        rect = option.rect

        border_width = min(rect.size().toTuple()) * border_width_percentage
        border_width_half = border_width * 0.5

        bg_rect = rect.adjusted(
            border_width_half, border_width_half, -border_width_half, -border_width_half
        )
        bg_rect_height = bg_rect.height()
        bg_rect_height_half = bg_rect_height * 0.5
        bg_radius = bg_rect_height_half

        text_rect = bg_rect.adjusted(
            bg_rect_height_half,
            border_width_half,
            -bg_rect_height_half,
            -border_width_half,
        )
        text_font_scale = 1.0

        if icon:
            text_font_scale = text_rect.width()
            if icon_alignment == Qt.AlignLeft:
                text_rect.setLeft(text_rect.left() + bg_rect_height_half)
                icon_rect = QtCore.QRect(
                    bg_rect.left(), bg_rect.top(), bg_rect_height, bg_rect_height
                )
            elif icon_alignment == Qt.AlignRight:
                text_rect.setRight(text_rect.right() - bg_rect_height_half)
                icon_rect = QtCore.QRect(
                    bg_rect.right() - bg_rect_height,
                    bg_rect.top(),
                    bg_rect_height,
                    bg_rect_height,
                )
            text_font_scale = text_rect.width() / text_font_scale
            icon_rect = rect_scale_from_center(icon_rect, icon_scale, icon_scale)

        # Paint start
        painter.save()
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
        pen = QtGui.QPen(label_color)
        painter.setPen(pen)
        painter.setFont(font)
        painter.drawText(text_rect, Qt.AlignCenter, label_text)
        painter.restore()

        if False:
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
        delegate = TagItemDelegate(self)
        self.setItemDelegate(delegate)
        self.setResizeMode(QtWidgets.QListView.Adjust)
