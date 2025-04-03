from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import (QMainWindow, QFileDialog, QApplication,
                            QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                            QLabel, QFrame, QColorDialog, QSlider, QButtonGroup,
                            QShortcut, QSizePolicy)

from Canvas import Canvas

class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        # Main window settings
        self.setWindowTitle("ArtBook-Lite")
        self.setGeometry(100, 100, 1000, 700)

        # Central widget with dark background
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #3a3a3a;")
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        # Canvas area with dark frame
        canvas_frame = QFrame()
        canvas_frame.setFrameShape(QFrame.StyledPanel)
        canvas_frame.setStyleSheet("""
            QFrame {
                background-color: #555555;
                border-radius: 6px;
                padding: 4px;
            }
        """)
        canvas_layout = QHBoxLayout(canvas_frame)
        canvas_layout.setContentsMargins(0, 0, 0, 0)

        self.canvas = Canvas()
        canvas_layout.addWidget(self.canvas)
        main_layout.addWidget(canvas_frame, stretch=4)

        # Dark tools panel
        tools_panel = QFrame()
        tools_panel.setFrameShape(QFrame.StyledPanel)
        tools_panel.setStyleSheet("""
            QFrame {
                background-color: #444444;
                border: 1px solid #333333;
                border-radius: 6px;
            }
            QPushButton {
                background-color: #505050;
                border: 1px solid #454545;
                border-radius: 4px;
                padding: 8px;
                min-width: 80px;
                color: #e0e0e0;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #585858;
                border: 1px solid #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #404040;
            }
            QPushButton:checked {
                background-color: #606060;
                color: white;
            }
            QLabel {
                font-weight: bold;
                color: #d0d0d0;
                font-size: 13px;
                padding: 4px 0;
            }
            QSlider {
                min-height: 20px;
            }
            QSlider::groove:horizontal {
                height: 6px;
                background: #505050;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                width: 16px;
                height: 16px;
                background: #808080;
                border-radius: 8px;
                margin: -5px 0;
            }
            #colorPreview {
                border: 1px solid #666666;
                border-radius: 4px;
                background-color: #ffffff;
            }
            #undoBtn, #redoBtn {
                min-width: 36px;
                max-width: 36px;
                min-height: 36px;
                max-height: 36px;
                font-size: 14px;
            }
        """)
        tools_panel.setFixedWidth(220)
        main_layout.addWidget(tools_panel)

        # Tools layout
        tools_layout = QVBoxLayout(tools_panel)
        tools_layout.setAlignment(Qt.AlignTop)
        tools_layout.setSpacing(12)
        tools_layout.setContentsMargins(12, 12, 12, 12)

        # Section style
        section_style = """
            font-weight: bold; 
            color: #c0c0c0; 
            font-size: 14px; 
            padding: 6px 0;
            border-bottom: 1px solid #555555;
        """

        # File operations
        file_label = QLabel("File Operations")
        file_label.setStyleSheet(section_style)
        tools_layout.addWidget(file_label)

        save_btn = QPushButton("Save (Ctrl+S)")
        save_btn.clicked.connect(self.save)
        tools_layout.addWidget(save_btn)

        clear_btn = QPushButton("Clear (Ctrl+C)")
        clear_btn.clicked.connect(self.clearCanvas)
        tools_layout.addWidget(clear_btn)

        # Undo/Redo operations
        undo_redo_label = QLabel("History")
        undo_redo_label.setStyleSheet(section_style)
        tools_layout.addWidget(undo_redo_label)

        undo_redo_layout = QHBoxLayout()
        undo_redo_layout.setSpacing(6)

        undo_btn = QPushButton("↩")
        undo_btn.setObjectName("undoBtn")
        undo_btn.setToolTip("Undo (Ctrl+Z)")
        undo_btn.clicked.connect(self.canvas.undo)
        undo_redo_layout.addWidget(undo_btn)

        redo_btn = QPushButton("↪")
        redo_btn.setObjectName("redoBtn")
        redo_btn.setToolTip("Redo (Ctrl+Shift+Z)")
        redo_btn.clicked.connect(self.canvas.redo)
        undo_redo_layout.addWidget(redo_btn)

        tools_layout.addLayout(undo_redo_layout)

        # Drawing tools
        tools_label = QLabel("Drawing Tools")
        tools_label.setStyleSheet(section_style)
        tools_layout.addWidget(tools_label)

        self.tool_group = QButtonGroup()

        tools = [
            ("Pencil", "pencil"),
            ("Eraser", "eraser"),
            ("Fill", "fill"),
            ("Lasso", "lasso")
        ]

        for name, tool_id in tools:
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setChecked(tool_id == "pencil")
            self.tool_group.addButton(btn)
            tools_layout.addWidget(btn)
            btn.clicked.connect(lambda _, t=tool_id: self.setTool(t))

        # Brush size
        size_label = QLabel("Brush Size")
        size_label.setStyleSheet(section_style)
        tools_layout.addWidget(size_label)

        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(1, 50)
        self.size_slider.setValue(5)
        self.size_slider.setTickInterval(5)
        self.size_slider.setTickPosition(QSlider.TicksBelow)
        self.size_slider.valueChanged.connect(self.updateSizeIndicator)
        tools_layout.addWidget(self.size_slider)

        # Current size indicator
        self.size_indicator = QLabel(f"Size: {self.size_slider.value()}px")
        self.size_indicator.setStyleSheet("color: #c0c0c0;")
        tools_layout.addWidget(self.size_indicator)

        # Brush color
        color_label = QLabel("Brush Color")
        color_label.setStyleSheet(section_style)
        tools_layout.addWidget(color_label)

        # Current color preview
        self.color_preview = QLabel()
        self.color_preview.setObjectName("colorPreview")
        self.color_preview.setFixedHeight(30)
        self.updateColorPreview()
        tools_layout.addWidget(self.color_preview)

        # Custom color button
        custom_color_btn = QPushButton("Choose Color")
        custom_color_btn.clicked.connect(self.chooseCustomColor)
        tools_layout.addWidget(custom_color_btn)

        # Add stretch to push all content up
        tools_layout.addStretch()

        # Setup shortcuts
        self.setupShortcuts()

    def setupShortcuts(self):
        QShortcut(QKeySequence("Ctrl+Z"), self).activated.connect(self.canvas.undo)
        QShortcut(QKeySequence("Ctrl+Shift+Z"), self).activated.connect(self.canvas.redo)
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self.save)
        QShortcut(QKeySequence("Ctrl+C"), self).activated.connect(self.clearCanvas)

    def updateSizeIndicator(self, size):
        self.size_indicator.setText(f"Size: {size}px")
        self.canvas.brushSize = size

    def clearCanvas(self):
        self.canvas.clear()

    def setTool(self, tool):
        self.canvas.currentTool = tool

    def updateColorPreview(self):
        self.color_preview.setStyleSheet(f"background-color: {self.canvas.brushColor.name()};")

    def save(self):
        filePath, _ = QFileDialog.getSaveFileName(self, "Save Image", "",
                                                  "PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*)")
        if filePath:
            self.canvas.image.save(filePath)

    def chooseCustomColor(self):
        color = QColorDialog.getColor(self.canvas.brushColor, self, "Select Brush Color")
        if color.isValid():
            self.canvas.brushColor = color
            self.updateColorPreview()