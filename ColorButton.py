from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt

from copy import copy


class ColorButton(QtWidgets.QPushButton):
    _highlight_color = QtGui.QColor.fromString("red")
    _highlight_alpha = 200
    _highlight_padding = 4
    _highlight_radius = 2

    _highlighted = True

    def __init__(self, label_text, *args, **kwargs):
        super().__init__(label_text, *args, **kwargs)

    def paintEvent(self, e):
        super().paintEvent(e)

        if not self._highlighted:
            return

        color = copy(self._highlight_color)

        if not self.isEnabled():
            color.setHsl(color.hue(), color.saturation() - 75, color.lightness() - 75)

        color.setAlpha(self._highlight_alpha)

        painter = QtGui.QPainter(self)
        pen = QtGui.QPen()
        pen.setColor(color)
        pen.setStyle(Qt.PenStyle.SolidLine)

        width = painter.device().width()
        height = painter.device().height()
        padding = self._highlight_padding
        radius = self._highlight_radius

        path = QtGui.QPainterPath()
        path.addRoundedRect(padding, padding, width - padding * 2, height - padding * 2, radius, radius)
        painter.setPen(pen)
        painter.drawPath(path)

        painter.end()

    def setHighlightColor(self, color):
        if isinstance(color, str):
            self._highlight_color = QtGui.QColor.fromString(color)
        elif isinstance(color, QtGui.QColor):
            self._highlight_color = color
        else:
            print("Error: Unrecognized color format")
        self.update()

    def setHighlightColorAlpha(self, alpha):
        self._highlight_alpha = alpha
        self.update()

    def setHighlightPadding(self, padding):
        self._highlight_padding = padding
        self.update()
    
    def setHighlightRadius(self, radius):
        self._highlight_radius = radius
        self.update()
    
    def setHighlighted(self, highlighted):
        self._highlighted = highlighted
        self.update()

    def highlighted(self):
        return self._highlighted
    
    def highlightColor(self):
        return self._highlightColor

    def highlightColorAlpha(self):
        return self._highlight_alpha

    def highlightPadding(self):
        return self._highlight_padding
    
    def highlightRadius(self):
        return self._highlight_radius
