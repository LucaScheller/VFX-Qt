from Qt import QtCore


def blend(value_a, value_b, factor):
    return value_b * factor + value_a * (1 - factor)

def fit(value, old_min, old_max, new_min, new_max):
    return new_min + (((value-old_min)/(old_max-old_min)) * (new_max-new_min))

def rect_scale_from_center(rect, scale_x, scale_y):
    rect_center = rect.center()
    rect_size = rect.size()
    rect.setSize(
        QtCore.QSize(rect_size.width() * scale_x, rect_size.height() * scale_y)
    )
    rect.translate(rect_center - rect.center())
    return rect
