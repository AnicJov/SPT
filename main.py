import sys

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
)

from MixerWidget import MixerWidget


class MainWindow(QMainWindow):
    window_title = "SPT - Song Practice Tool"
    media_state = "inactive"

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
        self.checkpoint2_set_button = QPushButton("S2")
        self.checkpoint2_set_button.setFixedSize(self.checkpoint_button_size)
        self.checkpoint2_ld_button = QPushButton("L2")
        self.checkpoint2_ld_button.setFixedSize(self.checkpoint_button_size)
        self.checkpoint3_set_button = QPushButton("S3")
        self.checkpoint3_set_button.setFixedSize(self.checkpoint_button_size)
        self.checkpoint3_ld_button = QPushButton("L3")
        self.checkpoint3_ld_button.setFixedSize(self.checkpoint_button_size)
        self.checkpoint4_set_button = QPushButton("S4")
        self.checkpoint4_set_button.setFixedSize(self.checkpoint_button_size)
        self.checkpoint4_ld_button = QPushButton("L4")
        self.checkpoint4_ld_button.setFixedSize(self.checkpoint_button_size)

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

        palette = self.palette()
        self.mixer_drum = MixerWidget(labelText="Drum")
        self.mixer_drum.setBackgroundColor(palette.base().color())
        self.mixer_drum.setColor(palette.highlight().color())
        self.mixer_bass = MixerWidget(labelText="Bass")
        self.mixer_bass.setBackgroundColor(palette.base().color())
        self.mixer_bass.setColor(palette.highlight().color())
        self.mixer_vocal = MixerWidget(labelText="Vocals")
        self.mixer_vocal.setBackgroundColor(palette.base().color())
        self.mixer_vocal.setColor(palette.highlight().color())
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

        self.mixer_section.addWidget(self.mixer_drum)
        self.mixer_section.addWidget(self.mixer_bass)
        self.mixer_section.addWidget(self.mixer_vocal)
        self.mixer_section.addWidget(self.mixer_other)
        self.mixer_section.addWidget(self.mixer_master)

        self.footer_section.addWidget(self.settings_button)
        self.footer_section.addSpacerItem(self.footer_spacer)
        self.footer_section.addWidget(self.notation_view_button)

        self.main_widget = QWidget()
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)
        
        # Audio functionality
        filename = "song.mp3"
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.player.setSource(QUrl.fromLocalFile(filename))
        self.audio_output.setVolume(100)
        self.mixer_master.volumeChanged.connect(self.volume_changed)

        self.media_ctrl_play_pause.clicked.connect(self.play_pause)
    
    def volume_changed(self, value):
        self.audio_output.setVolume(value / 100)

    def play_pause(self):
        if self.media_state != "playing":
            self.play()
        else:
            self.pause()

    def play(self):
        self.media_state = "playing"
        self.media_ctrl_play_pause.setIcon(QIcon.fromTheme("media-pause"))
        self.player.play()

    def pause(self):
        self.media_state = "paused"
        self.media_ctrl_play_pause.setIcon(QIcon.fromTheme("media-play"))
        self.player.pause()


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()


if __name__ == "__main__":
    main()
