from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
import pyqtgraph as pg
import wave
import numpy as np


class TrackerWidget(QtWidgets.QWidget):
    bg_color = QtGui.QColor.fromString("black")
    fg_color = QtGui.QColor.fromString("white")
    player = None
    audio_file_path = None
    n_visual_samples = 200_000

    # FIXME: Add functionality from the slider
    # FIXME: Add visual checkpoint functionality
    # FIXME: Handle visualizing multiple tracks

    def __init__(self, player, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.player = player

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

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.graph)

        self.setLayout(layout)

    def update_audio_data(self):
        wav_obj = wave.open(self.audio_file_path, "rb")
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

        self.times = times[indicies]
        self.amplitudes_l = l_channel[indicies]
        self.amplitudes_r = r_channel[indicies]

        self.plot_l.setData(self.times, self.amplitudes_l)
        self.plot_r.setData(self.times, self.amplitudes_r)

        self.paintEvent(None)

    def update_source(self):
        self.audio_file_path = self.player.source().path()
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
    
    def setVisualSampleCount(num_samples):
        self.n_visual_samples = num_samples
