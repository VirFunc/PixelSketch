from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *


class Canvas(QDockWidget):
    def __init__(self, initImg, *, title, parent):
        super().__init__(title, parent)

        # when  dock widget tab is changed
        # the visibility of the dock widget is changed
        # change the current canvas according to this
        self.visibilityChanged.connect(parent.currCanvasChanged)

        # canvas states
        self.fileName = title
        self.filePath = ""
        self.isSaved = True

        # image used to present
        self.image = initImg

        # double buffer
        self.tempImage = QImage(self.image)

        self.__dockContent = QWidget()

        self.frame = QFrame(self.__dockContent)
        self.frame.setFrameShape(QFrame.Box)
        self.frame.setFrameShadow(QFrame.Plain)
        self.frame.installEventFilter(self)

        self.__gridLayout = QGridLayout(self.__dockContent)
        self.__gridLayout.setContentsMargins(2, 2, 2, 2)
        self.__gridLayout.addWidget(self.frame, 0, 0, 1, 1)

        self.setWidget(self.__dockContent)
        parent.addDockWidget(Qt.LeftDockWidgetArea, self)

        # capture Canvas widget event
        self.frame.installEventFilter(parent)
        self.frame.setMouseTracking(True)

        # change dock widget back ground color
        __defaultWindowBackColor = QColor(150, 150, 150)
        pal = QPalette(self.palette())
        pal.setColor(QPalette.Background, __defaultWindowBackColor)
        self.setAutoFillBackground(True)
        self.setPalette(pal)

        self.__painter = QPainter()

        self.__begin = False

        # get focus event
        self.setFocusPolicy(Qt.StrongFocus)

    @classmethod
    def new(cls, width, height, imgFormat=QImage.Format_RGB888, initColor=Qt.white, *, title, parent):
        image = QImage(width, height, imgFormat)
        image.fill(initColor)
        return cls(image, title=title, parent=parent)

    @classmethod
    def open(cls, path, *, title, parent):
        image = QImage(path)
        temp = cls(image, title=title, parent=parent)
        temp.filePath = path
        return temp

    def save(self):
        if self.filePath == "":
            # if the file is not opened from disk
            self.filePath, _ = QFileDialog.getSaveFileName(self,
                                                           self.tr("Save"),
                                                           ".\\" + self.fileName + ".jpg",
                                                           "JPEG (*.jpg *.jpeg);;PNG (*.png);;All File Formats (*.*)",
                                                           "JPEG (*.jpg *.jpeg)")
        # if canceled
        if self.filePath != "":
            imgFormat = self.filePath.rpartition(".")[2].upper()
            self.image.save(self.filePath, imgFormat)
            self.saved()

    def saveAs(self):
        filePath, _ = QFileDialog.getSaveFileName(self,
                                                  self.tr("Save"),
                                                  self.filePath,
                                                  "JPEG (*.jpg *.jpeg);;PNG (*.png);;All File Formats (*.*)",
                                                  "JPEG (*.jpg *.jpeg)")
        if filePath != "":
            imgFormat = filePath.rpartition(".")[2].upper()
            self.image.save(filePath, imgFormat)
            self.saved()

    def eventFilter(self, watched, event):
        if watched == self.frame and event.type() == QEvent.Paint:
            self.__painter.begin(self.frame)

            if self.__begin:
                self.__painter.drawImage(1, 1, self.tempImage)
                self.tempImage = self.image.copy()
            else:
                self.__painter.drawImage(1, 1, self.image)

            self.__painter.end()
        return False

    def beginDblBuffer(self):
        self.__begin = True

    def endDblBuffer(self):
        self.__begin = False

    def getImage(self):
        self.updated()

        if self.__begin:
            return self.tempImage
        else:
            return self.image

    def updated(self):
        if self.isSaved is True:
            self.isSaved = False
            self.setWindowTitle(self.fileName + " *")

    def saved(self):
        if self.isSaved is False:
            self.isSaved = True
            self.setWindowTitle(self.fileName)

    def focusInEvent(self, event):
        self.parent().setCurrCanvas(self)

    def closeEvent(self, event):
        if not self.isSaved:
            button = QMessageBox.warning(self.parent(),
                                         self.tr("Warning"),
                                         "[ " + self.fileName + " ]" +
                                         self.tr(" has been modified but not saved,"
                                                 "want to save now?"),
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)

            # cancel
            if button == QMessageBox.Cancel:
                event.ignore()

            # no
            if button == QMessageBox.No:
                self.parent().removeCanvas(self)
                event.accept()

            # yes
            if button == QMessageBox.Yes:
                self.save()
                self.parent().removeCanvas(self)
                event.accept()

        else:
            self.parent().removeCanvas(self)
