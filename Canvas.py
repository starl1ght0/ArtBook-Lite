from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import (QMainWindow, QFileDialog, QApplication,
                            QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                            QLabel, QFrame, QColorDialog, QSlider, QButtonGroup,
                            QShortcut, QSizePolicy, QScrollArea)

class Canvas(QWidget):
    def __init__(self, parent=None, width=800, height=600):
        super().__init__(parent)
        # Set fixed dimensions for the canvas
        self.canvas_width = width
        self.canvas_height = height
        self.setFixedSize(self.canvas_width, self.canvas_height)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border: 2px solid #555555;
                border-radius: 4px;
            }
        """)
        self.image = QImage(QSize(self.canvas_width, self.canvas_height), QImage.Format_RGB32)
        self.image.fill(Qt.white)
        self.drawing = False
        self.brushSize = 5
        self.brushColor = QColor(Qt.black)
        self.lastPoint = QPoint()
        self.currentTool = "pencil"
        self.lassoPoints = []
        self.isLassoActive = False
        self.undo_stack = []
        self.redo_stack = []
        self.max_undo_steps = 5

    def saveState(self):
        """Save current state to undo stack"""
        if len(self.undo_stack) >= self.max_undo_steps:
            self.undo_stack.pop(0)
        self.undo_stack.append(self.image.copy())
        self.redo_stack.clear()

    def undo(self):
        """Undo last action"""
        if self.undo_stack:
            if len(self.redo_stack) >= self.max_undo_steps:
                self.redo_stack.pop(0)
            self.redo_stack.append(self.image.copy())
            self.image = self.undo_stack.pop().copy()
            self.update()

    def redo(self):
        """Redo last undone action"""
        if self.redo_stack:
            if len(self.undo_stack) >= self.max_undo_steps:
                self.undo_stack.pop(0)
            self.undo_stack.append(self.image.copy())
            self.image = self.redo_stack.pop().copy()
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(self.rect(), self.image, self.image.rect())

        if self.isLassoActive and len(self.lassoPoints) > 1:
            painter.setPen(QPen(Qt.blue, 1, Qt.DashLine))
            painter.drawPolygon(QPolygon(self.lassoPoints))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.lastPoint = event.pos()

            if self.currentTool == "fill":
                self.saveState()
                self.fill(event.pos())
                self.drawing = False
            elif self.currentTool == "lasso":
                self.lassoPoints = [event.pos()]
                self.isLassoActive = True

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) and self.drawing:
            if self.currentTool == "pencil":
                painter = QPainter(self.image)
                painter.setPen(QPen(self.brushColor, self.brushSize,
                                    Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                painter.drawLine(self.lastPoint, event.pos())
                self.lastPoint = event.pos()
                self.update()
            elif self.currentTool == "eraser":
                painter = QPainter(self.image)
                painter.setPen(QPen(Qt.white, self.brushSize,
                                    Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                painter.drawLine(self.lastPoint, event.pos())
                self.lastPoint = event.pos()
                self.update()
            elif self.currentTool == "lasso":
                self.lassoPoints.append(event.pos())
                self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing:
            self.drawing = False
            if self.currentTool == "lasso" and len(self.lassoPoints) > 2:
                self.saveState()
                self.processLassoSelection()
            elif self.currentTool in ["pencil", "eraser"]:
                self.saveState()
            self.lassoPoints = []
            self.isLassoActive = False
            self.update()

    def fill(self, point):
        """Flood fill implementation"""
        image = self.image
        target_color = image.pixelColor(point)
        fill_color = self.brushColor

        if target_color == fill_color:
            return

        stack = [point]
        width, height = image.width(), image.height()
        visited = set()

        while stack:
            n = stack.pop()
            if not (0 <= n.x() < width and 0 <= n.y() < height):
                continue

            if (n.x(), n.y()) in visited:
                continue

            if image.pixelColor(n) != target_color:
                continue

            image.setPixelColor(n, fill_color)
            visited.add((n.x(), n.y()))

            stack.append(QPoint(n.x() + 1, n.y()))
            stack.append(QPoint(n.x() - 1, n.y()))
            stack.append(QPoint(n.x(), n.y() + 1))
            stack.append(QPoint(n.x(), n.y() - 1))

        self.update()

    def processLassoSelection(self):
        """Process the selected area with lasso tool"""
        if len(self.lassoPoints) > 2:
            painter = QPainter(self.image)
            painter.setPen(QPen(self.brushColor, self.brushSize,
                                Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawPolygon(QPolygon(self.lassoPoints))
            self.update()
            
    def setCanvasSize(self, width, height):
        """Set a new canvas size while preserving content"""
        self.saveState()  # Save current state for undo
        
        # Create new image with the new dimensions
        new_image = QImage(QSize(width, height), QImage.Format_RGB32)
        new_image.fill(Qt.white)
        
        # Draw the old image onto the new one (centered if larger, cropped if smaller)
        painter = QPainter(new_image)
        
        # Calculate position to center the old image on the new canvas
        x_offset = max(0, (width - self.canvas_width) // 2)
        y_offset = max(0, (height - self.canvas_height) // 2)
        
        painter.drawImage(QPoint(x_offset, y_offset), self.image)
        painter.end()
        
        # Update canvas properties
        self.canvas_width = width
        self.canvas_height = height
        self.setFixedSize(width, height)
        self.image = new_image
        self.update()
        
    def getCanvasSize(self):
        """Return the current canvas dimensions"""
        return (self.canvas_width, self.canvas_height)

    def clear(self):
        self.saveState()
        self.image.fill(Qt.white)
        self.update()
        
    def addImage(self, imported_image, x=0, y=0):
        """Add an imported QImage to the canvas at position (x,y)"""
        self.saveState()
        painter = QPainter(self.image)
        painter.drawImage(QPoint(x, y), imported_image)
        painter.end()
        self.update()
