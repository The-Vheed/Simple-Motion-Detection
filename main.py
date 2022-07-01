# -*- coding: utf-8 -*-

# All detected movements or changes are saved in a 'detected.avi' file in the same directory as the script
# IP Cameras can also be easily integrated with the code for seamless motion detection and automated recording
# All recordings are time-lapsed for easy analysis
# Alarm is automatically triggered when the motion has been confirmed as valid

# Form implementation generated from reading ui file 'MotionDetector.ui'

import os
from pathlib import Path
import PyQt5

from PyQt5 import QtCore, QtGui, QtWidgets
import cv2
import numpy as np
import pygame

os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = os.fspath(
    Path(PyQt5.__file__).resolve().parent / "Qt5" / "plugins"
)

file_name = 'detected'
cap = cv2.VideoCapture(0)
comparison_mode = 'grey'

diff_thresh = 60
amt_thresh = 10
line_width = 2


# noinspection PyUnresolvedReferences
class motiondetect(QtCore.QObject):
    amt_percentage = QtCore.pyqtSignal()
    view_change = QtCore.pyqtSignal()
    diff_percent = 0

    def __init__(self, window):
        super().__init__()
        self.window = window

    @QtCore.pyqtSlot()
    def detect(self):

        pygame.init()

        # Loading and playing background music:
        pygame.mixer.music.load('assets/beep.wav')

        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(str(file_name) + '.avi', fourcc, 30.0, (640, 480))

        def difference(array1: np.array, array2: np.array):
            diffs = []
            list1 = array1.tolist()
            list2 = array2.tolist()
            if comparison_mode == 'grey':
                thresh = ui.diff_thresh_slider.sliderPosition()
                for y in range(len(list1)):
                    for x in range(len(list1[y])):
                        diff = abs(list1[y][x] - list2[y][x])
                        if diff > thresh:
                            diffs.append([y, x])
            else:
                r = 0
                g = 0
                b = 0
                thresh = ui.diff_thresh_slider.sliderPosition()
                for y in range(len(list1)):
                    for x in range(len(list1[y])):
                        # diff = abs(list1[y][x] - list2[y][x])
                        # diff = abs(list1[y][x][0] - list2[y][x][0])+abs(list1[y][x][1] - list2[y][x][1])+abs(list1[y][x][2] - list2[y][x][2])
                        for c in range(array1.shape[2]):
                            if c == 0:
                                b = abs(int(array1[y, x, c]) - int(array2[y, x, c]))
                            if c == 1:
                                g = abs(int(array1[y, x, c]) - int(array2[y, x, c]))
                            if c == 2:
                                r = abs(int(array1[y, x, c]) - int(array2[y, x, c]))
                        diff = b + g + r
                        if diff > thresh:
                            diffs.append([y, x])

            return np.array(diffs)

        def get_bounding_rect(list1):
            x1 = 640
            x2 = 0
            y1 = 480
            y2 = 0
            for i in range(len(list1)):
                if list1[i][1] > x2:
                    x2 = list1[i][1]
                if list1[i][1] < x1:
                    x1 = list1[i][1]
                if list1[i][0] > y2:
                    y2 = list1[i][0]
                if list1[i][0] < y1:
                    y1 = list1[i][0]
            # print([(x1, y1), (x2, y2)])
            return [(x1, y1), (x2, y2)]

        prev = 0
        count = 0
        playing = False
        numofdetections = 0
        ret, frame = cap.read()
        self.size = frame.size / 75
        self.amt_thresh = amt_thresh

        while True:
            try:
                count += 1
                # Capture frame-by-frame
                ret, frame = cap.read()
                view = frame
                # Our operations on the frame come here
                # Display the resulting frame
                if ret:
                    if comparison_mode == 'grey':
                        color_modded = cv2.cvtColor(frame, cv2.COLOR_BGR2color_modded)
                    else:
                        color_modded = frame.copy()
                    if count == 1:
                        count = 0
                        if type(prev) == int:
                            prev = color_modded.copy()
                            continue
                        diff = difference(color_modded, prev)
                        std = 0
                        # if diff.shape[0] > 0:
                        #     std = np.array(diff).std(0).mean()
                        prev = color_modded.copy()
                        # view = color_modded.copy()
                        # bounding_rect = get_bounding_rect(diff)
                        # diff_size = ((bounding_rect[1][0] - bounding_rect[0][0]) * (
                        #         bounding_rect[1][1] - bounding_rect[0][1]))
                        self.diff_percent = int(diff.size / self.size * 100)
                        # ui.amt_percentage.setValue(diff_percent)
                        self.amt_percentage.emit()
                        if self.diff_percent > self.amt_thresh:
                            ui_line_slider_pos = ui.line_width_slider.sliderPosition()
                            if ui_line_slider_pos > 0:
                                bounding_rect = get_bounding_rect(diff)
                                view = cv2.rectangle(frame, bounding_rect[0], bounding_rect[1], (0, 0, 255),
                                                     ui_line_slider_pos)
                            numofdetections += 1
                            if std < 60:
                                if not playing == True and numofdetections > 2:
                                    playing = True
                                    pygame.mixer.music.play(-1, 0.0)
                                if numofdetections > 0:
                                    out.write(view)
                        else:
                            if numofdetections > 0:
                                numofdetections -= 1
                            elif numofdetections == 0:
                                playing = False
                                pygame.mixer.music.stop()

                    # cv2.imshow('frame', view)
                    self.curr_view = view.copy()
                    # height, width, channel = self.curr_view.shape
                    # bytesPerLine = 3 * width
                    # qImg = QtGui.QImage(view.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888).rgbSwapped()
                    # self.window.setPixmap(QtGui.QPixmap(qImg))
                    self.view_change.emit()
                # if cv2.waitKey(1) & 0xFF == ord('q'):
                #     break
            except KeyboardInterrupt:
                break

        # When everything done, release the capture
        cap.release()
        out.release()
        cv2.destroyAllWindows()


