from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt

from ColorButton import ColorButton


class _Bar(QtWidgets.QWidget):
    clicked_value = QtCore.pyqtSignal(int)

    def __init__(self, steps, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)

        if isinstance(steps, list):
            # List of colors
            self.n_steps = len(steps)
            self.steps = steps
        elif isinstance(steps, int):
            # Number of bars to draw
            self.n_steps = steps
            self.steps = ['mediumpurple'] * steps
        else:
            raise TypeError("Steps must be of type list or int")

        self._bar_solid_percent = 0.8
        self._background_color = QtGui.QColor("window")
        self._padding = 4

    def paintEvent(self, e):
        painter = QtGui.QPainter(self)

        brush = QtGui.QBrush()
        brush.setColor(self._background_color)
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        rect = QtCore.QRect(0, 0, painter.device().width(), painter.device().height())
        painter.fillRect(rect, brush)

        # Get current state of dial
        dial = self.parent()._dial
        vmin, vmax = dial.minimum(), dial.maximum()
        value = dial.value()

        padding = 5

        # Define canvas
        d_height = painter.device().height() - (padding * 2)
        d_width = painter.device().width() - (padding * 2)
        
        # Draw bars
        step_size = int(d_height / self.n_steps)
        bar_height = int(step_size * self._bar_solid_percent)
        bar_spacer = int(step_size * (1 - self._bar_solid_percent) / 2)

        pc = (value - vmin) / (vmax - vmin)
        n_steps_to_draw = int(pc * self.n_steps)

        for n in range(n_steps_to_draw):
            brush.setColor(QtGui.QColor(self.steps[n]))
            if self.parent().muted:
                brush.setColor(QtGui.QColor("#45475a"))

            rect = QtCore.QRect(
                padding,
                padding + d_height - ((n + 1) * step_size) + bar_spacer,
                d_width,
                bar_height
            )
            painter.fillRect(rect, brush)
        
        painter.end()

    def sizeHint(self):
        return QtCore.QSize(60, 160)

    def _trigger_refresh(self):
        self.update()

    def _calculate_clicked_value(self, e):
        # FIXME: This behavior is buggy, fix it.
        dial = self.parent()._dial
        vmin, vmax = dial.minimum(), dial.maximum()
        d_height = self.size().height()
        step_size = d_height / self.n_steps
        click_y = int(e.position().y() / d_height * self.n_steps)

        pc = int(self.n_steps - click_y)
        value = int(vmin + pc * (vmax / self.n_steps))
        self.clicked_value.emit(value)

    def mouseMoveEvent(self, e):
        self._calculate_clicked_value(e)

    def mousePressEvent(self, e):
        self._calculate_clicked_value(e)


class MixerWidget(QtWidgets.QWidget):
    """
    Custom Qt Widget to show and control volume of and
    audio track, with option for muting and soloing the
    track.
    """
    
    colorChanged = QtCore.pyqtSignal()
    volumeChanged = QtCore.pyqtSignal((int, str))
    trackMuted = QtCore.pyqtSignal((bool, str))
    trackSoloed = QtCore.pyqtSignal((bool, str))

    label = "volume"
    muted = False
    soloed = False

    def __init__(self, labelText="volume", steps=10, *args, **kwargs):
        super(MixerWidget, self).__init__(*args, **kwargs)

        self.label = labelText

        layout = QtWidgets.QVBoxLayout()

        self._label = QtWidgets.QLabel(labelText)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._label)

        self._bar = _Bar(steps)
        self._bar.setFixedSize(QtCore.QSize(60, 160))
        layout.addWidget(self._bar)

        buttons_layout = QtWidgets.QHBoxLayout()

        self.button_mute = ColorButton("M")
        self.button_mute.setFixedSize(QtCore.QSize(20, 20))
        self.button_mute.setHighlightColor("#f38ba8")
        self.button_mute.setHighlightPadding(3)
        self.button_mute.setHighlighted(False)
        buttons_layout.addWidget(self.button_mute)
        self.button_solo = ColorButton("S")
        self.button_solo.setFixedSize(QtCore.QSize(20, 20))
        self.button_solo.setHighlightColor("#94e2d5")
        self.button_solo.setHighlightPadding(3)
        self.button_solo.setHighlighted(False)
        buttons_layout.addWidget(self.button_solo)
        layout.addLayout(buttons_layout)
        
        self._dial = QtWidgets.QDial()
        self._dial.setFixedSize(QtCore.QSize(60, 60))
        self._dial.setNotchesVisible(True)
        self._dial.setWrapping(False)
        self._dial.valueChanged.connect(self._bar._trigger_refresh)
        self._dial.setValue(99)
        layout.addWidget(self._dial)

        self.setLayout(layout)

        self._bar.clicked_value.connect(self._dial.setValue)
        self._dial.valueChanged.connect(self._value_changed)
        self.button_mute.pressed.connect(self._toggle_mute)
        self.button_solo.pressed.connect(self._toggle_solo)

    def _toggle_mute(self):
        if self.muted == False:
            self.muted = True
            self.button_mute.setHighlighted(True)
            self.trackMuted.emit(True, self.label)
        else:
            self.muted = False
            self.button_mute.setHighlighted(False)
            self.trackMuted.emit(False, self.label)
        self._bar.update()

    def _toggle_solo(self):
        if self.soloed == False:
            self.soloed = True
            self.trackSoloed.emit(True, self.label)
        else:
            self.soloed = False
            self.trackSoloed.emit(False, self.label)
        
    def _value_changed(self, value):
        self.volumeChanged.emit(value, self.label)

    def sizeHint(self):
        return QtCore.QSize(60, 300)

    def setLabelText(newText):
        self._label.setLabelText(newText)
        self.label = newText

    def setColor(self, color):
        self._bar.steps = [color] * self._bar.n_steps
        self._bar.update()

    def setColors(self, colors):
        self._bar.n_steps = len(colors)
        self._bar.steps = colors
        self._bar.update()

    def setBarPadding(self, padding):
        self._bar._padding = int(padding)
        self._bar.update()
    
    def setBarSolidPercent(self, percent):
        self._bar._bar_solid_percent = float(percent)
        self._bar.update()
    
    def setBackgroundColor(self, color):
        self._bar._background_color = color
        self._bar.update()
    
    def value(self):
        return self._dial.value()
