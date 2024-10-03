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

    def __init__(self):
        super().__init__()

        # General settings
        self.setWindowTitle(self.window_title)
        self.setWindowIcon(QIcon("res/drumpal_icon.webp"))
        self.setMinimumSize(QSize(400, 550))

        # Layout definitions
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignJustify)

        song_select_section = QHBoxLayout()
        song_select_section.setAlignment(Qt.AlignmentFlag.AlignLeft)

        tracker_section = QVBoxLayout()
        tracker_labels_section = QHBoxLayout()
        tracker_labels_section.setAlignment(Qt.AlignmentFlag.AlignLeading)
        pos_ctrl_section = QHBoxLayout()
        checkpoint_section = QGridLayout()
        checkpoint_section.setAlignment(Qt.AlignmentFlag.AlignLeft)
        media_ctrl_section = QHBoxLayout()

        speed_ctrl_section = QVBoxLayout()
        speed_fine_section = QHBoxLayout()
        speed_coarse_section = QHBoxLayout()

        mixer_section = QHBoxLayout()
        mixer_section.setAlignment(Qt.AlignmentFlag.AlignJustify)

        footer_section = QHBoxLayout()

        # Widget definitions
        song_select_button = QPushButton(QIcon.fromTheme("document-open"), "Browse...")
        song_select_button.setFixedSize(QSize(100, 30))

        song_select_label = QLabel("No song selected")
        song_select_label.setFont(QFont("sans-serif", italic=True))

        tracker = QSlider()
        tracker.setOrientation(Qt.Orientation.Horizontal)
        tracker.setFixedHeight(50)

        tracker_current_label = QLabel("00:00.00")
        tracker_label_spacer = QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        tracker_duration_label = QLabel("00:00.00")

        pos_ctrl_section.addLayout(checkpoint_section)
        pos_ctrl_section.addLayout(media_ctrl_section)

        checkpoint_button_size = QSize(30, 30)
        checkpoint1_set_button = QPushButton("S1")
        checkpoint1_set_button.setFixedSize(checkpoint_button_size)
        checkpoint1_ld_button = QPushButton("L1")
        checkpoint1_ld_button.setFixedSize(checkpoint_button_size)
        checkpoint2_set_button = QPushButton("S2")
        checkpoint2_set_button.setFixedSize(checkpoint_button_size)
        checkpoint2_ld_button = QPushButton("L2")
        checkpoint2_ld_button.setFixedSize(checkpoint_button_size)
        checkpoint3_set_button = QPushButton("S3")
        checkpoint3_set_button.setFixedSize(checkpoint_button_size)
        checkpoint3_ld_button = QPushButton("L3")
        checkpoint3_ld_button.setFixedSize(checkpoint_button_size)
        checkpoint4_set_button = QPushButton("S4")
        checkpoint4_set_button.setFixedSize(checkpoint_button_size)
        checkpoint4_ld_button = QPushButton("L4")
        checkpoint4_ld_button.setFixedSize(checkpoint_button_size)

        media_button_size = QSize(40, 40)
        media_ctrl_ld_back = QPushButton(QIcon.fromTheme("media-skip-backward"), "")
        media_ctrl_ld_back.setFixedSize(media_button_size)
        media_ctrl_back = QPushButton(QIcon.fromTheme("media-seek-backward"), "")
        media_ctrl_back.setFixedSize(media_button_size)
        media_ctrl_play_pause = QPushButton(QIcon.fromTheme("media-play"), "")
        media_ctrl_play_pause.setFixedSize(media_button_size)
        media_ctrl_fwd = QPushButton(QIcon.fromTheme("media-seek-forward"), "")
        media_ctrl_fwd.setFixedSize(media_button_size)
        media_ctrl_ld_fwd = QPushButton(QIcon.fromTheme("media-skip-forward"), "")
        media_ctrl_ld_fwd.setFixedSize(media_button_size)

        mixer_drum = MixerWidget(labelText="Drum")
        mixer_bass = MixerWidget(labelText="Bass")
        mixer_vocal = MixerWidget(labelText="Vocals")
        mixer_other = MixerWidget(labelText="Other")
        mixer_master = MixerWidget(labelText="Master")

        settings_button = QPushButton(QIcon.fromTheme("document-properties"), "")
        settings_button.setFixedSize(media_button_size)
        footer_spacer = QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        notation_view_button = QPushButton(QIcon.fromTheme("go-next"), "Notation View")
        notation_view_button.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        notation_view_button.setFixedSize(QSize(160, 40))

        # Layout placement
        main_layout.addLayout(song_select_section)
        main_layout.addLayout(tracker_section)
        main_layout.addLayout(pos_ctrl_section)
        main_layout.addLayout(speed_ctrl_section)
        main_layout.addLayout(mixer_section)
        main_layout.addLayout(footer_section)

        # Widget placement
        song_select_section.addWidget(song_select_button)
        song_select_section.addWidget(song_select_label)

        tracker_section.addWidget(tracker)
        tracker_section.addLayout(tracker_labels_section)
        tracker_labels_section.addWidget(tracker_current_label)
        tracker_labels_section.addSpacerItem(tracker_label_spacer)
        tracker_labels_section.addWidget(tracker_duration_label)

        checkpoint_section.addWidget(checkpoint1_set_button, 0, 0)
        checkpoint_section.addWidget(checkpoint1_ld_button, 1, 0)
        checkpoint_section.addWidget(checkpoint2_set_button, 0, 1)
        checkpoint_section.addWidget(checkpoint2_ld_button, 1, 1)
        checkpoint_section.addWidget(checkpoint3_set_button, 0, 2)
        checkpoint_section.addWidget(checkpoint3_ld_button, 1, 2)
        checkpoint_section.addWidget(checkpoint4_set_button, 0, 3)
        checkpoint_section.addWidget(checkpoint4_ld_button, 1, 3)

        media_ctrl_section.addWidget(media_ctrl_ld_back)
        media_ctrl_section.addWidget(media_ctrl_back)
        media_ctrl_section.addWidget(media_ctrl_play_pause)
        media_ctrl_section.addWidget(media_ctrl_fwd)
        media_ctrl_section.addWidget(media_ctrl_ld_fwd)

        mixer_section.addWidget(mixer_drum)
        mixer_section.addWidget(mixer_bass)
        mixer_section.addWidget(mixer_vocal)
        mixer_section.addWidget(mixer_other)
        mixer_section.addWidget(mixer_master)

        footer_section.addWidget(settings_button)
        footer_section.addSpacerItem(footer_spacer)
        footer_section.addWidget(notation_view_button)

        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()


if __name__ == "__main__":
    main()
