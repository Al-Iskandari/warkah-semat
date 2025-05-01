from PySide6.QtCore import Qt, QTimer, QDateTime
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHBoxLayout,
    QHeaderView,
    QTextEdit,
    QLabel,
    QWidget,
    QMessageBox,
)


class Dashboard(QDialog):
    def __init__(self, active_notewindows, parent=None):
        super().__init__(parent)
        self.active_notewindows = active_notewindows
        self.setWindowTitle("Notes Dashboard")
        self.setGeometry(100, 100, 800, 600)  # Adjust size as needed

        self.layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(6)  # Increased column count
        self.table.setHorizontalHeaderLabels(
            [
                "ID",
                "Text",
                "Priority",
                "Timer",
                "Time Remaining",
                "Actions",
            ]
        )  # Updated header labels
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )  # Stretch columns
        self.layout.addWidget(self.table)

        self.populate_table()
        self.table.cellClicked.connect(self.show_details)

        self.setLayout(self.layout)

        # Timer to update the time remaining every minute
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time_remaining)
        self.timer.start(60000)  # Update every 60 seconds

    def populate_table(self):
        self.table.setRowCount(0)
        for note_window_id, note_window in self.active_notewindows.items():
            note = note_window.note
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)

            self.table.setItem(row_position, 0, QTableWidgetItem(str(note.id)))
            self.table.setItem(row_position, 1, QTableWidgetItem(note.text[:50]))  # Show only first 50 characters
            self.table.setItem(row_position, 2, QTableWidgetItem(note.priority))
            timer_status = "Yes" if note.timer_enabled else "No"
            self.table.setItem(row_position, 3, QTableWidgetItem(timer_status))

            # Add time remaining, initially empty
            self.table.setItem(row_position, 4, QTableWidgetItem(""))
            self.update_time_remaining()  # Initial update

            # Action buttons
            actions_widget = self.create_action_buttons(note_window)
            self.table.setCellWidget(row_position, 5, actions_widget)

    def create_action_buttons(self, note_window):
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        widget.setLayout(layout)

        stick_button = QPushButton("Stick")
        stick_button.clicked.connect(lambda: self.stick_note(note_window))
        layout.addWidget(stick_button)

        return widget

    def stick_note(self, note_window):
        note_window.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        note_window.show()  # Refresh the window to apply the flag

    def show_details(self, row, column):
        note_id = int(self.table.item(row, 0).text())
        # Find the corresponding note_window
        note_window = next(
            (
                note_window
                for note_window_id, note_window in self.active_notewindows.items()
                if note_window.note.id == note_id
            ),
            None,
        )

        if note_window:
            # Create a pop-up dialog to show the full details
            details_dialog = QDialog(self)
            details_dialog.setWindowTitle(f"Note Details - ID: {note_id}")
            details_layout = QVBoxLayout()

            text_edit = QTextEdit()
            text_edit.setText(note_window.note.text)
            text_edit.setReadOnly(True)
            details_layout.addWidget(text_edit)

            priority_label = QLabel(f"Priority: {note_window.note.priority}")
            details_layout.addWidget(priority_label)

            timer_label = QLabel(
                f"Timer Enabled: {'Yes' if note_window.note.timer_enabled else 'No'}"
            )
            details_layout.addWidget(timer_label)

            if note_window.note.timer_enabled:
                timer_time = QDateTime.fromSecsSinceEpoch(note_window.note.timer_time)
                timer_time_label = QLabel(f"Timer Time: {timer_time.toString()}")
                details_layout.addWidget(timer_time_label)

            details_dialog.setLayout(details_layout)
            details_dialog.exec_()

    def update_time_remaining(self):
        for row in range(self.table.rowCount()):
            note_id = int(self.table.item(row, 0).text())
            # Find the corresponding note_window
            note_window = next(
                (
                    note_window
                    for note_window_id, note_window in self.active_notewindows.items()
                    if note_window.note.id == note_id
                ),
                None,
            )
            if note_window and note_window.note.timer_enabled:
                time_remaining_ms = (
                    QDateTime.fromSecsSinceEpoch(note_window.note.timer_time).toMSecsSinceEpoch()
                    - QDateTime.currentDateTime().toMSecsSinceEpoch()
                )
                if time_remaining_ms > 0:
                    days, seconds = divmod(time_remaining_ms // 1000, 24 * 3600)
                    hours, seconds = divmod(seconds, 3600)
                    minutes, seconds = divmod(seconds, 60)
                    time_remaining_str = f"{days}d {hours}h {minutes}m {seconds}s"
                    self.table.setItem(row, 4, QTableWidgetItem(time_remaining_str))
                else:
                    self.table.setItem(row, 4, QTableWidgetItem("Timer Expired"))
