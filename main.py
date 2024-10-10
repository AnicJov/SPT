import sys
from os import path
import math
from datetime import datetime

from PyQt6.QtCore import Qt, QSize, QUrl
from PyQt6.QtGui import QIcon, QPalette, QColor, QFont
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QPushButton,
    QSlider,
    QSpacerItem,
    QSizePolicy,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QLayout,
    QGridLayout,
    QFileDialog,
)

import demucs.separate

from MixerWidget import MixerWidget
from TrackerWidget import TrackerWidget


class MainWindow(QMainWindow):
    window_title = "SPT - Song Practice Tool"

    media_filename = ""
    media_separated_dir = ""
    media_state = "inactive"
    media_duration = 0
    media_position = 0

    master_track_volume = 1

    checkpoints = {}
    checkpoint_colors = ["#a6e3a1", "#89b4fa", "#f9e2af", "#f5c2e7"]

    def __init__(self):
        super().__init__()

        # General settings
        self.setWindowTitle(self.window_title)
        self.setWindowIcon(QIcon("res/spt_icon.webp"))
        self.setMinimumSize(QSize(400, 550))

        # Layout definitions
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignJustify)

        self.song_select_section = QHBoxLayout()
        self.song_select_section.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.tracker_section = QVBoxLayout()
        self.tracker_labels_section = QHBoxLayout()
        self.tracker_labels_section.setAlignment(Qt.AlignmentFlag.AlignLeading)
        self.pos_ctrl_section = QHBoxLayout()
        self.checkpoint_section = QGridLayout()
        self.checkpoint_section.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.media_ctrl_section = QHBoxLayout()

        self.speed_ctrl_section = QVBoxLayout()
        self.speed_fine_section = QHBoxLayout()
        self.speed_coarse_section = QHBoxLayout()

        self.mixer_section = QHBoxLayout()
        self.mixer_section.setAlignment(Qt.AlignmentFlag.AlignJustify)

        self.footer_section = QHBoxLayout()

        # Widget definitions
        self.song_select_button = QPushButton(QIcon.fromTheme("document-open"), "Browse...")
        self.song_select_button.setFixedSize(QSize(100, 30))

        self.song_select_label = QLabel("No song selected")
        self.song_select_label.setFont(QFont("sans-serif", italic=True))

        self.tracker = QSlider()
        self.tracker.setOrientation(Qt.Orientation.Horizontal)
        self.tracker.setFixedHeight(50)


        self.tracker_current_label = QLabel("00:00.00")
        self.tracker_label_spacer = QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.tracker_duration_label = QLabel("00:00.00")

        self.pos_ctrl_section.addLayout(self.checkpoint_section)
        self.pos_ctrl_section.addLayout(self.media_ctrl_section)

        self.checkpoint_button_size = QSize(30, 30)
        self.checkpoint1_set_button = QPushButton("S1")
        self.checkpoint1_set_button.setFixedSize(self.checkpoint_button_size)
        self.checkpoint1_ld_button = QPushButton("L1")
        self.checkpoint1_ld_button.setFixedSize(self.checkpoint_button_size)
        self.checkpoint1_ld_button.setDisabled(True)
        self.checkpoint2_set_button = QPushButton("S2")
        self.checkpoint2_set_button.setFixedSize(self.checkpoint_button_size)
        self.checkpoint2_ld_button = QPushButton("L2")
        self.checkpoint2_ld_button.setFixedSize(self.checkpoint_button_size)
        self.checkpoint2_ld_button.setDisabled(True)
        self.checkpoint3_set_button = QPushButton("S3")
        self.checkpoint3_set_button.setFixedSize(self.checkpoint_button_size)
        self.checkpoint3_ld_button = QPushButton("L3")
        self.checkpoint3_ld_button.setFixedSize(self.checkpoint_button_size)
        self.checkpoint3_ld_button.setDisabled(True)
        self.checkpoint4_set_button = QPushButton("S4")
        self.checkpoint4_set_button.setFixedSize(self.checkpoint_button_size)
        self.checkpoint4_ld_button = QPushButton("L4")
        self.checkpoint4_ld_button.setFixedSize(self.checkpoint_button_size)
        self.checkpoint4_ld_button.setDisabled(True)

        self.media_button_size = QSize(40, 40)
        self.media_ctrl_ld_back = QPushButton(QIcon.fromTheme("media-skip-backward"), "")
        self.media_ctrl_ld_back.setFixedSize(self.media_button_size)
        self.media_ctrl_back = QPushButton(QIcon.fromTheme("media-seek-backward"), "")
        self.media_ctrl_back.setFixedSize(self.media_button_size)
        self.media_ctrl_play_pause = QPushButton(QIcon.fromTheme("media-play"), "")
        self.media_ctrl_play_pause.setFixedSize(self.media_button_size)
        self.media_ctrl_fwd = QPushButton(QIcon.fromTheme("media-seek-forward"), "")
        self.media_ctrl_fwd.setFixedSize(self.media_button_size)
        self.media_ctrl_ld_fwd = QPushButton(QIcon.fromTheme("media-skip-forward"), "")
        self.media_ctrl_ld_fwd.setFixedSize(self.media_button_size)

        self.speed_label = QLabel("Playback speed ")
        self.min_speed_label = QLabel("x0")
        self.max_speed_label = QLabel("x2")
        self.speed_ctrl_slider = QSlider(Qt.Orientation.Horizontal)
        
        speed_ctrl_button_size = QSize(40, 25)
        self.speed_ctrl_button_p5 = QPushButton("x0.5")
        self.speed_ctrl_button_p75 = QPushButton("x0.75")
        self.speed_ctrl_button_p8 = QPushButton("x0.8")
        self.speed_ctrl_button_p9 = QPushButton("x0.9")
        self.speed_ctrl_button_1 = QPushButton("x1")
        self.speed_ctrl_button_1p1 = QPushButton("x1.1")
        self.speed_ctrl_button_1p2 = QPushButton("x1.2")
        self.speed_ctrl_button_1p3 = QPushButton("x1.3")
        self.speed_ctrl_button_1p5 = QPushButton("x1.5")
        self.speed_ctrl_button_p5.setFixedSize(speed_ctrl_button_size)
        self.speed_ctrl_button_p75.setFixedSize(speed_ctrl_button_size)
        self.speed_ctrl_button_p8.setFixedSize(speed_ctrl_button_size)
        self.speed_ctrl_button_p9.setFixedSize(speed_ctrl_button_size)
        self.speed_ctrl_button_1.setFixedSize(speed_ctrl_button_size)
        self.speed_ctrl_button_1p1.setFixedSize(speed_ctrl_button_size)
        self.speed_ctrl_button_1p2.setFixedSize(speed_ctrl_button_size)
        self.speed_ctrl_button_1p3.setFixedSize(speed_ctrl_button_size)
        self.speed_ctrl_button_1p5.setFixedSize(speed_ctrl_button_size)

        palette = self.palette()
        self.mixer_drums = MixerWidget(labelText="Drums")
        self.mixer_drums.setBackgroundColor(palette.base().color())
        self.mixer_drums.setColor(palette.highlight().color())
        self.mixer_bass = MixerWidget(labelText="Bass")
        self.mixer_bass.setBackgroundColor(palette.base().color())
        self.mixer_bass.setColor(palette.highlight().color())
        self.mixer_vocals = MixerWidget(labelText="Vocals")
        self.mixer_vocals.setBackgroundColor(palette.base().color())
        self.mixer_vocals.setColor(palette.highlight().color())
        self.mixer_other = MixerWidget(labelText="Other")
        self.mixer_other.setBackgroundColor(palette.base().color())
        self.mixer_other.setColor(palette.highlight().color())
        self.mixer_master = MixerWidget(labelText="Master")
        self.mixer_master.setBackgroundColor(palette.base().color())
        self.mixer_master.setColor(palette.highlight().color())

        self.settings_button = QPushButton(QIcon.fromTheme("document-properties"), "")
        self.settings_button.setFixedSize(QSize(30, 30))
        self.footer_spacer = QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.notation_view_button = QPushButton(QIcon.fromTheme("go-next"), "Notation View")
        self.notation_view_button.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.notation_view_button.setFixedSize(QSize(160, 30))

        # Layout placement
        self.main_layout.addLayout(self.song_select_section)
        self.main_layout.addLayout(self.tracker_section)
        self.main_layout.addLayout(self.pos_ctrl_section)
        self.main_layout.addLayout(self.speed_ctrl_section)
        self.main_layout.addLayout(self.mixer_section)
        self.main_layout.addLayout(self.footer_section)

        # Widget placement
        self.song_select_section.addWidget(self.song_select_button)
        self.song_select_section.addWidget(self.song_select_label)

        self.tracker_section.addWidget(self.tracker)
        self.tracker_section.addLayout(self.tracker_labels_section)
        self.tracker_labels_section.addWidget(self.tracker_current_label)
        self.tracker_labels_section.addSpacerItem(self.tracker_label_spacer)
        self.tracker_labels_section.addWidget(self.tracker_duration_label)

        self.checkpoint_section.addWidget(self.checkpoint1_set_button, 0, 0)
        self.checkpoint_section.addWidget(self.checkpoint1_ld_button, 1, 0)
        self.checkpoint_section.addWidget(self.checkpoint2_set_button, 0, 1)
        self.checkpoint_section.addWidget(self.checkpoint2_ld_button, 1, 1)
        self.checkpoint_section.addWidget(self.checkpoint3_set_button, 0, 2)
        self.checkpoint_section.addWidget(self.checkpoint3_ld_button, 1, 2)
        self.checkpoint_section.addWidget(self.checkpoint4_set_button, 0, 3)
        self.checkpoint_section.addWidget(self.checkpoint4_ld_button, 1, 3)

        self.media_ctrl_section.addWidget(self.media_ctrl_ld_back)
        self.media_ctrl_section.addWidget(self.media_ctrl_back)
        self.media_ctrl_section.addWidget(self.media_ctrl_play_pause)
        self.media_ctrl_section.addWidget(self.media_ctrl_fwd)
        self.media_ctrl_section.addWidget(self.media_ctrl_ld_fwd)

        self.speed_ctrl_section.addLayout(self.speed_fine_section)
        self.speed_ctrl_section.addLayout(self.speed_coarse_section)
        self.speed_fine_section.addWidget(self.speed_label)
        self.speed_fine_section.addWidget(self.min_speed_label)
        self.speed_fine_section.addWidget(self.speed_ctrl_slider)
        self.speed_fine_section.addWidget(self.max_speed_label)
        self.speed_coarse_section.addWidget(self.speed_ctrl_button_p5)
        self.speed_coarse_section.addWidget(self.speed_ctrl_button_p75)
        self.speed_coarse_section.addWidget(self.speed_ctrl_button_p8)
        self.speed_coarse_section.addWidget(self.speed_ctrl_button_p9)
        self.speed_coarse_section.addWidget(self.speed_ctrl_button_1)
        self.speed_coarse_section.addWidget(self.speed_ctrl_button_1p1)
        self.speed_coarse_section.addWidget(self.speed_ctrl_button_1p2)
        self.speed_coarse_section.addWidget(self.speed_ctrl_button_1p3)
        self.speed_coarse_section.addWidget(self.speed_ctrl_button_1p5)

        self.mixer_section.addWidget(self.mixer_drums)
        self.mixer_section.addWidget(self.mixer_bass)
        self.mixer_section.addWidget(self.mixer_vocals)
        self.mixer_section.addWidget(self.mixer_other)
        self.mixer_section.addWidget(self.mixer_master)

        self.footer_section.addWidget(self.settings_button)
        self.footer_section.addSpacerItem(self.footer_spacer)
        self.footer_section.addWidget(self.notation_view_button)

        self.main_widget = QWidget()
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        # File selection functionality
        self.song_select_button.clicked.connect(self.open_file)
        
        # Audio functionality
        self.player_drums = QMediaPlayer()
        self.player_bass = QMediaPlayer()
        self.player_vocals = QMediaPlayer()
        self.player_other = QMediaPlayer()

        self.audio_output_drums = QAudioOutput()
        self.audio_output_bass = QAudioOutput()
        self.audio_output_vocals = QAudioOutput()
        self.audio_output_other = QAudioOutput()

        self.player_drums.setAudioOutput(self.audio_output_drums)
        self.player_bass.setAudioOutput(self.audio_output_bass)
        self.player_vocals.setAudioOutput(self.audio_output_vocals)
        self.player_other.setAudioOutput(self.audio_output_other)

        self.audio_output_drums.setVolume(100)
        self.audio_output_bass.setVolume(100)
        self.audio_output_vocals.setVolume(100)
        self.audio_output_other.setVolume(100)

        self.mixer_drums.volumeChanged.connect(self.volume_changed)
        self.mixer_drums.trackMuted.connect(self.track_muted)
        # self.mixer_drums.trackSoloed.connect(self.track_soloed)
        self.mixer_bass.volumeChanged.connect(self.volume_changed)
        self.mixer_bass.trackMuted.connect(self.track_muted)
        # self.mixer_bass.trackSoloed.connect(self.track_soloed)
        self.mixer_vocals.volumeChanged.connect(self.volume_changed)
        self.mixer_vocals.trackMuted.connect(self.track_muted)
        # self.mixer_vocals.trackSoloed.connect(self.track_soloed)
        self.mixer_other.volumeChanged.connect(self.volume_changed)
        self.mixer_other.trackMuted.connect(self.track_muted)
        # self.mixer_other.trackSoloed.connect(self.track_soloed)
        self.mixer_master.volumeChanged.connect(self.volume_changed)
        self.mixer_master.trackMuted.connect(self.track_muted)

        self.media_ctrl_play_pause.clicked.connect(self.play_pause)
        self.media_ctrl_back.clicked.connect(self.skip_backward)
        self.media_ctrl_fwd.clicked.connect(self.skip_forward)

        self.player_other.durationChanged.connect(self.update_duration)
        self.player_other.positionChanged.connect(self.update_current_position)
        self.player_other.playbackStateChanged.connect(self.update_playback_state)

        # Speed control functionality
        self.speed_ctrl_slider.setValue(50)
        self.speed_ctrl_slider.valueChanged.connect(self.update_playback_speed)
        self.speed_ctrl_button_p5.clicked.connect(lambda: self.set_playback_speed(0.5))
        self.speed_ctrl_button_p75.clicked.connect(lambda: self.set_playback_speed(0.75))
        self.speed_ctrl_button_p8.clicked.connect(lambda: self.set_playback_speed(0.8))
        self.speed_ctrl_button_p9.clicked.connect(lambda: self.set_playback_speed(0.9))
        self.speed_ctrl_button_1.clicked.connect(lambda: self.set_playback_speed(1))
        self.speed_ctrl_button_1p1.clicked.connect(lambda: self.set_playback_speed(1.1))
        self.speed_ctrl_button_1p2.clicked.connect(lambda: self.set_playback_speed(1.2))
        self.speed_ctrl_button_1p3.clicked.connect(lambda: self.set_playback_speed(1.3))
        self.speed_ctrl_button_1p5.clicked.connect(lambda: self.set_playback_speed(1.5))

        # Checkpoint functionality
        self.checkpoint1_set_button.clicked.connect(lambda: self.set_checkpoint(0, self.player_other.position()))
        self.checkpoint2_set_button.clicked.connect(lambda: self.set_checkpoint(1, self.player_other.position()))
        self.checkpoint3_set_button.clicked.connect(lambda: self.set_checkpoint(2, self.player_other.position()))
        self.checkpoint4_set_button.clicked.connect(lambda: self.set_checkpoint(3, self.player_other.position()))

        self.checkpoint1_ld_button.clicked.connect(lambda: self.load_checkpoint(0))
        self.checkpoint2_ld_button.clicked.connect(lambda: self.load_checkpoint(1))
        self.checkpoint3_ld_button.clicked.connect(lambda: self.load_checkpoint(2))
        self.checkpoint4_ld_button.clicked.connect(lambda: self.load_checkpoint(3))

        self.media_ctrl_ld_back.clicked.connect(self.load_previous_checkpoint)
        self.media_ctrl_ld_fwd.clicked.connect(self.load_next_checkpoint)

        # Tracker functionality
        self.new_tracker = TrackerWidget(self.player_other)
        self.new_tracker.setBackgroundColor(self.palette().base().color())
        self.new_tracker.setForegroundColor(self.palette().highlight().color())

        self.player_other.sourceChanged.connect(self.new_tracker.update_source)
        self.tracker_section.addWidget(self.new_tracker)

        self.new_tracker.trackerMoved.connect(self.change_position)

    def open_file(self):
        file_name = QFileDialog.getOpenFileName(self, caption="Open Audio File", filter="Audio Files (*.mp3 *.wav *.ogg *.opus *.m4a)")

        if not path.isfile(file_name[0]):
            print("Error: Could not open file")
            return

        if len(file_name[0]) < 30:
            self.song_select_label.setText(file_name[0])
        else:
            self.song_select_label.setText(path.basename(file_name[0]))

        self.media_filename = file_name[0]
    
        self.song_select_label.setFont(QFont("sans-serif", False))

        # Separate audio
        # FIXME: Don't do this here, use a worker
        model = "htdemucs_ft"
        self.media_separated_dir = f"separated/{model}/{path.splitext(path.basename(file_name[0]))[0]}/"
        if not path.exists(self.media_separated_dir):
            demucs.separate.main(["-n", model, self.media_filename])

        self.player_drums.setSource(QUrl.fromLocalFile(self.media_separated_dir + "drums.wav"))
        self.player_bass.setSource(QUrl.fromLocalFile(self.media_separated_dir + "bass.wav"))
        self.player_vocals.setSource(QUrl.fromLocalFile(self.media_separated_dir + "vocals.wav"))
        self.player_other.setSource(QUrl.fromLocalFile(self.media_separated_dir + "other.wav"))


    def load_previous_checkpoint(self):
        current_pos = self.player_other.position()
        min_diff = math.inf
        prev_checkpoint = None

        for checkpoint in self.checkpoints.values():
            if checkpoint >= current_pos:
                continue
            if (current_pos - checkpoint) < min_diff:
                min_diff = (current_pos - checkpoint)
                prev_checkpoint = checkpoint

        if prev_checkpoint is not None:
            self.player_drums.setPosition(prev_checkpoint)
            self.player_bass.setPosition(prev_checkpoint)
            self.player_vocals.setPosition(prev_checkpoint)
            self.player_other.setPosition(prev_checkpoint)
        else:
            self.player_drums.setPosition(0)
            self.player_bass.setPosition(0)
            self.player_vocals.setPosition(0)
            self.player_other.setPosition(0)

    def load_next_checkpoint(self):
        current_pos = self.player_other.position()
        min_diff = math.inf
        next_checkpoint = None

        for checkpoint in self.checkpoints.values():
            if checkpoint <= current_pos:
                continue
            if (checkpoint - current_pos) < min_diff:
                min_diff = (checkpoint - current_pos)
                next_checkpoint = checkpoint
        
        if next_checkpoint is not None:
            self.player_drums.setPosition(next_checkpoint)
            self.player_bass.setPosition(next_checkpoint)
            self.player_vocals.setPosition(next_checkpoint)
            self.player_other.setPosition(next_checkpoint)
        else:
            self.player_drums.setPosition(self.media_duration)
            self.player_bass.setPosition(self.media_duration)
            self.player_vocals.setPosition(self.media_duration)
            self.player_other.setPosition(self.media_duration)

    def load_checkpoint(self, index):
        if self.checkpoints[index] is not None:
            self.player_drums.setPosition(self.checkpoints[index])
            self.player_bass.setPosition(self.checkpoints[index])
            self.player_vocals.setPosition(self.checkpoints[index])
            self.player_other.setPosition(self.checkpoints[index])

    def set_checkpoint(self, index, position):
        self.checkpoints[index] = position
        self.new_tracker.addCheckpoint(index, position, QColor.fromString(self.checkpoint_colors[index]))
        match index:
            case 0:
                self.checkpoint1_ld_button.setEnabled(True)
            case 1:
                self.checkpoint2_ld_button.setEnabled(True)
            case 2:
                self.checkpoint3_ld_button.setEnabled(True)
            case 3:
                self.checkpoint4_ld_button.setEnabled(True)

    def set_playback_speed(self, speed):
        self.speed_ctrl_slider.setValue(self._interpolate_slider_value(speed))

    def update_playback_speed(self):
        slider_value = self.speed_ctrl_slider.value()
        speed = self._interpolate_playback_speed(slider_value)

        self.player_drums.setPlaybackRate(speed)
        self.player_bass.setPlaybackRate(speed)
        self.player_vocals.setPlaybackRate(speed)
        self.player_other.setPlaybackRate(speed)

    def skip_forward(self):
        new_position = self.player_other.position() + 5000
        if new_position >= self.media_duration:
            self.player_drums.setPosition(self.media_duration)
            self.player_bass.setPosition(self.media_duration)
            self.player_vocals.setPosition(self.media_duration)
            self.player_other.setPosition(self.media_duration)
        else:
            self.player_drums.setPosition(new_position)
            self.player_bass.setPosition(new_position)
            self.player_vocals.setPosition(new_position)
            self.player_other.setPosition(new_position)

    def skip_backward(self):
        new_position = self.player_other.position() - 5000
        if new_position <= 0:
            self.player_drums.setPosition(0)
            self.player_bass.setPosition(0)
            self.player_vocals.setPosition(0)
            self.player_other.setPosition(0)
        else:
            self.player_drums.setPosition(new_position)
            self.player_bass.setPosition(new_position)
            self.player_vocals.setPosition(new_position)
            self.player_other.setPosition(new_position)

    def track_muted(self, muted, track):
        match track:
            case "Drums":
                if muted == True:
                    self.audio_output_drums.setVolume(0)
                else:
                    self.audio_output_drums.setVolume(self.mixer_drums.value() / 100 * self.master_track_volume)
            case "Bass":
                if muted == True:
                    self.audio_output_bass.setVolume(0)
                else:
                    self.audio_output_bass.setVolume(self.mixer_bass.value() / 100 * self.master_track_volume)
            case "Vocals":
                if muted == True:
                    self.audio_output_vocals.setVolume(0)
                else:
                    self.audio_output_vocals.setVolume(self.mixer_vocals.value() / 100 * self.master_track_volume)
            case "Other":
                if muted == True:
                    self.audio_output_other.setVolume(0)
                else:
                    self.audio_output_other.setVolume(self.mixer_other.value() / 100 * self.master_track_volume)
            case "Master":
                if muted == True:
                    self.master_track_volume = 0
                    self.volume_changed(0, "Master")
                else:
                    self.master_track_volume = (self.mixer_master.value() / 100)
                    self.volume_changed(self.mixer_master.value(), "Master")

    def update_playback_state(self, state):
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.media_state = "playing"
            self.media_ctrl_play_pause.setIcon(QIcon.fromTheme("media-pause"))
        elif state == QMediaPlayer.PlaybackState.PausedState:
            self.media_state = "paused"
            self.media_ctrl_play_pause.setIcon(QIcon.fromTheme("media-play"))
        elif state == QMediaPlayer.PlaybackState.StoppedState:
            self.media_state = "stopped"
            self.media_ctrl_play_pause.setIcon(QIcon.fromTheme("media-play"))

    def change_position(self, value):
        self.player_drums.setPosition(value)
        self.player_bass.setPosition(value)
        self.player_vocals.setPosition(value)
        self.player_other.setPosition(value)
    
    def update_duration(self, duration):
        self.media_duration = duration
        self.new_tracker.setMaximum(duration)
        self.tracker_duration_label.setText(self._ms_to_timestamp(duration))

    def update_current_position(self, position):
        self.media_position = position
        self.new_tracker.setTrackerPosition(self.media_position)
        self.tracker_current_label.setText(self._ms_to_timestamp(position))
    
    def volume_changed(self, value, track):
        match track:
            case "Drums":
                if not self.mixer_drums.muted:
                    self.audio_output_drums.setVolume(value / 100 * self.master_track_volume)
            case "Bass":
                if not self.mixer_bass.muted:
                    self.audio_output_bass.setVolume(value / 100 * self.master_track_volume)
            case "Vocals":
                if not self.mixer_vocals.muted:
                    self.audio_output_vocals.setVolume(value / 100 * self.master_track_volume)
            case "Other":
                if not self.mixer_other.muted:
                    self.audio_output_other.setVolume(value / 100 * self.master_track_volume)
            case "Master":
                self.master_track_volume = value / 100

        if not self.mixer_drums.muted:
            self.audio_output_drums.setVolume(self.mixer_drums.value() / 100 * self.master_track_volume)
        if not self.mixer_bass.muted:
            self.audio_output_bass.setVolume(self.mixer_bass.value() / 100 * self.master_track_volume)
        if not self.mixer_vocals.muted:
            self.audio_output_vocals.setVolume(self.mixer_vocals.value() / 100 * self.master_track_volume)
        if not self.mixer_other.muted:
            self.audio_output_other.setVolume(self.mixer_other.value() / 100 * self.master_track_volume)

    def play_pause(self):
        if self.media_state == "inactive":
            self.play()
        elif self.media_state == "paused":
            self.play()
        elif self.media_state == "stopped":
            self.restart()
        elif self.media_state == "playing":
            self.pause()
        else:
            print(f"Error: Unknown playback state '{self.media_state}'")

    def play(self):
        self.media_state = "playing"
        self.media_ctrl_play_pause.setIcon(QIcon.fromTheme("media-pause"))
        self.player_drums.play()
        self.player_bass.play()
        self.player_vocals.play()
        self.player_other.play()

    def pause(self):
        self.media_state = "paused"
        self.media_ctrl_play_pause.setIcon(QIcon.fromTheme("media-play"))
        self.player_drums.pause()
        self.player_bass.pause()
        self.player_vocals.pause()
        self.player_other.pause()

    def restart(self):
        self.media_state = "playing"
        self.media_ctrl_play_pause.setIcon(QIcon.fromTheme("media-pause"))
        self.player_drums.setPosition(0)
        self.player_bass.setPosition(0)
        self.player_vocals.setPosition(0)
        self.player_other.setPosition(0)
        self.player_drums.play()
        self.player_bass.play()
        self.player_vocals.play()
        self.player_other.play()

    @staticmethod
    def _interpolate_playback_speed(slider_value):
        if slider_value == 50:
            speed = 1
        if slider_value < 50:
            speed = slider_value / 49
        if slider_value > 50:
            speed = (slider_value - 51) / (99 - 51) * (2 - 1) + 1
        
        return speed
    
    @staticmethod
    def _interpolate_slider_value(playback_speed):
        if playback_speed == 1:
            slider_value = 50
        if playback_speed < 1:
            slider_value = playback_speed * 49  # Scale from 0-49
        if playback_speed > 1:
            slider_value = (playback_speed - 1) / (2 - 1) * (99 - 51) + 51

        return int(slider_value)
        
    @staticmethod
    def _ms_to_timestamp(ms):
        minutes = ms // 60000
        seconds = (ms % 60000) // 1000
        millies = ms % 1000
        return f"{minutes:02d}:{seconds:02d}.{millies:02d}"
    
    @staticmethod
    def _ms_to_percentage(current, duration):
        start_time = 0

        if duration == start_time:
            return 100 
        if current >= duration:
            return 100

        elapsed_time = current - start_time
        total_time = duration - start_time
        percentage = (elapsed_time / total_time) * 100

        return percentage

    @staticmethod
    def _percentage_to_ms(percentage, duration):
        start_time = 0
        result_time = start_time + (percentage / 100) * duration

        return result_time



def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()


if __name__ == "__main__":
    main()
