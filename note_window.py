import os
from PySide6.QtCore import Qt, QDateTime, QTimer, QRectF, Signal
from PySide6.QtGui import (
    QIcon,
    QPixmap,
    QColor,
    QPainter,
    QPainterPath,
    QBrush,
    QTextCursor,
)
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
    QFrame,
)
from database import Note, session
from utils import auto_list


class NoteWindow(QWidget):
    note_updated = Signal()

    def __init__(self, note=None, active_notewindows=None):
        super().__init__()
        # Store active_notewindows
        self.active_notewindows = active_notewindows

        self.setWindowFlags(
            self.windowFlags()
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.setStyleSheet(
            "background: rgba(0, 0, 0, 0);"
            "color: #62622f;"
            "border: 0;"
            "border-radius:20px;"
            "border-radius:7px;"
            "font-size: 16pt; "
            "QComboBox {border: 1px solid gray; border-radius: 3px; "
            "padding: 1px 18px 1px 3px; min-width: 6em;}"
            "QComboBox::drop-down {subcontrol-origin: padding; "
            "subcontrol-position: top right; width: 15px; "
            "border-left-width: 1px; border-left-color: darkgray; "
            "border-left-style: solid; /* just a single line */"
            "border-top-right-radius: 3px; /* same radius as the QComboBox */"
            "border-bottom-right-radius: 3px;}"
            "QComboBox:on { /* shift the text when the popup opens */ "
            "padding: 3px 3px 3px 3px; }"
            "QComboBox QAbstractItemView {selection-background-color: #FFFF99;"
            "selection-color: #62622f;}"

        )
        layout = QVBoxLayout()

        buttons = QHBoxLayout()
        self.unstick_btn = QPushButton()
        self.unstick_btn.setToolTip("minimize")
        self.unstick_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.set_button_icon(
            self.unstick_btn, os.path.join('resources', 'minimize.png')
        )
        self.unstick_btn.clicked.connect(self.unstick)
        buttons.addWidget(self.unstick_btn)

        self.divider = QLabel("|")
        self.divider.setStyleSheet("color: #62622f; font-size: 16pt;")
        buttons.addWidget(self.divider)
        self.divider.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.delete_btn = QPushButton()
        self.delete_btn.setToolTip('delete')
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.set_button_icon(
            self.delete_btn, os.path.join('resources', 'trash.png')
        )
        self.delete_btn.clicked.connect(self.delete)
        buttons.addWidget(self.delete_btn)

        buttons.setAlignment(Qt.AlignmentFlag.AlignRight)
        buttons.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(buttons)

        # Add a divider line
        self.line = QWidget()
        self.line.setFixedHeight(1)
        self.line.setStyleSheet("background-color: #444444;")
        layout.addWidget(self.line)

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
        self.timer_checkbox.setStyleSheet(f"""
            QCheckBox {{
                spacing: 5px; /* Adjust spacing between label and indicator */
            }}

            QCheckBox::indicator {{
                background: white;
                border: 1px solid black;
                width: 20px;
                height: 20px;
                border-radius: 11px;
            }}

            QCheckBox::indicator:unchecked {{
                image: url({os.path.join('resources', 'unchecked.png')});
            }}

            QCheckBox::indicator:checked {{
                image: url({os.path.join('resources', 'checked.png')});
            }}

            """)
        self.timer_checkbox.stateChanged.connect(self.toggle_timer_input)
        layout.addWidget(self.timer_checkbox)

        self.timer_input = QDateTimeEdit()
        self.timer_input.setCalendarPopup(True)
        self.timer_input.dateTimeChanged.connect(self.save)
        self.timer_input.setVisible(False)  # Initially hidden
        layout.addWidget(self.timer_input)

        self.text = QTextEdit()
        layout.addWidget(self.text)

        # Set timer countdown
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(1000)  # Update every 1 second
        self.time_remaining = ""

        # Create a frame (border)
        self.frame = QFrame()
        self.frame.setFrameShape(QFrame.Shape.Box)
        self.frame.setLineWidth(2)
        self.frame.setStyleSheet("border: 1px solid black; margin: 20px;")

        # Create a label
        self.timer_label = QLabel("Deadline", self.frame)
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setStyleSheet(
            "background-color: white; color: black; padding: 5px;"
        )

        # create label for the timer
        self.time_remaining_label = QLabel("", self.frame)
        self.time_remaining_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_remaining_label.setStyleSheet(
            "border: 0;"
        )

        # Layout setup
        layoutTimer = QVBoxLayout()
        layoutTimer.addWidget(self.frame)
        layoutTimer.setContentsMargins(10, 10, 10, 10)  # Remove margins

        self.main_layout_timer = QVBoxLayout()
        self.main_layout_timer.addLayout(layoutTimer)

        layout.addLayout(self.main_layout_timer)

        # Adjust label position to overlap the border
        self.timer_label.move(10, -10)
        self.time_remaining_label.move(10, 25)

        # Adjust frame and label size
        self.frame.setFixedSize(250, 100)
        self.timer_label.setFixedWidth(self.frame.width() - 100)
        self.time_remaining_label.setFixedWidth(self.frame.width() - 20)

        self.setLayout(layout)

        self.text.textChanged.connect(self.text_changed)

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

    def text_changed(self):
        self.text.blockSignals(True)
        self.text.setText(auto_list(self.text.toPlainText()))
        self.text.setMinimumHeight(self.text.document().size().height())
        self.text.adjustSize()
        cursor = self.text.textCursor()
        cursor.movePosition(QTextCursor.End)  # Restore cursor position
        cursor.setPosition(cursor.position())
        self.text.setTextCursor(cursor)
        self.save()
        self.text.blockSignals(False)

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

    def update_countdown(self):
        if self.note.timer_enabled and self.note.timer_time:
            now = QDateTime.currentDateTime().toSecsSinceEpoch()
            remaining = self.note.timer_time - now
            if remaining > 0:
                days = remaining // (24 * 3600)
                remaining %= (24 * 3600)
                hours = remaining // 3600
                remaining %= 3600
                minutes = remaining // 60
                seconds = remaining % 60
                self.time_remaining = f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"
            else:
                self.time_remaining = "Expired"
            self.time_remaining_label.setText(self.time_remaining)
            self.frame.setVisible(True)
        else:
            self.time_remaining = ""
            self.frame.setVisible(False)

        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.active_notewindows is not None:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            path = QPainterPath()
            rect = QRectF(0, 0, self.width(), self.height())
            path.addRoundedRect(rect, 20, 20)
            if self.note.priority == "Critical":
                bg_color = "#C5172E"
            elif self.note.priority == "High":
                bg_color = "#85193C"
            elif self.note.priority == "Medium":
                bg_color = "#E85C0D"
            else:
                bg_color = "#FCF259"
            painter.fillPath(path, QBrush(QColor(bg_color)))

    def load(self):
        self.move(self.note.x, self.note.y)

        # Set the priority combo box
        index = self.priority_combo.findText(self.note.priority)
        timerEnabled = 1 if self.note.timer_enabled else 0
        date_time = QDateTime.fromSecsSinceEpoch(
            self.note.timer_time if self.note.timer_time else 1746378000
        )
        # print(f"Timer time: {date_time.toString()}")
        self.text.setPlainText(self.note.text if self.note.text else "")

        if index >= 0:
            self.priority_combo.setCurrentIndex(index)
        else:
            self.priority_combo.setCurrentIndex(0)

        # Set the timer checkbox
        self.timer_checkbox.setChecked(timerEnabled)

        if timerEnabled:
            if self.note.timer_time is not None:
                try:
                    self.timer_input.setDateTime(date_time)
                    self.timer_input.setVisible(True)
                except Exception as e:
                    print(f"Error setting timer time: {e}")
                    self.timer_input.setVisible(False)
            else:
                self.timer_input.setVisible(False)
        else:
            self.timer_input.setVisible(False)

        self.update_countdown()

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
        self.note_updated.emit()

    def delete(self):
        session.delete(self.note)
        session.commit()
        if self.active_notewindows is not None:
            del self.active_notewindows[id(self)]
        self.note_updated.emit()
        self.close()

    def unstick(self):
        self.setWindowFlag(Qt.WindowStaysOnTopHint, False)
        self.hide()

    def set_button_icon(self, button: QPushButton, icon_path: str, color: QColor = None):
        icon = QIcon(icon_path)
        pixmap = icon.pixmap(35, 30)
        if color is not None:
            image = pixmap.toImage()
            for x in range(image.width()):
                for y in range(image.height()):
                    if image.pixelColor(x, y).alpha() > 0:
                        image.setPixelColor(x, y, color.toRgb())
            pixmap = QPixmap.fromImage(image)
        button.setIcon(QIcon(pixmap))

    def update_styles(self):
        if self.note.priority == "Critical":
            bg_color = "#C5172E"
            text_color = "#FFFFFF"
        elif self.note.priority == "High":
            bg_color = "#85193C"
            text_color = "#FFFFFF"
        elif self.note.priority == "Medium":
            bg_color = "#E85C0D"
            text_color = "#FFFFFF"
        else:
            bg_color = "#FCF259"
            text_color = "#62622f"

        self.setStyleSheet(
            f"background: rgba(0, 0, 0, 0); color: {text_color};"
            f"border: 0; border-radius:20px; "
            f"border-radius:7px; font-size: 16pt; "
            f"QComboBox {{border: 1px solid gray; border-radius: 3px; "
            f"padding: 1px 18px 1px 3px; min-width: 6em;}}"
            f"QComboBox::drop-down {{subcontrol-origin: padding; "
            f"subcontrol-position: top right; width: 15px; "
            f"border-left-width: 1px; border-left-color: darkgray; "
            f"border-left-style: solid; /* just a single line */"
            f"border-top-right-radius: 3px; /* same radius as the QComboBox */"
            f"border-bottom-right-radius: 3px;}}"
            f"QComboBox:on {{ /* shift the text when the popup opens */ "
            f"padding: 3px 3px 3px 3px; }}"
            f"QComboBox QAbstractItemView {{selection-background-color: #FFFF99;"
            f"selection-color: {text_color};}}"
        )
        timer_bg_color = bg_color  # Same as note background
        timer_text_color = text_color
        self.frame.setStyleSheet(
            f"border: 1px solid {text_color}; border-radius: 7px; "
            f"background-color: {timer_bg_color}; margin: 20px;"
        )

        self.timer_label.setStyleSheet(
            f"border: 1px solid {text_color}; border-radius: 7px; "
            f"padding: 2px; background-color: {timer_bg_color}; "
            f"color: {timer_text_color}; font-size: 16pt;"
        )

        if self.note.priority in ("Critical", "High", "Medium"):
            self.set_button_icon(
                self.unstick_btn, os.path.join('resources', 'minimize.png'),
                QColor(text_color)
            )
            self.set_button_icon(
                self.delete_btn, os.path.join('resources', 'trash.png'),
                QColor(text_color)
            )
            self.line.setStyleSheet(f"background-color: {text_color};")
            self.divider.setStyleSheet(
                f"color: {text_color}; font-size: 16pt;"
            )
            self.resize(300, 200)
            self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        else:
            self.set_button_icon(
                self.unstick_btn, os.path.join('resources', 'minimize.png')
            )
            self.set_button_icon(
                self.delete_btn, os.path.join('resources', 'trash.png')
            )
            self.line.setStyleSheet(f"background-color: {text_color};")
            self.divider.setStyleSheet(
                f"color: {text_color}; font-size: 16pt;"
            )
            self.resize(300, 200)
            self.setWindowFlag(Qt.WindowStaysOnTopHint, False)
        self.show()