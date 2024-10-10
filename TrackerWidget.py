from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
import pyqtgraph as pg
import wave
import numpy as np


class _Tracker(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def paintEvent(self, e):
        painter = QtGui.QPainter(self)

        _pos = self.parent().position()
        _min = self.parent().minimum()
        _max = self.parent().maximum()
        _width = painter.device().width()
        _height = painter.device().height()

        bar_width = 2

        # Paint checkpoints
        checkpoints = self.parent().checkpoints
        for checkpoint in checkpoints.values():
            brush = QtGui.QBrush()
            color = checkpoint[1]
            color.setAlpha(150)
            brush.setColor(checkpoint[1])
            brush.setStyle(Qt.BrushStyle.SolidPattern)

            visual_position = int(np.interp(checkpoint[0], [_min, _max], [0, _width]))
            if visual_position == _width:
                visual_position -= 2
            if visual_position == _width - 1:
                visual_position -= 1
            
            rect = QtCore.QRect(visual_position, 0, bar_width, painter.device().height())
            painter.fillRect(rect, brush)

        # Paint current position
        brush = QtGui.QBrush()
        brush.setColor(QtGui.QColor.fromString("#f38ba8"))
        brush.setStyle(Qt.BrushStyle.SolidPattern)

        bar_width = 1
        triangle_size = 4

        visual_position = int(np.interp(_pos, [_min, _max], [0, _width]))

        if visual_position == _width - 1:
            visual_position -= 1

        rect = QtCore.QRect(visual_position, 0, bar_width, painter.device().height())

        triangle_top = QtGui.QPainterPath()
        triangle_top.moveTo(visual_position - triangle_size, 0)
        triangle_top.lineTo(visual_position + triangle_size, 0)
        triangle_top.lineTo(visual_position, triangle_size)
        triangle_top.lineTo(visual_position - triangle_size, 0)

        triangle_bot = QtGui.QPainterPath()
        triangle_bot.moveTo(visual_position - triangle_size, _height)
        triangle_bot.lineTo(visual_position + triangle_size, _height)
        triangle_bot.lineTo(visual_position, _height - triangle_size)
        triangle_bot.lineTo(visual_position - triangle_size, _height)

        painter.fillPath(triangle_top, brush)
        painter.fillPath(triangle_bot, brush)
        painter.fillRect(rect, brush)

        painter.end()


class TrackerWidget(QtWidgets.QWidget):
    bg_color = QtGui.QColor.fromString("black")
    fg_color = QtGui.QColor.fromString("white")
    players = None
    track_to_graph = -1 # Graph sum if -1
    audio_file_path = None
    n_visual_samples = 200_000

    _position = 0
    _minimum = 0
    _maximum = 100

    checkpoints = {}

    trackerMoved = QtCore.pyqtSignal(int)

    def __init__(self, players, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.players = players

        self.tracker = _Tracker()

        self.graph = pg.PlotWidget()

        self.graph.setAntialiasing(True)
        self.graph.setInteractive(False)
        self.graph.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.graph.getPlotItem().hideAxis("bottom")
        self.graph.getPlotItem().hideAxis("left")
        self.graph.getPlotItem().setClipToView(True)
        self.graph.getPlotItem().getViewBox().setDefaultPadding(0)

        self.pen = pg.mkPen(self.fg_color)
        self.pen_alt = pg.mkPen(self.fg_color)

        self.times = np.linspace(0, 1, num=2)
        self.amplitudes_l = np.zeros(2)
        self.amplitudes_r = np.zeros(2) 

        self.plot_l = self.graph.plot(self.times, self.amplitudes_l, pen=self.pen_alt, skipFiniteCheck=True)
        self.plot_r = self.graph.plot(self.times, self.amplitudes_l, pen=self.pen, skipFiniteCheck=True)

        layout = QtWidgets.QStackedLayout()
        layout.addWidget(self.graph)
        layout.addWidget(self.tracker)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setStackingMode(QtWidgets.QStackedLayout.StackingMode.StackAll)

        self.setLayout(layout)

    def _calculate_clicked_value(self, e):
        click_x = int(e.position().x())
        width = self.width()

        if click_x > width:
            click_x = width

        if click_x < 0:
            click_x = 0

        self.setTrackerPosition(int(np.interp(click_x, [0, width], [self._minimum, self._maximum])))
        self.trackerMoved.emit(self._position)

    def mouseMoveEvent(self, e):
        self._calculate_clicked_value(e)

    def mousePressEvent(self, e):
        self._calculate_clicked_value(e)

    def update_audio_data(self):
        n = [self.track_to_graph]
        if self.track_to_graph == -1:
            n = range(len(self.players))

        self.times = []
        self.amplitudes_l = []
        self.amplitudes_r = []
            
        for i in n:
            wav_obj = wave.open(self.players[i].source().path(), "rb")
            sample_rate = wav_obj.getframerate()
            n_samples = wav_obj.getnframes()
            t_audio = n_samples/sample_rate
            n_channels = wav_obj.getnchannels()
            signal_wave = wav_obj.readframes(n_samples)
            signal_array = np.frombuffer(signal_wave, dtype=np.int16)

            l_channel = signal_array[0::2]
            r_channel = signal_array[1::2]
            times = np.linspace(0, n_samples/sample_rate, num=n_samples)

            indicies = np.linspace(0, len(times) - 1, self.n_visual_samples, dtype=int)

            if (self.times is None) or (len(self.times) == 0):
                self.times = times[indicies]
                self.amplitudes_l = l_channel[indicies]
                self.amplitudes_r = r_channel[indicies]
            else:
                self.times = np.add(self.times, times[indicies])
                self.amplitudes_l = np.add(self.amplitudes_l, l_channel[indicies])
                self.amplitudes_r = np.add(self.amplitudes_r, r_channel[indicies])

        self.plot_l.setData(self.times, self.amplitudes_l)
        self.plot_r.setData(self.times, self.amplitudes_r)

        self.paintEvent(None)

    def update_source(self):
        self.update_audio_data()

    def setBackgroundColor(self, color):
        self.bg_color = color
        self.graph.setBackground(self.bg_color)
        self.graph.update()
        self.update()

    def setForegroundColor(self, color):
        self.fg_color = color
        self.pen.setColor(QtGui.QColor.fromRgb(self.fg_color.red(), self.fg_color.green(), self.fg_color.blue(), 40))
        alt_color = QtGui.QColor.fromHsl(self.fg_color.hue(), self.fg_color.saturation() - 30, self.fg_color.lightness() - 30)
        self.pen_alt.setColor(QtGui.QColor.fromRgb(alt_color.red(), alt_color.green(), alt_color.blue(), 40))
        self.graph.update()
        self.update()
        
    def setPlayer(self, player):
        self.player = player
    
    def setVisualSampleCount(self, num_samples):
        self.n_visual_samples = num_samples

    def setOrientation(self, orientation):
        print(f"Warning: TrackerWidget.setOrientation stub. Value {orientation}")

    def setMaximum(self, maximum):
        if maximum < self._minimum:
            print(f"Error: Tracker maximum can't be set to less than tracker minimum. {self.minimum} <= {maximum}")
            return

        if self._position > maximum:
            self._position = maximum

        self._maximum = maximum
        self.update()

    def setMinimum(self, minimum):
        if minimum > self.maximum:
            print(f"Error: Tracker minimum can't be set to more than tracker maximum. {minimum} <= {self.maximum}")
            return

        if self.position < minimum:
            self.position = minimum

        self.minimum = minimum
        self.tracker.update()

    def position(self):
        return self._position

    def setTrackerPosition(self, position):
        if position > self._maximum or position < self._minimum:
            print(f"Error: Tracker position set beyond bounds. {self._minimum} < {position} < {self._maximum}")
            return

        self._position = position
        self.tracker.update()

    def minimum(self):
        return self._minimum

    def maximum(self):
        return self._maximum
    
    def addCheckpoint(self, index, position, color):
        self.checkpoints[index] = (position, color)
        self.tracker.update()
