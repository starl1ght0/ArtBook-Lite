from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import (QMainWindow, QFileDialog, QApplication,
                            QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                            QLabel, QFrame, QColorDialog, QSlider, QButtonGroup,
                            QShortcut, QSizePolicy, QScrollArea, QDialog,
                            QSpinBox, QDialogButtonBox, QGroupBox)

from Canvas import Canvas
from ImageHandler import ImageHandler, ImageImportDialog

class CanvasSizeDialog(QDialog):
    """Dialog for changing canvas size"""
    def __init__(self, parent=None, current_width=800, current_height=600):
        super().__init__(parent)
        self.setWindowTitle("Set Canvas Size")
        self.setMinimumWidth(30)
        
        layout = QVBoxLayout(self)
        
        # Width input
        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel("Width:"))
        self.width_spin = QSpinBox()
        self.width_spin.setRange(50, 3000)
        self.width_spin.setValue(current_width)
        self.width_spin.setSuffix(" px")
        width_layout.addWidget(self.width_spin)
        layout.addLayout(width_layout)
        
        # Height input
        height_layout = QHBoxLayout()
        height_layout.addWidget(QLabel("Height:"))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(50, 3000)
        self.height_spin.setValue(current_height)
        self.height_spin.setSuffix(" px")
        height_layout.addWidget(self.height_spin)
        layout.addLayout(height_layout)
        
        # Preset sizes
        presets_group = QGroupBox("Presets")
        presets_layout = QHBoxLayout(presets_group)
        
        preset_sizes = [
            ("HD", 1280, 720),
            ("Square", 800, 800),
            ("A4", 595, 842)
        ]
        
        for name, w, h in preset_sizes:
            btn = QPushButton(name)
            btn.clicked.connect(lambda _, w=w, h=h: self.set_preset(w, h))
            presets_layout.addWidget(btn)
            
        layout.addWidget(presets_group)
        
        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def set_preset(self, width, height):
        self.width_spin.setValue(width)
        self.height_spin.setValue(height)
    
    def get_canvas_size(self):
        return (self.width_spin.value(), self.height_spin.value())

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
        
        # Add scroll area for canvas
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #555555;
            }
            QScrollBar {
                background-color: #444444;
                width: 12px;
                height: 12px;
            }
            QScrollBar::handle {
                background-color: #666666;
                border-radius: 4px;
            }
        """)
        
        # Initialize canvas with default size
        self.canvas = Canvas(width=800, height=600)
        self.scroll_area.setWidget(self.canvas)
        
        canvas_layout = QVBoxLayout(canvas_frame)
        canvas_layout.setContentsMargins(5, 5, 5, 5)
        canvas_layout.addWidget(self.scroll_area)
        
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

        # Canvas settings
        canvas_settings_label = QLabel("Canvas Settings")
        canvas_settings_label.setStyleSheet(section_style)
        tools_layout.addWidget(canvas_settings_label)
        
        resize_canvas_btn = QPushButton("Resize Canvas")
        resize_canvas_btn.clicked.connect(self.showResizeCanvasDialog)
        tools_layout.addWidget(resize_canvas_btn)
        
        # Display current canvas size
        self.canvas_size_label = QLabel(f"Size: {self.canvas.canvas_width}×{self.canvas.canvas_height} px")
        self.canvas_size_label.setStyleSheet("color: #c0c0c0; font-size: 12px;")
        tools_layout.addWidget(self.canvas_size_label)

        # File operations
        file_label = QLabel("File Operations")
        file_label.setStyleSheet(section_style)
        tools_layout.addWidget(file_label)

        save_btn = QPushButton("Save (Ctrl+S)")
        save_btn.clicked.connect(self.save)
        tools_layout.addWidget(save_btn)

        # Import image button
        import_btn = QPushButton("Import Image")
        import_btn.clicked.connect(self.importImage)
        tools_layout.addWidget(import_btn)

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
        QShortcut(QKeySequence("Ctrl+I"), self).activated.connect(self.importImage)
        QShortcut(QKeySequence("Ctrl+R"), self).activated.connect(self.showResizeCanvasDialog)

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
            
    def showResizeCanvasDialog(self):
        """Show dialog to resize canvas"""
        current_width, current_height = self.canvas.getCanvasSize()
        dialog = CanvasSizeDialog(self, current_width, current_height)
        
        if dialog.exec_() == QDialog.Accepted:
            new_width, new_height = dialog.get_canvas_size()
            self.canvas.setCanvasSize(new_width, new_height)
            self.canvas_size_label.setText(f"Size: {new_width}×{new_height} px")
    
    def importImage(self):
        """Import an image onto the canvas"""
        # Get image file path
        image_path = ImageHandler.import_image(self)
        if not image_path:
            return
            
        # Load the image
        image = ImageHandler.load_image(image_path)
        if image is None:
            QMessageBox.critical(self, "Error", "Failed to load image.")
            return
            
        # Show dialog for image import options
        current_width, current_height = self.canvas.getCanvasSize()
        dialog = ImageImportDialog(self, image_path, current_width, current_height)
        
        if dialog.exec_() == QDialog.Accepted:
            config = dialog.get_import_config()
            
            # Scale the image
            scaled_image = ImageHandler.scale_image(
                image, 
                config['width'], 
                config['height'], 
                config['maintain_aspect']
            )
            
            # Add to canvas
            self.canvas.addImage(scaled_image, config['x'], config['y'])
