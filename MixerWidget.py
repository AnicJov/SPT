from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt


class _Bar(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)

    def sizeHint(self):
        return QtCore.QSize(60, 160)

    def paintEvent(self, e):
        painter = QtGui.QPainter(self)
        brush = QtGui.QBrush()
        brush.setColor(QtGui.QColor("black"))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        rect = QtCore.QRect(0, 0, painter.device().width(), painter.device().height())
        painter.fillRect(rect, brush)


class MixerWidget(QtWidgets.QWidget):
    """
    Custom Qt Widget to show and control volume of and
    audio track, with option for muting and soloing the
    track.
    """

    def __init__(self, labelText="volume", steps=10, *args, **kwargs):
        super(MixerWidget, self).__init__(*args, **kwargs)

        layout = QtWidgets.QVBoxLayout()

        self._label = QtWidgets.QLabel(labelText)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._label)

        self._bar = _Bar()
        self._bar.setFixedSize(QtCore.QSize(60, 160))
        layout.addWidget(self._bar)

        buttons_layout = QtWidgets.QHBoxLayout()

        button_mute = QtWidgets.QPushButton("M")
        button_mute.setFixedSize(QtCore.QSize(20, 20))
        buttons_layout.addWidget(button_mute)
        button_solo = QtWidgets.QPushButton("S")
        button_solo.setFixedSize(QtCore.QSize(20, 20))
        buttons_layout.addWidget(button_solo)
        layout.addLayout(buttons_layout)
        
        self._dial = QtWidgets.QDial()
        self._dial.setFixedSize(QtCore.QSize(60, 60))
        layout.addWidget(self._dial)

        self.setLayout(layout)

    def sizeHint(self):
        return QtCore.QSize(60, 300)

    def setLabelText(newText):
        self._label.setLabelText(newText)
