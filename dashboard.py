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
    QComboBox,
)


class Dashboard(QDialog):
    def __init__(self, active_notewindows, parent=None):
        super().__init__(parent)
        self.active_notewindows = active_notewindows
        self.setWindowTitle("Notes Dashboard")
        self.setGeometry(100, 100, 800, 600)

        self.layout = QVBoxLayout()

        # Add sorting combobox
        self.sorting_criteria = QComboBox()
        self.sorting_criteria.addItems(
            [
                "Priority",
                "Time Remaining",
                "ID",
                "Text",
                "Timer",
            ]
        )  # Add sorting options
        self.sorting_criteria.currentIndexChanged.connect(
            self.populate_table
        )  # Repopulate table on change
        self.layout.addWidget(self.sorting_criteria)

        self.table = QTableWidget()
        self.table.setStyleSheet(
            "QHeaderView::section {background-color: #FFFF99; color: #62622f;}"
        )

        self.table.setColumnCount(6)
        header_labels = [
            "Priority",
            "ID",
            "Text",
            "Timer",
            "Time Remaining",
            "Actions",
        ]
        self.table.setHorizontalHeaderLabels(header_labels)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.resizeRowsToContents()
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 20)
        self.layout.addWidget(self.table)

        self.populate_table()
        self.table.cellClicked.connect(self.show_details)

        # Connect note_updated signal to populate_table
        for note_window_id, note_window in self.active_notewindows.items():
            note_window.note_updated.connect(self.populate_table)

        self.setLayout(self.layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time_remaining)
        self.timer.start(1000)  # Update every 1 second

    def populate_table(self):
        self.table.setRowCount(0)
        # Get selected sorting criteria
        sorting_criteria = self.sorting_criteria.currentText()

        # Sort the note windows based on the selected criteria
        sorted_note_windows = sorted(
            self.active_notewindows.items(),
            key=lambda item: self.get_sorting_key(item[1], sorting_criteria),
        )

        for note_window_id, note_window in sorted_note_windows:
            note = note_window.note
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)

            # Create a colored label based on priority
            priority_color = self.get_priority_color(note.priority)
            color_label = QLabel()
            color_label.setStyleSheet(
                f"background-color: {priority_color}; border: none;"
            )
            color_label.setFixedSize(60, 100)  # Adjust size as needed
            color_label.setToolTip(note.priority)  # Show priority on hover
            color_widget = QWidget()
            color_layout = QHBoxLayout()
            color_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            color_layout.setContentsMargins(0, 0, 0, 0)
            color_layout.addWidget(color_label)
            color_widget.setLayout(color_layout)
            self.table.setCellWidget(row_position, 0, color_widget)
            self.table.setItem(
                row_position, 1, QTableWidgetItem(str(note.id))
            )
            note_text = note.text[:50]
            self.table.setItem(
                row_position, 2, QTableWidgetItem(note_text)
            )
            timer_status = "Yes" if note.timer_enabled else "No"
            self.table.setItem(
                row_position, 3, QTableWidgetItem(timer_status)
            )

            self.table.setItem(row_position, 4, QTableWidgetItem(""))
            self.update_time_remaining()

            actions_widget = self.create_action_buttons(note_window)
            self.table.setCellWidget(row_position, 5, actions_widget)

    def get_sorting_key(self, note_window, criteria):
        note = note_window.note
        if criteria == "Priority":
            priority_values = {"Critical": 1, "High": 2, "Medium": 3, "Low": 4}
            return priority_values.get(note.priority, 5)  # Lower value means higher priority
        elif criteria == "Time Remaining":
            if note.timer_enabled and note.timer_time is not None:
                timer_time_epoch = QDateTime.fromSecsSinceEpoch(
                    note.timer_time
                ).toMSecsSinceEpoch()
                current_time_epoch = (
                    QDateTime.currentDateTime().toMSecsSinceEpoch()
                )
                time_remaining_ms = timer_time_epoch - current_time_epoch
                return time_remaining_ms if time_remaining_ms >= 0 else float(
                    'inf'
                )  # Expired timers go to the end
            else:
                return float('inf')  # No timer goes to the end
        elif criteria == "ID":
            return note.id
        elif criteria == "Text":
            return note.text
        elif criteria == "Timer":
            return note.timer_enabled
        else:
            return 0  # Default case

    def get_priority_color(self, priority):
        if priority == "Critical":
            return "#C5172E"
        elif priority == "High":
            return "#85193C"
        elif priority == "Medium":
            return "#E85C0D"
        else:
            return "#FCF259"

    def create_action_buttons(self, note_window):
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        widget.setLayout(layout)

        stick_button = QPushButton()
        self.update_stick_button_text(stick_button, note_window)
        stick_button.setStyleSheet(
            "background-color: lightblue; border-radius: 5px; padding: 5px;"
            "border: 1px solid #62622f; color: black;"
            "font-weight: bold; font-size: 12px; min-width: 60px;"
        )
        stick_button.setCursor(Qt.CursorShape.PointingHandCursor)
        stick_button.clicked.connect(
            lambda: self.toggle_note(note_window, stick_button)
        )
        layout.addWidget(stick_button)

        return widget

    def update_stick_button_text(self, stick_button, note_window):
        if note_window.isVisible():
            stick_button.setText("Unstick")
        else:
            stick_button.setText("Stick")

    def toggle_note(self, note_window, stick_button):
        if note_window.isVisible():
            note_window.hide()
        else:
            note_window.setWindowFlag(Qt.WindowStaysOnTopHint, True)
            note_window.show()
        self.update_stick_button_text(stick_button, note_window)

    def show_details(self, row, column):
        note_id = int(self.table.item(row, 1).text())
        note_window = next(
            (
                note_window
                for note_window_id, note_window in (
                    self.active_notewindows.items()
                )
                if note_window.note.id == note_id
            ),
            None,
        )

        if note_window:
            details_dialog = QDialog(self)
            details_dialog.setWindowTitle(f"Note Details - ID: {note_id}")
            details_layout = QVBoxLayout()

            text_edit = QTextEdit()
            text_edit.setText(note_window.note.text)
            text_edit.setReadOnly(True)
            details_layout.addWidget(text_edit)

            priority_label = QLabel(
                f"Priority: {note_window.note.priority}"
            )
            details_layout.addWidget(priority_label)

            timer_enabled = bool(note_window.note.timer_enabled)
            timer_label = QLabel(
                f"Timer Enabled: {'Yes' if timer_enabled else 'No'}"
            )
            details_layout.addWidget(timer_label)

            if note_window.note.timer_enabled:
                timer_time = QDateTime.fromSecsSinceEpoch(
                    note_window.note.timer_time
                )
                timer_time_label = QLabel(
                    f"Timer Time: {timer_time.toString()}"
                )
                details_layout.addWidget(timer_time_label)

            details_dialog.setLayout(details_layout)
            details_dialog.exec_()

    def update_time_remaining(self):
        for row in range(self.table.rowCount()):
            note_id = int(self.table.item(row, 1).text())
            note_window = next(
                (
                    note_window
                    for note_window_id, note_window in (
                        self.active_notewindows.items()
                    )
                    if note_window.note.id == note_id
                ),
                None,
            )
            if note_window and note_window.note.timer_enabled:
                if note_window.note.timer_time is not None:
                    timer_time_epoch = QDateTime.fromSecsSinceEpoch(
                        note_window.note.timer_time
                    ).toMSecsSinceEpoch()
                    current_time_epoch = (
                        QDateTime.currentDateTime().toMSecsSinceEpoch()
                    )
                    time_remaining_ms = timer_time_epoch - current_time_epoch
                    if time_remaining_ms >= 0:
                        days, seconds = divmod(
                            time_remaining_ms // 1000, 24 * 3600
                        )
                        hours, seconds = divmod(seconds, 3600)
                        minutes, seconds = divmod(seconds, 60)
                        time_remaining_str = (
                            f"{int(days)}d {int(hours)}h "
                            f"{int(minutes)}m {int(seconds)}s"
                        )
                    else:
                        time_remaining_str = "Timer Expired"
                    item = self.table.item(row, 4)
                    if item:
                        item.setText(time_remaining_str)
                else:
                    item = self.table.item(row, 4)
                    if item:
                        item.setText("N/A")
