from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QLineEdit, QLabel, QSizePolicy, QSlider
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
import sys

class ClickableSlider(QSlider):
    """Custom QSlider that allows seeking by clicking directly on the slider."""
    def __init__(self, orientation):
        super().__init__(orientation)
        self.setTracking(False)  # Disable real-time updating while dragging the slider

    def mousePressEvent(self, event):
        """Handle clicking on the slider."""
        if event.button() == Qt.LeftButton:
            # Calculate the clicked position as a fraction of the slider's range
            clicked_value = (event.x() / self.width()) * self.maximum()
            self.setValue(int(clicked_value))  # Set slider to the clicked position
            # Emit the sliderMoved signal manually to trigger the seek_video method
            self.sliderMoved.emit(int(clicked_value))
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Ensure the slider is updated when dragging is finished."""
        if event.button() == Qt.LeftButton:
            clicked_value = (event.x() / self.width()) * self.maximum()
            self.setValue(int(clicked_value))
            self.sliderMoved.emit(int(clicked_value))
        super().mouseReleaseEvent(event)

class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("pyPlay")
        self.setGeometry(100, 100, 800, 600)

        # Set up media player and video widget
        self.player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.videoWidget = QVideoWidget()

        # Main layout
        main_layout = QVBoxLayout()

        # Video widget
        self.videoWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(self.videoWidget)

        # Controls layout
        self.control_layout = QHBoxLayout()

        # Play/Pause Button
        self.playPauseButton = QPushButton()
        self.playPauseButton.setIcon(QIcon("play_icon.png"))
        self.playPauseButton.clicked.connect(self.toggle_play_pause)
        self.control_layout.addWidget(self.playPauseButton)

        # Stop Button
        self.stopButton = QPushButton()
        self.stopButton.setIcon(QIcon("stop_icon.png"))
        self.stopButton.clicked.connect(self.stop_video)
        self.control_layout.addWidget(self.stopButton)

        # Fullscreen Button
        self.fullscreenButton = QPushButton()
        self.fullscreenButton.setIcon(QIcon("fullscreen_icon.png"))
        self.fullscreenButton.clicked.connect(self.toggle_fullscreen)
        self.control_layout.addWidget(self.fullscreenButton)

        # Progress Bar
        self.progressBar = ClickableSlider(Qt.Horizontal)
        self.progressBar.setRange(0, 100)
        self.progressBar.sliderMoved.connect(self.seek_video)
        self.control_layout.addWidget(self.progressBar)

        # Add controls
        main_layout.addLayout(self.control_layout)

        # URL and Open File input layout
        url_layout = QHBoxLayout()
        self.urlInput = QLineEdit(self)
        self.urlInput.setPlaceholderText("Enter Video URL (Optional)")
        self.urlInput.returnPressed.connect(self.load_from_url)
        url_layout.addWidget(self.urlInput)

        self.openButton = QPushButton("Open File")
        self.openButton.clicked.connect(self.open_media)
        url_layout.addWidget(self.openButton)

        or_label = QLabel("or")
        url_layout.addWidget(or_label)

        main_layout.addLayout(url_layout)

        # Feedback label
        self.feedbackLabel = QLabel("Choose a file or URL to start playing.")
        main_layout.addWidget(self.feedbackLabel)

        # Player and widget connection
        self.player.setVideoOutput(self.videoWidget)
        self.player.positionChanged.connect(self.update_progress)
        self.player.durationChanged.connect(self.update_duration)

        self.setLayout(main_layout)

    def open_media(self):
        choice = QFileDialog.getOpenFileName(
            self, "Open Media File", "",
            "Media Files (*.mp4 *.mov *.avi *.mkv *.wmv *.flv *.mp3 *.wav *.aac *.flac *.ogg *.wma);;All Files (*.*)"
        )
        if choice[0]:
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(choice[0])))
            self.play_video()
            self.feedbackLabel.setText(f"Now playing: {choice[0]}")

    def load_from_url(self):
        url = self.urlInput.text()
        if url:
            self.player.setMedia(QMediaContent(QUrl(url)))
            self.play_video()
            self.feedbackLabel.setText(f"Now playing: {url}")

    def play_video(self):
        if self.player.state() != QMediaPlayer.PlayingState:
            self.player.play()
            self.playPauseButton.setIcon(QIcon("pause_icon.png"))

    def pause_video(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.playPauseButton.setIcon(QIcon("play_icon.png"))

    def toggle_play_pause(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.pause_video()
        else:
            self.play_video()

    def stop_video(self):
        self.player.stop()
        self.playPauseButton.setIcon(QIcon("play_icon.png"))

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def update_progress(self, position):
        """Update the progress bar based on the current position of the video."""
        duration = self.player.duration()
        if duration > 0:
            progress = (position / duration) * 100
            self.progressBar.setValue(int(progress))

    def update_duration(self, duration):
        """Update the range of the progress bar when the video duration changes."""
        if duration > 0:
            self.progressBar.setRange(0, 100)

    def seek_video(self):
        """Seek the video to the selected position."""
        position = int((self.progressBar.value() / 100) * self.player.duration())
        self.player.setPosition(position)

    def keyPressEvent(self, event):
        """Handle ESC key to exit fullscreen."""
        if event.key() == Qt.Key_Escape and self.isFullScreen():
            self.showNormal()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        """Clear focus from URL input on click elsewhere."""
        self.urlInput.clearFocus()
        super().mousePressEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoPlayer()
    window.show()
    sys.exit(app.exec_())