class ImageWidget(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        # self.setScaledContents(True)
        # self.sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        # self.sizePolicy.setHeightForWidth(True)
        # self.setSizePolicy(self.sizePolicy)

    def hasHeightForWidth(self):
        return self.pixmap() is not None

    def heightForWidth(self, a0: int) -> int:
        if self.pixmap():
            return int(a0 * (self.pixmap().height() / self.pixmap().width()))


# noinspection PyUnresolvedReferences
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 759)
        font = QtGui.QFont()
        font.setPointSize(20)
        MainWindow.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("assets/icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        MainWindow.setWindowIcon(icon)
        MainWindow.setAutoFillBackground(False)
        MainWindow.setStyleSheet("background-color: rgb(46, 52, 54);")
        MainWindow.setAnimated(True)
        MainWindow.setDocumentMode(False)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.main_vl = QtWidgets.QVBoxLayout()
        self.main_vl.setContentsMargins(10, 10, 10, 10)
        self.main_vl.setSpacing(3)
        self.main_vl.setObjectName("main_vl")
        # self.title = QtWidgets.QLabel(self.centralwidget)
        # self.title.setMinimumSize(QtCore.QSize(0, 35))
        # self.title.setMaximumSize(QtCore.QSize(16777215, 30))
        # font = QtGui.QFont()
        # font.setPointSize(26)
        # font.setBold(True)
        # font.setUnderline(False)
        # font.setWeight(75)
        # font.setStrikeOut(False)
        # self.title.setFont(font)
        # self.title.setAutoFillBackground(False)
        # self.title.setStyleSheet("color: rgb(238, 238, 236);")
        # self.title.setScaledContents(False)
        # self.title.setAlignment(QtCore.Qt.AlignCenter)
        # self.title.setObjectName("title")
        # self.main_vl.addWidget(self.title)
        self.view = ImageWidget(self.centralwidget)
        self.view.setMinimumSize(QtCore.QSize(640, 480))
        # self.view.setSizeIncrement(QtCore.QSize(4, 3))
        self.view.setStyleSheet("color: rgb(238, 238, 236);\n"
                                "border-color: rgb(204, 0, 0);")
        self.view.setText("")
        self.view.setPixmap(QtGui.QPixmap("assets/L.jpeg"))
        # self.view.setScaledContents(True)
        self.view.setAlignment(QtCore.Qt.AlignCenter)
        self.view.setObjectName("view")
        self.main_vl.addWidget(self.view)
        self.diff_thresh_line_width = QtWidgets.QHBoxLayout()
        self.diff_thresh_line_width.setObjectName("diff_thresh_line_width")
        self.diff_thresh = QtWidgets.QVBoxLayout()
        self.diff_thresh.setContentsMargins(4, 4, 4, 4)
        self.diff_thresh.setObjectName("diff_thresh")
        self.diff_thresh_hl = QtWidgets.QHBoxLayout()
        self.diff_thresh_hl.setObjectName("diff_thresh_hl")
        self.diff_thresh_label = QtWidgets.QLabel(self.centralwidget)
        self.diff_thresh_label.setMinimumSize(QtCore.QSize(200, 30))
        self.diff_thresh_label.setMaximumSize(QtCore.QSize(200, 30))
        self.diff_thresh_label.setStyleSheet("color: rgb(211, 215, 207);")
        self.diff_thresh_label.setAlignment(QtCore.Qt.AlignCenter)
        self.diff_thresh_label.setObjectName("diff_thresh_label")
        self.diff_thresh_hl.addWidget(self.diff_thresh_label)
        self.diff_thresh_value = QtWidgets.QLabel(self.centralwidget)
        self.diff_thresh_value.setMinimumSize(QtCore.QSize(0, 30))
        self.diff_thresh_value.setMaximumSize(QtCore.QSize(200, 30))
        self.diff_thresh_value.setStyleSheet("color: rgb(211, 215, 207);")
        self.diff_thresh_value.setTextFormat(QtCore.Qt.AutoText)
        self.diff_thresh_value.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.diff_thresh_value.setObjectName("diff_thresh_value")
        self.diff_thresh_hl.addWidget(self.diff_thresh_value)
        self.diff_thresh.addLayout(self.diff_thresh_hl)
        self.diff_thresh_slider = QtWidgets.QSlider(self.centralwidget)
        self.diff_thresh_slider.setMaximumSize(QtCore.QSize(500, 16777215))
        self.diff_thresh_slider.setMinimum(1)
        self.diff_thresh_slider.setMaximum(255)
        self.diff_thresh_slider.setSliderPosition(40)
        self.diff_thresh_slider.setOrientation(QtCore.Qt.Horizontal)
        self.diff_thresh_slider.setInvertedAppearance(False)
        self.diff_thresh_slider.setInvertedControls(False)
        self.diff_thresh_slider.setTickPosition(QtWidgets.QSlider.NoTicks)
        self.diff_thresh_slider.setTickInterval(0)
        self.diff_thresh_slider.setObjectName("diff_thresh_slider")
        self.diff_thresh.addWidget(self.diff_thresh_slider)
        self.diff_thresh_line_width.addLayout(self.diff_thresh)
        self.line_width = QtWidgets.QVBoxLayout()
        self.line_width.setObjectName("line_width")
        self.line_width_hl = QtWidgets.QHBoxLayout()
        self.line_width_hl.setObjectName("line_width_hl")
        self.line_width_label = QtWidgets.QLabel(self.centralwidget)
        self.line_width_label.setMinimumSize(QtCore.QSize(0, 30))
        self.line_width_label.setMaximumSize(QtCore.QSize(150, 30))
        self.line_width_label.setStyleSheet("color: rgb(211, 215, 207);")
        self.line_width_label.setAlignment(QtCore.Qt.AlignCenter)
        self.line_width_label.setObjectName("line_width_label")
        self.line_width_hl.addWidget(self.line_width_label)
        self.line_width_value = QtWidgets.QLabel(self.centralwidget)
        self.line_width_value.setMinimumSize(QtCore.QSize(0, 30))
        self.line_width_value.setMaximumSize(QtCore.QSize(50, 30))
        self.line_width_value.setStyleSheet("color: rgb(211, 215, 207);")
        self.line_width_value.setAlignment(QtCore.Qt.AlignCenter)
        self.line_width_value.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.line_width_value.setObjectName("line_width_value")
        self.line_width_hl.addWidget(self.line_width_value)
        self.line_width.addLayout(self.line_width_hl)
        self.line_width_slider = QtWidgets.QSlider(self.centralwidget)
        self.line_width_slider.setMaximumSize(QtCore.QSize(364, 16777215))
        self.line_width_slider.setMinimum(0)
        self.line_width_slider.setMaximum(50)
        self.line_width_slider.setPageStep(1)
        self.line_width_slider.setSliderPosition(2)
        self.line_width_slider.setOrientation(QtCore.Qt.Horizontal)
        self.line_width_slider.setObjectName("line_width_slider")
        self.line_width.addWidget(self.line_width_slider)
        self.diff_thresh_line_width.addLayout(self.line_width)
        self.main_vl.addLayout(self.diff_thresh_line_width)
        self.amt_thresh = QtWidgets.QVBoxLayout()
        self.amt_thresh.setContentsMargins(4, 4, 4, 4)
        self.amt_thresh.setObjectName("amt_thresh")
        self.amt_thresh_hl = QtWidgets.QHBoxLayout()
        self.amt_thresh_hl.setObjectName("amt_thresh_hl")
        self.amt_thresh_label = QtWidgets.QLabel(self.centralwidget)
        self.amt_thresh_label.setMinimumSize(QtCore.QSize(200, 30))
        self.amt_thresh_label.setMaximumSize(QtCore.QSize(200, 30))
        self.amt_thresh_label.setStyleSheet("color: rgb(211, 215, 207);")
        self.amt_thresh_label.setAlignment(QtCore.Qt.AlignCenter)
        self.amt_thresh_label.setObjectName("amt_thresh_label")
        self.amt_thresh_hl.addWidget(self.amt_thresh_label)
        self.amt_thresh_value = QtWidgets.QLabel(self.centralwidget)
        self.amt_thresh_value.setMinimumSize(QtCore.QSize(0, 30))
        self.amt_thresh_value.setMaximumSize(QtCore.QSize(200, 30))
        self.amt_thresh_value.setStyleSheet("color: rgb(211, 215, 207);")
        self.amt_thresh_value.setTextFormat(QtCore.Qt.AutoText)
        self.amt_thresh_value.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.amt_thresh_value.setObjectName("amt_thresh_value")
        self.amt_thresh_hl.addWidget(self.amt_thresh_value)
        self.amt_thresh.addLayout(self.amt_thresh_hl)
        self.amt_thresh_slider = QtWidgets.QSlider(self.centralwidget)
        self.amt_thresh_slider.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.amt_thresh_slider.setMinimum(0)
        self.amt_thresh_slider.setMaximum(100)
        self.amt_thresh_slider.setSingleStep(1)
        self.amt_thresh_slider.setPageStep(10)
        self.amt_thresh_slider.setSliderPosition(amt_thresh)
        self.amt_thresh_slider.setOrientation(QtCore.Qt.Horizontal)
        self.amt_thresh_slider.setTickPosition(QtWidgets.QSlider.NoTicks)
        self.amt_thresh_slider.setTickInterval(0)
        self.amt_thresh_slider.setObjectName("amt_thresh_slider")
        self.amt_thresh.addWidget(self.amt_thresh_slider)
        self.amt_percentage = QtWidgets.QProgressBar(self.centralwidget)
        self.amt_percentage.setMinimumSize(QtCore.QSize(0, 20))
        self.amt_percentage.setMaximumSize(QtCore.QSize(16777215, 20))
        self.amt_percentage.setAutoFillBackground(False)
        self.amt_percentage.setStyleSheet("color: rgb(238, 238, 236);\n"
                                          "selection-background-color: rgb(255, 0, 0);\n"
                                          "background-color: rgb(0, 255, 0);")
        self.amt_percentage.setProperty("value", 0)
        self.amt_percentage.setTextVisible(True)
        self.amt_percentage.setOrientation(QtCore.Qt.Horizontal)
        self.amt_percentage.setInvertedAppearance(False)
        self.amt_percentage.setTextDirection(QtWidgets.QProgressBar.TopToBottom)
        self.amt_percentage.setObjectName("amt_percentage")
        self.amt_thresh.addWidget(self.amt_percentage)
        self.main_vl.addLayout(self.amt_thresh)
        self.verticalLayout_2.addLayout(self.main_vl)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.diff_thresh_slider.valueChanged['int'].connect(self.diff_thresh_value.setNum)  # type: ignore
        self.amt_thresh_slider.sliderMoved.connect(self.change_amt_thresh)  # type: ignore
        self.line_width_slider.valueChanged['int'].connect(self.line_width_value.setNum)  # type: ignore
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Motion Detector"))
        # self.title.setText(_translate("MainWindow", "CAMERA FEED"))
        self.diff_thresh_label.setText(_translate("MainWindow", "Difference Threshold:"))
        self.diff_thresh_value.setText(_translate("MainWindow", str(self.diff_thresh_slider.sliderPosition())))
        self.line_width_label.setText(_translate("MainWindow", "Line Width:"))
        self.line_width_value.setText(_translate("MainWindow", str(self.line_width_slider.sliderPosition())))
        self.amt_thresh_label.setText(_translate("MainWindow", "Amount Threshold:"))
        self.amt_thresh_value.setText(_translate("MainWindow", str(self.amt_thresh_slider.sliderPosition())))
        self.amt_percentage.setFormat(_translate("MainWindow", "Amount: %p%"))

    def detect(self):
        self.detector = motiondetect(self.view)
        self.thread = QtCore.QThread()
        self.detector.moveToThread(self.thread)
        self.thread.started.connect(self.detector.detect)
        self.thread.start()
        self.detector.amt_percentage.connect(self.change_amt_percentage)
        self.detector.view_change.connect(self.change_view)
        # motiondetector = motiondetect(self.view)
        # motiondetector.start()
        # print('Detecting')

    def change_amt_thresh(self):
        amt_thresh_slider_position = self.amt_thresh_slider.value()
        self.amt_thresh_value.setText(str(amt_thresh_slider_position) + '%')
        self.detector.amt_thresh = amt_thresh_slider_position

    def change_amt_percentage(self):
        # sleep(0.1)
        self.amt_percentage.setValue(self.detector.diff_percent)

    def change_view(self):
        view = self.detector.curr_view
        height, width, channel = view.shape
        bytesPerLine = 3 * width
        qImg = QtGui.QImage(view.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888).rgbSwapped()
        self.view.setPixmap(QtGui.QPixmap(qImg))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    ui.detect()
    sys.exit(app.exec_())
