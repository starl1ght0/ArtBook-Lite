from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import (QWidget, QFileDialog, QDialog, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QComboBox,
                           QSlider, QCheckBox, QSpinBox, QDialogButtonBox)
import os

class ImageHandler:
    """Class to handle image import and manipulation operations"""
    
    @staticmethod
    def import_image(parent):
        """Open file dialog and return selected image path"""
        file_path, _ = QFileDialog.getOpenFileName(
            parent,
            "Import Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*.*)"
        )
        if file_path:
            return file_path
        return None
    
    @staticmethod
    def load_image(file_path):
        """Load image from path and return QImage"""
        if not os.path.exists(file_path):
            return None
        
        image = QImage(file_path)
        if image.isNull():
            return None
            
        return image
        
    @staticmethod
    def scale_image(image, width, height, maintain_aspect=True):
        """Scale image to target dimensions"""
        if maintain_aspect:
            return image.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        else:
            return image.scaled(width, height, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            
    @staticmethod
    def position_image(canvas_image, import_image, x, y):
        """Position the imported image on canvas at the specified coordinates"""
        painter = QPainter(canvas_image)
        painter.drawImage(x, y, import_image)
        painter.end()
        return canvas_image


class ImageImportDialog(QDialog):
    """Dialog to configure image importing options"""
    
    def __init__(self, parent=None, image_path=None, canvas_width=0, canvas_height=0):
        super().__init__(parent)
        self.setWindowTitle("Import Image Options")
        self.setMinimumWidth(400)
        
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.image_path = image_path
        self.original_image = QImage(image_path)
        
        # Default values
        self.maintain_aspect = True
        self.image_width = min(self.original_image.width(), canvas_width)
        self.image_height = min(self.original_image.height(), canvas_height)
        self.x_position = 0
        self.y_position = 0
        
        # Setup UI
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Image information
        info_label = QLabel(f"Original size: {self.original_image.width()}×{self.original_image.height()} px")
        layout.addWidget(info_label)
        
        # Preview (could be implemented with label and pixmap)
        preview_label = QLabel("Preview:")
        layout.addWidget(preview_label)
        
        self.preview_image = QLabel()
        self.preview_image.setAlignment(Qt.AlignCenter)
        self.preview_image.setMinimumHeight(200)
        self.preview_image.setStyleSheet("background-color: #fff; border: 1px solid #aaa;")
        layout.addWidget(self.preview_image)
        
        # Scaling options
        scaling_layout = QHBoxLayout()
        
        # Size control
        size_group = QVBoxLayout()
        
        # Maintain aspect ratio
        self.aspect_check = QCheckBox("Maintain aspect ratio")
        self.aspect_check.setChecked(self.maintain_aspect)
        self.aspect_check.stateChanged.connect(self.on_aspect_changed)
        size_group.addWidget(self.aspect_check)
        
        scaling_layout.addLayout(size_group)
        layout.addLayout(scaling_layout)
        
        # Position controls
        position_layout = QHBoxLayout()
        position_layout.addWidget(QLabel("Position:"))
        
        # X position
        x_layout = QHBoxLayout()
        x_layout.addWidget(QLabel("X:"))
        self.x_spin = QSpinBox()
        self.x_spin.setRange(0, self.canvas_width - self.image_width)
        self.x_spin.setValue(self.x_position)
        self.x_spin.valueChanged.connect(self.on_position_changed)
        x_layout.addWidget(self.x_spin)
        position_layout.addLayout(x_layout)
        
        # Y position
        y_layout = QHBoxLayout()
        y_layout.addWidget(QLabel("Y:"))
        self.y_spin = QSpinBox()
        self.y_spin.setRange(0, self.canvas_height - self.image_height)
        self.y_spin.setValue(self.y_position)
        self.y_spin.valueChanged.connect(self.on_position_changed)
        y_layout.addWidget(self.y_spin)
        position_layout.addLayout(y_layout)
        
        layout.addLayout(position_layout)
        
        # Centering button
        center_btn = QPushButton("Center Image")
        center_btn.clicked.connect(self.center_image)
        layout.addWidget(center_btn)
        
        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Update preview
        self.update_preview()
    
    def on_width_changed(self, value):
        self.image_width = value
        if self.maintain_aspect and not self.width_spin.isSliderDown():
            # Calculate new height maintaining aspect ratio
            aspect = self.original_image.width() / self.original_image.height()
            self.image_height = int(value / aspect)
            self.height_spin.blockSignals(True)
            self.height_spin.setValue(self.image_height)
            self.height_spin.blockSignals(False)
        
        # Update position limits
        self.x_spin.setMaximum(self.canvas_width - self.image_width)
        self.update_preview()
    
    def on_height_changed(self, value):
        self.image_height = value
        if self.maintain_aspect and not self.height_spin.isSliderDown():
            # Calculate new width maintaining aspect ratio
            aspect = self.original_image.width() / self.original_image.height()
            self.image_width = int(value * aspect)
            self.width_spin.blockSignals(True)
            self.width_spin.setValue(self.image_width)
            self.width_spin.blockSignals(False)
        
        # Update position limits
        self.y_spin.setMaximum(self.canvas_height - self.image_height)
        self.update_preview()
    
    def on_aspect_changed(self, state):
        self.maintain_aspect = state == Qt.Checked
        if self.maintain_aspect:
            # Adjust height to match width with aspect ratio
            aspect = self.original_image.width() / self.original_image.height()
            self.image_height = int(self.image_width / aspect)
            self.height_spin.blockSignals(True)
            self.height_spin.setValue(self.image_height)
            self.height_spin.blockSignals(False)
            
            # Update position limits
            self.y_spin.setMaximum(self.canvas_height - self.image_height)
        self.update_preview()
    
    def on_position_changed(self):
        self.x_position = self.x_spin.value()
        self.y_position = self.y_spin.value()
        self.update_preview()
    
    def center_image(self):
        self.x_position = max(0, (self.canvas_width - self.image_width) // 2)
        self.y_position = max(0, (self.canvas_height - self.image_height) // 2)
        self.x_spin.setValue(self.x_position)
        self.y_spin.setValue(self.y_position)
        self.update_preview()
    
    def update_preview(self):
        # Create a small representation of the canvas with the image placed on it
        canvas_pixmap = QPixmap(min(self.canvas_width, 380), min(self.canvas_height, 180))
        canvas_pixmap.fill(Qt.white)
        
        # Scale image for preview
        scale_factor = min(canvas_pixmap.width() / self.canvas_width, 
                           canvas_pixmap.height() / self.canvas_height)
        
        # Draw the imported image on the preview
        scaled_image = self.original_image.scaled(
            self.image_width, self.image_height, 
            Qt.KeepAspectRatio if self.maintain_aspect else Qt.IgnoreAspectRatio, 
            Qt.SmoothTransformation
        )
        
        # Draw on the preview canvas
        preview_x = int(self.x_position * scale_factor)
        preview_y = int(self.y_position * scale_factor)
        preview_width = int(self.image_width * scale_factor)
        preview_height = int(self.image_height * scale_factor)
        
        painter = QPainter(canvas_pixmap)
        painter.drawImage(
            QRect(preview_x, preview_y, preview_width, preview_height),
            scaled_image
        )
        painter.end()
        
        self.preview_image.setPixmap(canvas_pixmap)
    
    def get_import_config(self):
        """Return the configuration for importing the image"""
        return {
            'width': self.image_width,
            'height': self.image_height,
            'x': self.x_position,
            'y': self.y_position,
            'maintain_aspect': self.maintain_aspect,
            'path': self.image_path
        }
