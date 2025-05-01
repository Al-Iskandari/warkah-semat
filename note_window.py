from PySide6.QtCore import Qt, QDateTime, QTimer
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QComboBox,
    QDateTimeEdit,
    QCheckBox,
    QLabel,
    QMenu,
)
from database import Note, session


class NoteWindow(QWidget):
    def __init__(self, note=None, active_notewindows=None):
        super().__init__()

        self.active_notewindows = active_notewindows  # Store active_notewindows

        self.setWindowFlags(
            self.windowFlags()
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )

        self.setStyleSheet(
            "background: #FCF259; color: #62622f; border: 0; font-size: 16pt;"
            "QComboBox {border: 1px solid gray;border-radius: 3px;padding: 1px 18px 1px 3px;min-width: 6em;}"
            "QComboBox::drop-down {subcontrol-origin: padding;subcontrol-position: top right;width: 15pxborder-left-width: 1px;border-left-color: darkgray;border-left-style: solid; /* just a single line */border-top-right-radius: 3px; /* same radius as the QComboBox */border-bottom-right-radius: 3px;}"
            "QComboBox:on { /* shift the text when the popup opens */ padding: 3px 3px 3px 3px; }"
            "QComboBox QAbstractItemView {selection-background-color: #FFFF99; selection-color: #62622f;}"

        )
        layout = QVBoxLayout()

        buttons = QHBoxLayout()
        self.close_btn = QPushButton("×")
        self.close_btn.setStyleSheet(
            "font-weight: bold; font-size: 25px; width: 25px; height: 25px;"
        )
        self.close_btn.clicked.connect(self.delete)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        buttons.addStretch()  # Add stretch on left to push button right.
        buttons.addWidget(self.close_btn)
        layout.addLayout(buttons)

        # Priority selection
        self.priority_label = QLabel("Priority:")
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Low", "Medium", "High", "Critical"])
        self.priority_combo.currentIndexChanged.connect(self.save)
        priority_layout = QHBoxLayout()
        priority_layout.addWidget(self.priority_label)
        priority_layout.addWidget(self.priority_combo)
        layout.addLayout(priority_layout)

        # Timer option
        self.timer_checkbox = QCheckBox("Set Timer:")
        self.timer_checkbox.stateChanged.connect(self.toggle_timer_input)
        layout.addWidget(self.timer_checkbox)

        self.timer_input = QDateTimeEdit()
        self.timer_input.setCalendarPopup(True)
        self.timer_input.dateTimeChanged.connect(self.save)
        self.timer_input.setVisible(False)  # Initially hidden
        layout.addWidget(self.timer_input)

        self.text = QTextEdit()
        layout.addWidget(self.text)
        self.setLayout(layout)

        self.text.textChanged.connect(self.save)

        # Store a reference to this note in the active_notewindows
        if self.active_notewindows is not None:
            self.active_notewindows[id(self)] = self

        # If no note is provided, create one.
        if note is None:
            self.note = Note()
            self.save()
        else:
            self.note = note
            self.load()

        self.update_styles()

    def toggle_timer_input(self, state):
        self.timer_input.setVisible(state == Qt.CheckState.Checked)
        self.save()

    def mousePressEvent(self, e):
        self.previous_pos = e.globalPosition()

    def mouseMoveEvent(self, e):
        delta = e.globalPosition() - self.previous_pos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.previous_pos = e.globalPosition()

    def mouseReleaseEvent(self, e):
        self.save()

    def load(self):
        self.move(self.note.x, self.note.y)
        self.text.setText(self.note.text)
        self.priority_combo.setCurrentText(self.note.priority)
        self.timer_checkbox.setChecked(self.note.timer_enabled)
        if self.note.timer_enabled:
            self.timer_input.setDateTime(QDateTime.fromSecsSinceEpoch(self.note.timer_time))
            self.timer_input.setVisible(True)
        else:
            self.timer_input.setVisible(False)

    def save(self):
        self.note.x = self.x()
        self.note.y = self.y()
        self.note.text = self.text.toPlainText()
        self.note.priority = self.priority_combo.currentText()
        self.note.timer_enabled = self.timer_checkbox.isChecked()
        if self.timer_checkbox.isChecked():
            self.note.timer_time = self.timer_input.dateTime().toSecsSinceEpoch()
        else:
            self.note.timer_time = None

        # Write the data to the database, adding the Note object to the
        # current session and committing the changes.
        session.add(self.note)
        session.commit()
        self.update_styles()

    def delete(self):
        session.delete(self.note)
        session.commit()
        if self.active_notewindows is not None:
            del self.active_notewindows[id(self)]
        self.close()

    def update_styles(self):
        if self.note.priority == "Critical":
            self.setStyleSheet(
                "background: #C5172E; color: #FFFFFF; border:0; font-size: 18pt;"
            )
            self.resize(300, 200)  # Larger dimensions
            self.setWindowFlag(Qt.WindowStaysOnTopHint, True)  # Always on top
            self.show()  # Refresh the window to apply the flag
        elif self.note.priority == "High":
            self.setStyleSheet(
                "background: #85193C; color: #FFFFFF; border:0; font-size: 18pt;"
            )
            self.resize(300, 200)
            self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
            self.show()
        else:
            self.setStyleSheet(
                "background: #FCF259; color: #62622f; border: 0; font-size: 16pt;"
            )
            self.setWindowFlag(Qt.WindowStaysOnTopHint, False)  # Not always on top
            self.show()  # Refresh the window to apply the flag
