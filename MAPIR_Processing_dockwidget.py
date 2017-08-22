# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MAPIR_ProcessingDockWidget
                                 A QGIS plugin
 Widget for processing images captured by MAPIR cameras
                             -------------------
        begin                : 2016-09-26
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Peau Productions
        email                : ethan@peauproductions.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

os.umask(0)
import sys
import shutil
from PyQt5 import QtCore, QtGui, QtWidgets

import PyQt5.uic as uic

# from qgis.core import QgsMessageLog

from scipy import stats
import numpy as np
import subprocess
import cv2

import hid
import time
import distutils
from distutils import dir_util
from MAPIR_Enums import *
import struct

modpath = os.path.dirname(os.path.realpath(__file__))

# print(str(modpath))
if not os.path.exists(modpath + os.sep + "instring.txt"):
    istr = open(modpath + os.sep + "instring.txt", "w")
    istr.close()
# sys.path.insert(0, modpath)
# if sys.platform == "win32":  # Windows OS
#
#     # pypath = os.path.split(os.path.split(sys.executable)[0])[0] + os.sep + "apps" + os.sep + "Python27"
#     # if not os.path.exists(pypath + os.sep + "Scripts" + os.sep + "exiftool.exe")\
#     #        or not os.path.exists(pypath + os.sep + "Scripts" + os.sep + "dcraw.exe")\
#     #        or not os.path.exists(pypath + os.sep + "Scripts" + os.sep + "cygwin1.dll")\
#     #        or not os.path.exists(pypath + os.sep + "Lib" + os.sep + "site-packages" + os.sep + "exiftool.py")\
#     #        or not os.path.exists(pypath + os.sep + "Lib" + os.sep + "site-packages" + os.sep + "exiftool.pyc")\
#     #        or not os.path.exists(pypath + os.sep + "Lib" + os.sep + "site-packages" + os.sep + "cv2.pyd"):
#     #    os.chmod(pypath,0777)
#     #    shutil.copy(modpath + os.sep + "exiftool.exe", pypath + os.sep + "Scripts")
#     #    shutil.copy(modpath + os.sep + "dcraw.exe", pypath + os.sep + "Scripts")
#     #    shutil.copy(modpath + os.sep + "cygwin1.dll", pypath + os.sep + "Scripts")
#     #    shutil.copy(modpath + os.sep + "exiftool.py", pypath + os.sep + "Lib" + os.sep + "site-packages")
#     #    shutil.copy(modpath + os.sep + "exiftool.pyc", pypath + os.sep + "Lib" + os.sep + "site-packages")
#     #    shutil.copy(modpath + os.sep + "cv2.pyd", pypath + os.sep + "Lib" + os.sep + "site-packages")
#
# elif sys.platform == "darwin":
#     if not os.path.exists(r'/usr/local/bin/brew'):
#         subprocess.call([r'/usr/bin/ruby', r'-e',
#                          r'"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"', r'<',
#                          r'/dev/null'])
#         subprocess.call([r'/usr/local/bin/brew', r'tap', r'homebrew/science'])
#     if not os.path.exists(r'/usr/local/bin/dcraw'):
#         subprocess.call([r'/usr/local/bin/brew', r'install', r'dcraw'])
#
#     if not os.path.exists(r'/usr/local/bin/exiftool'):
#         subprocess.call([r'/usr/local/bin/brew', r'install', r'exiftool'])
#
#     if not os.path.exists(r'/usr/local/bin/opencv2'):
#         subprocess.call([r'/usr/local/bin/brew', r'install', r'opencv2'])
#     sys.path.append(r'/usr/local/bin')
#     sys.path.append(r'/usr/local/bin/dcraw')
#     sys.path.append(r'/usr/local/bin/exiftool')
#     sys.path.append(r'/usr/local/bin/opencv2')

import gdal

import glob

all_cameras = []
if sys.platform == "win32":
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
# if sys.platform == "win32":
#       import exiftool
#       exiftool.executable = modpath + os.sep + "exiftool.exe"
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'MAPIR_Processing_dockwidget_base.ui'))
MODAL_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'MAPIR_Processing_dockwidget_modal.ui'))
CAN_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'MAPIR_Processing_dockwidget_CAN.ui'))
TIME_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'MAPIR_Processing_dockwidget_time.ui'))


class KernelModal(QtWidgets.QDialog, MODAL_CLASS):
    parent = None

    def __init__(self, parent=None):
        """Constructor."""
        super(KernelModal, self).__init__(parent=parent)
        self.parent = parent
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

    def on_ModalSaveButton_released(self):
        seconds = int(self.SecondsLine.text())
        minutes = int(self.MinutesLine.text())
        hours = int(self.HoursLine.text())
        days = int(self.DaysLine.text())
        weeks = int(self.WeeksLine.text())
        if (seconds / 60) > 1:
            minutes += int(seconds / 60)
            seconds = seconds % 60
        if (minutes / 60) > 1:
            hours += int(minutes / 60)
            minutes = minutes % 60
        if (hours / 24) > 1:
            days += int(hours / 24)
            hours = hours % 24
        if (days / 7) > 1:
            weeks += int(days / 7)
            days = days % 7
        self.parent.seconds = seconds
        self.parent.minutes = minutes
        self.parent.hours = hours
        self.parent.days = days
        self.parent.weeks = weeks
        self.parent.writeToIntervalLine()

        # weeks /= 604800
        # days /= 86400
        # hours /= 3600
        # minutes /= 60
        # seconds += minutes + hours + days + weeks
        #
        # MAPIR_ProcessingDockWidget.interval = int(seconds)
        self.close()

    def on_ModalCancelButton_released(self):
        self.close()


class KernelCAN(QtWidgets.QDialog, CAN_CLASS):
    parent = None

    def __init__(self, parent=None):
        """Constructor."""
        super(KernelCAN, self).__init__(parent=parent)
        self.parent = parent
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

    def on_ModalSaveButton_released(self):
        buf = [0] * 512
        buf[0] = self.parent.SET_REGISTER_WRITE_REPORT
        buf[1] = eRegister.RG_CAN_NODE_ID.value
        nodeid = int(self.KernelNodeID.text())
        buf[2] = nodeid

        self.parent.writeToKernel(buf)
        buf = [0] * 512
        buf[0] = self.parent.SET_REGISTER_BLOCK_WRITE_REPORT
        buf[1] = eRegister.RG_CAN_BIT_RATE_1.value
        buf[2] = 2
        bitrate = int(self.KernelBitRate.currentText())
        bit1 = (bitrate >> 8) & 0xff
        bit2 = bitrate & 0xff
        buf[3] = bit1
        buf[4] = bit2

        buf = [0] * 512
        buf = [0] * 512
        buf[0] = self.parent.SET_REGISTER_BLOCK_WRITE_REPORT
        buf[1] = eRegister.RG_CAN_SAMPLE_POINT_1.value
        buf[2] = 2
        samplepoint = int(self.KernelSamplePoint.text())
        sample1 = (samplepoint >> 8) & 0xff
        sample2 = samplepoint & 0xff
        buf[3] = sample1
        buf[4] = sample2
        self.close()

    def on_ModalCancelButton_released(self):
        self.close()


class KernelTime(QtWidgets.QDialog, TIME_CLASS):
    parent = None
    timer = QtCore.QTimer()
    BUFF_LEN = 512
    SET_EVENT_REPORT = 1
    SET_COMMAND_REPORT = 3
    SET_REGISTER_WRITE_REPORT = 5
    SET_REGISTER_BLOCK_WRITE_REPORT = 7
    SET_REGISTER_READ_REPORT = 9
    SET_REGISTER_BLOCK_READ_REPORT = 11
    SET_CAMERA = 13
    def __init__(self, parent=None):
        """Constructor."""
        super(KernelTime, self).__init__(parent=parent)
        self.parent = parent
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(1)
    def on_ModalSaveButton_released(self):
        self.timer.stop()
        buf = [0] * 512

        buf[0] = self.SET_REGISTER_BLOCK_WRITE_REPORT
        buf[1] = eRegister.RG_REALTIME_CLOCK.value
        buf[2] = 8
        t = QtCore.QDateTime.toMSecsSinceEpoch(self.KernelReferenceTime.dateTime())
        buf[3] = t & 0xff
        buf[4] = (t >> 8) & 0xff
        buf[5] = (t >> 16) & 0xff
        buf[6] = (t >> 24) & 0xff
        buf[7] = (t >> 32) & 0xff
        buf[8] = (t >> 40) & 0xff
        buf[9] = (t >> 48) & 0xff
        buf[10] = (t >> 54) & 0xff
        self.parent.writeToKernel(buf)
        buf = [0] * 512

        buf[0] = self.SET_REGISTER_BLOCK_READ_REPORT
        buf[1] = eRegister.RG_REALTIME_CLOCK.value
        buf[2] = 8
        r = self.parent.writeToKernel(buf)[2:11]
        val = r[0] | (r[1] << 8) | (r[2] << 16) | (r[3] << 24) | (r[4] << 32) | (r[5] << 40) | (r[6] << 48) | (
        r[7] << 56)

        offset = QtCore.QDateTime.currentMSecsSinceEpoch() - val

        while offset > 1:
            if self.KernelTimeSelect.currentIndex() == 0:
                buf[0] = self.SET_REGISTER_BLOCK_WRITE_REPORT
                buf[1] = eRegister.RG_REALTIME_CLOCK.value
                buf[2] = 8
                t = QtCore.QDateTime.toMSecsSinceEpoch(QtCore.QDateTime.currentDateTimeUtc().addSecs(18).addMSecs(offset))
                buf[3] = t & 0xff
                buf[4] = (t >> 8) & 0xff
                buf[5] = (t >> 16) & 0xff
                buf[6] = (t >> 24) & 0xff
                buf[7] = (t >> 32) & 0xff
                buf[8] = (t >> 40) & 0xff
                buf[9] = (t >> 48) & 0xff
                buf[10] = (t >> 54) & 0xff
                self.parent.writeToKernel(buf)
                buf = [0] * 512

                buf[0] = self.SET_REGISTER_BLOCK_READ_REPORT
                buf[1] = eRegister.RG_REALTIME_CLOCK.value
                buf[2] = 8
                r = self.parent.writeToKernel(buf)[2:11]
                val = r[0] | (r[1] << 8) | (r[2] << 16) | (r[3] << 24) | (r[4] << 32) | (r[5] << 40) | (r[6] << 48) | (
                    r[7] << 56)

                offset = QtCore.QDateTime.currentMSecsSinceEpoch() - val
            elif self.KernelTimeSelect.currentIndex() == 1:
                buf[0] = self.SET_REGISTER_BLOCK_WRITE_REPORT
                buf[1] = eRegister.RG_REALTIME_CLOCK.value
                buf[2] = 8
                t = QtCore.QDateTime.toMSecsSinceEpoch(QtCore.QDateTime.currentDateTimeUtc().addMSecs(offset))
                buf[3] = t & 0xff
                buf[4] = (t >> 8) & 0xff
                buf[5] = (t >> 16) & 0xff
                buf[6] = (t >> 24) & 0xff
                buf[7] = (t >> 32) & 0xff
                buf[8] = (t >> 40) & 0xff
                buf[9] = (t >> 48) & 0xff
                buf[10] = (t >> 54) & 0xff
                self.parent.writeToKernel(buf)
                buf = [0] * 512

                buf[0] = self.SET_REGISTER_BLOCK_READ_REPORT
                buf[1] = eRegister.RG_REALTIME_CLOCK.value
                buf[2] = 8
                r = self.parent.writeToKernel(buf)[2:11]
                val = r[0] | (r[1] << 8) | (r[2] << 16) | (r[3] << 24) | (r[4] << 32) | (r[5] << 40) | (r[6] << 48) | (
                    r[7] << 56)

                offset = QtCore.QDateTime.currentMSecsSinceEpoch() - val
            else:

                buf[0] = self.SET_REGISTER_BLOCK_WRITE_REPORT
                buf[1] = eRegister.RG_REALTIME_CLOCK.value
                buf[2] = 8
                t = QtCore.QDateTime.toMSecsSinceEpoch(QtCore.QDateTime.currentDateTime().addMSecs(offset))
                buf[3] = t & 0xff
                buf[4] = (t >> 8) & 0xff
                buf[5] = (t >> 16) & 0xff
                buf[6] = (t >> 24) & 0xff
                buf[7] = (t >> 32) & 0xff
                buf[8] = (t >> 40) & 0xff
                buf[9] = (t >> 48) & 0xff
                buf[10] = (t >> 54) & 0xff
                self.parent.writeToKernel(buf)
                buf = [0] * 512

                buf[0] = self.SET_REGISTER_BLOCK_READ_REPORT
                buf[1] = eRegister.RG_REALTIME_CLOCK.value
                buf[2] = 8
                r = self.parent.writeToKernel(buf)[2:11]
                val = r[0] | (r[1] << 8) | (r[2] << 16) | (r[3] << 24) | (r[4] << 32) | (r[5] << 40) | (r[6] << 48) | (
                    r[7] << 56)

                offset = QtCore.QDateTime.currentMSecsSinceEpoch() - val

        self.close()

    def on_ModalCancelButton_released(self):
        self.timer.stop()
        self.close()

    def tick(self):
        buf = [0] * 512

        buf[0] = self.SET_REGISTER_BLOCK_READ_REPORT
        buf[1] = eRegister.RG_REALTIME_CLOCK.value
        buf[2] = 8
        r = self.parent.writeToKernel(buf)[2:11]
        val = r[0] | (r[1] << 8) | (r[2] << 16) | (r[3] << 24) | (r[4] << 32) | (r[5] << 40) | (r[6] << 48) | (r[7] << 56)
        self.KernelCameraTime.setDateTime(QtCore.QDateTime.fromMSecsSinceEpoch(val))
        if self.KernelTimeSelect.currentIndex() == 0:
            self.KernelReferenceTime.setDateTime(QtCore.QDateTime.currentDateTimeUtc().addSecs(18))
        elif self.KernelTimeSelect.currentIndex() == 1:
            self.KernelReferenceTime.setDateTime(QtCore.QDateTime.currentDateTimeUtc())
        else:
            self.KernelReferenceTime.setDateTime(QtCore.QDateTime.currentDateTime())
class tPoll:
    def __init__(self):
        request = 0
        code = 0
        len = 0 #Len can also store the value depending on the code given
        values = []
class tEventInfo:
    def __init__(self):
        mode = 0
        process = 0
        focusing = 0
        inversion = 0
        nr_faces = 0
class MAPIR_ProcessingDockWidget(QtWidgets.QDockWidget, FORM_CLASS):
    BASE_COEFF_SURVEY2_RED_JPG = [-2.55421832, 16.01240929, 0.0, 0.0, 0.0, 0.0]
    BASE_COEFF_SURVEY2_GREEN_JPG = [0.0, 0.0, -0.60437250, 4.82869470, 0.0, 0.0]
    BASE_COEFF_SURVEY2_BLUE_JPG = [0.0, 0.0, 0.0, 0.0, -0.39268985, 2.67916884]
    BASE_COEFF_SURVEY2_NDVI_JPG = [-0.29870245, 6.51199915, 0.0, 0.0, -0.65112026, 10.30416005]
    BASE_COEFF_SURVEY2_NIR_JPG = [-0.46967653, 7.13619139, 0.0, 0.0, 0.0, 0.0]
    BASE_COEFF_SURVEY1_NDVI_JPG = [-6.33770486888, 331.759383023, 0.0, 0.0, -0.6931339436, 51.3264675118]
    BASE_COEFF_SURVEY2_RED_TIF = [-5.09645820, 0.24177528, 0.0, 0.0, 0.0, 0.0]
    BASE_COEFF_SURVEY2_GREEN_TIF = [0.0, 0.0, -1.39528479, 0.07640011, 0.0, 0.0]
    BASE_COEFF_SURVEY2_BLUE_TIF = [0.0, 0.0, 0.0, 0.0, -0.67299134, 0.03943339]
    BASE_COEFF_SURVEY2_NDVI_TIF = [3.21946584661, 1.06087488594, 0.0, 0.0, -43.6505776052, 1.46482226805]
    BASE_COEFF_SURVEY2_NIR_TIF = [-2.24216724, 0.12962333, 0.0, 0.0, 0.0, 0.0]
    BASE_COEFF_DJIX3_NDVI_JPG = [-0.34430543, 4.63184993, 0.0, 0.0, -0.49413940, 16.36429964]
    BASE_COEFF_DJIX3_NDVI_TIF = [-0.74925346, 0.01350319, 0.0, 0.0, -0.77810008, 0.03478272]
    BASE_COEFF_DJIPHANTOM4_NDVI_JPG = [-1.17016961, 0.03333209, 0.0, 0.0, -0.99455214, 0.05373502]
    BASE_COEFF_DJIPHANTOM4_NDVI_TIF = [-1.17016961, 0.03333209, 0.0, 0.0, -0.99455214, 0.05373502]
    BASE_COEFF_DJIPHANTOM3_NDVI_JPG = [-1.54494979, 3.44708472, 0.0, 0.0, -1.40606832, 6.35407929]
    BASE_COEFF_DJIPHANTOM3_NDVI_TIF = [-1.37495554, 0.01752340, 0.0, 0.0, -1.41073753, 0.03700812]
    BASE_COEFF_KERNEL_F644 = [0.0, 0.0]
    BASE_COEFF_KERNEL_F405 = [0.0, 0.0]
    BASE_COEFF_KERNEL_F450 = [0.0, 0.0]
    BASE_COEFF_KERNEL_F520 = [0.0, 0.0]
    BASE_COEFF_KERNEL_F550 = [0.0, 0.0]
    BASE_COEFF_KERNEL_F632 = [0.0, 0.0]
    BASE_COEFF_KERNEL_F650 = [0.0, 0.0]
    BASE_COEFF_KERNEL_F725 = [0.0, 0.0]
    BASE_COEFF_KERNEL_F808 = [0.0, 0.0]
    BASE_COEFF_KERNEL_F850 = [0.0, 0.0]
    BASE_COEFF_KERNEL_F395_870 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    BASE_COEFF_KERNEL_F475_850 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    BASE_COEFF_KERNEL_F550_850 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    BASE_COEFF_KERNEL_F660_850 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    BASE_COEFF_KERNEL_F475_550_850 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    BASE_COEFF_KERNEL_F550_660_850 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    camera = 0
    poll = []
    ei = tEventInfo()
    capturing = False
    SQ_TO_TARG = 2.1875
    SQ_TO_SQ = 5.0
    CORNER_TO_CORNER = 5.25
    CORNER_TO_TARG = 10.0
    TARGET_LENGTH = 2.0
    TARG_TO_TARG = 2.6
    dialog = None
    imcols = 4608
    imrows = 3456
    imsize = imcols * imrows
    closingPlugin = QtCore.pyqtSignal()
    firstpass = True
    useqr = False
    qrcoeffs = []  # Red Intercept, Red Slope,  Green Intercept, Green Slope, Blue Intercept, Blue Slope

    qrcoeffs2 = []
    qrcoeffs3 = []
    qrcoeffs4 = []
    qrcoeffs5 = []
    qrcoeffs6 = []

    oldrefvalues = {
        "660/850": [[87.032549, 52.135779, 23.664799], [0, 0, 0], [84.63514, 51.950608, 22.795518]],
        "446/800": [[84.19608509, 52.0440145, 23.0113958], [0, 0, 0], [86.45652801, 50.37779363, 23.59041624]],
        "850": [[84.63514, 51.950608, 22.795518], [0, 0, 0], [0, 0, 0]],
        "808": [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
        "650": [[87.032549, 52.135779, 23.664799], [0, 0, 0], [0, 0, 0]],
        "550": [[0, 0, 0], [87.415089, 51.734381, 24.032515], [0, 0, 0]],
        "450": [[0, 0, 0], [0, 0, 0], [86.469794, 50.392915, 23.565447]],
        "Mono450": [86.34818638, 50.24087105, 23.51860396],
        "Mono550": [87.40616379, 51.73070235, 24.02423818],
        "Mono650": [87.05783136, 52.12290524, 23.66437854],
        "Mono725": [86.06071247, 52.1474266, 23.37744252],
        "Mono808": [84.06184266, 52.03405498, 22.97701185],
        "Mono850": [84.81919553, 51.9491643, 22.78713071],
        "Mono405": [85.56905469, 49.21243183, 23.09899254],
        "Mono518": [87.29814889, 51.51370187, 24.04729692],
        "Mono632": [87.24034645, 52.09649915, 23.74529161],
        # "Mono660": [87.04202831, 52.12214688, 23.65919358],
        "Mono590": [87.47043911, 51.95596573, 23.92049856],
        "550/660/850": [[84.74610999, 51.96055607, 22.79922965],[86.99940018, 52.12235151, 23.64397706],[87.40311726, 51.72611881, 24.02870156]]
    }
    refvalues = {
        # "660/850": [[87.032549, 52.135779, 23.664799], [0, 0, 0], [84.63514, 51.950608, 22.795518]],
        # "446/800": [[84.19608509, 52.0440145, 23.0113958], [0, 0, 0], [86.45652801, 50.37779363, 23.59041624]],
        # "850": [[84.63514, 51.950608, 22.795518], [0, 0, 0], [0, 0, 0]],
        # "808": [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
        # "650": [[87.032549, 52.135779, 23.664799], [0, 0, 0], [0, 0, 0]],
        # "550": [[0, 0, 0], [87.415089, 51.734381, 24.032515], [0, 0, 0]],
        # "450": [[0, 0, 0], [0, 0, 0], [86.469794, 50.392915, 23.565447]],
        # TODO Fix this for new calib targets

        "Mono450": [10.137101, 24.131129, 24.131129, 2.50],
        "Mono550": [13.050459, 25.918403, 25.918403, 2.444385],
        "Mono650": [42.873777, 25.681838, 25.681838, 2.4],
        "Mono725": [57.362319, 26.209292, 26.209292, 2.444148],
        "Mono808": [80.761967, 27.552786, 27.552786, 2.522048],
        "Mono850": [85.470884, 27.989664, 27.989664, 2.476279],
        "Mono405": [10.419592, 23.297778, 23.297778, 2.579408],
        "Mono518": [10.192879, 25.668374, 25.668374, 2.50],
        "Mono632": [40.314177, 25.624361, 25.624361, 2.40],
        "Mono615": [36.590561, 25.575475, 25.575475, 2.40],
        # "Mono660": [87.04202831, 52.12214688, 23.65919358],
        "Mono590": [28.088219, 25.614054, 25.614054, 2.40],
        # "550/660/850": [[84.74610999, 51.96055607, 22.79922965], [86.99940018, 52.12235151, 23.64397706],
        #                 [87.40311726, 51.72611881, 24.02870156]]
    }
    pixel_min_max = {"redmax": 0.0, "redmin": 65535.0,
                     "greenmax": 0.0, "greenmin": 65535.0,
                     "bluemax": 0.0, "bluemin": 65535.0}
    monominmax = {"min": 65535.0,"max": 0.0}
    weeks = 0
    days = 0
    hours = 0
    minutes = 0
    seconds = 1
    modalwindow = None
    array_indicator = False

    POLL_TIME = 3000
    # SLOW_POLL = 10000
    slow = 0
    regs = [0] * eRegister.RG_SIZE.value
    paths = []
    pathnames = []
    driveletters = ['\0','\0','\0','\0','\0','\0']
    source = 0
    evt = 0
    info = 0
    VENDOR_ID = 0x525
    PRODUCT_ID = 0xa4ac
    BUFF_LEN = 512
    SET_EVENT_REPORT = 1
    SET_COMMAND_REPORT = 3
    SET_REGISTER_WRITE_REPORT = 5
    SET_REGISTER_BLOCK_WRITE_REPORT = 7
    SET_REGISTER_READ_REPORT = 9
    SET_REGISTER_BLOCK_READ_REPORT = 11
    SET_CAMERA = 13
    # mMutex = QMutex()
    regs = []
    paths_1_2 = []
    paths_3_0 = []
    paths_14_0 = []
    ISO_VALS = (1,2,4,8,16,32)
    def __init__(self, parent=None):
        """Constructor."""
        super(MAPIR_ProcessingDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        # self.timer.timeout.connect(self.tick)

    # def tick(self):
    #     self.KernelUpdate()

    def on_KernelConnect_released(self):
        self.ConnectKernels()
    def ConnectKernels(self):
        all_cameras = hid.enumerate(self.VENDOR_ID, self.PRODUCT_ID)
        if all_cameras == []:

            self.KernelLog.append("No cameras found! Please check your USB connection and try again.")

        self.paths.clear()
        self.paths_1_2.clear()
        self.paths_3_0.clear()
        self.paths_14_0.clear()
        for cam in all_cameras:

            self.paths.append(cam['path'])


        # if len(self.paths) > 1:
        #     temppaths = self.paths
        #     arids = []
        #     for path in self.paths:
        #         self.camera = path
        #         buf = [0] * 512
        #         buf[0] = self.SET_REGISTER_READ_REPORT
        #         buf[1] = eRegister.RG_CAMERA_LINK_ID.value
        #         arid = self.writeToKernel(buf)[2]
        #         arids.append(arid)
            # [self.paths for (y, self.paths) in sorted(zip(arids, temppaths), key=lambda pair: pair[0])]
            # for count, id in enumerate(arids):
            #     self.paths[id] = temppaths[count]

        self.KernelCameraSelect.blockSignals(True)
        self.KernelCameraSelect.clear()
        self.KernelCameraSelect.addItem("All")
        self.KernelCameraSelect.blockSignals(False)
        for path in self.paths:
            self.camera = path
            buf = [0] * 512
            buf[0] = self.SET_REGISTER_BLOCK_READ_REPORT
            buf[1] = eRegister.RG_MEDIA_FILE_NAME_A.value
            buf[2] = 3
            res = self.writeToKernel(buf)
            print(chr(res[2]) + chr(res[3]) + chr(res[4]))
            item = chr(res[2]) + chr(res[3]) + chr(res[4])
            buf = [0] * 512
            buf[0] = self.SET_REGISTER_READ_REPORT
            buf[1] = eRegister.RG_SENSOR_ID.value
            res = self.writeToKernel(buf)
            if res[2] == 2:
                self.paths_1_2.append(path)
            elif res[2] == 1:
                self.paths_3_0.append(path)
            elif res[2] == 0:
                self.paths_14_0.append(path)
            self.pathnames.append(item)
            self.KernelCameraSelect.blockSignals(True)
            self.KernelCameraSelect.addItem(item)
            self.KernelCameraSelect.blockSignals(False)
        self.camera = self.paths[0]

        self.KernelUpdate()
    def on_Kernel3LetterSave_released(self):
        threeletter = self.Kernel3LetterID.text()
        buf = [0] * 512
        buf[0] = self.SET_REGISTER_BLOCK_WRITE_REPORT
        buf[1] = eRegister.RG_MEDIA_FILE_NAME_A.value
        buf[2] = 3
        buf[3] = ord(threeletter[0])
        buf[4] = ord(threeletter[1])
        buf[5] = ord(threeletter[2])
        res = self.writeToKernel(buf)
        self.KernelUpdate()
    def on_KernelCameraSelect_currentIndexChanged(self):
        self.camera = self.paths[self.KernelCameraSelect.currentIndex() - 1]

        if not self.KernelTransferButton.isChecked():
            self.KernelUpdate()
    def on_KernelArraySelect_currentIndexChanged(self):
        if self.KernelArraySelect.currentIndex() == 0:
            self.array_indicator = False
            self.KernelCameraSelect.setEnabled(True)
        else:
            self.array_indicator = True
            self.KernelCameraSelect.setEnabled(False)
    def on_KernelExposureMode_currentIndexChanged(self, int):
        if self.KernelExposureMode.currentIndex() == 0:
            self.KernelISO.setEnabled(False)
            self.KernelShutterSpeed.setEnabled(False)
        else:
            self.KernelISO.setEnabled(True)
            self.KernelShutterSpeed.setEnabled(True)

    def KernelUpdate(self):
        self.KernelExposureMode.blockSignals(True)
        self.KernelShutterSpeed.blockSignals(True)
        self.KernelISO.blockSignals(True)
        self.KernelVideoOut.blockSignals(True)
        self.KernelFolderCount.blockSignals(True)
        self.KernelBeep.blockSignals(True)
        self.KernelPWMSignal.blockSignals(True)

        buf = [0] * 512
        buf[0] = self.SET_REGISTER_BLOCK_READ_REPORT
        buf[1] = eRegister.RG_CAMERA_SETTING.value
        buf[2] = eRegister.RG_SIZE.value

        res = self.writeToKernel(buf)
        self.regs = res[2:]
        shutter = self.getRegister(eRegister.RG_SHUTTER.value)
        if shutter == 0:
            self.KernelExposureMode.setCurrentIndex(0)
            self.KernelISO.setEnabled(False)
            self.KernelShutterSpeed.setEnabled(False)
        else:
            self.KernelExposureMode.setCurrentIndex(1)
            self.KernelISO.setEnabled(True)
            self.KernelShutterSpeed.setEnabled(True)

        self.KernelShutterSpeed.setCurrentIndex(shutter - 1)

        iso = self.getRegister(eRegister.RG_ISO.value)
        if iso == self.ISO_VALS[0]:

            self.KernelISO.setCurrentIndex(0)
        elif iso == self.ISO_VALS[1]:
            self.KernelISO.setCurrentIndex(1)
        elif iso == self.ISO_VALS[2]:
            self.KernelISO.setCurrentIndex(2)
        else:
            self.KernelISO.setCurrentIndex(3)

        dac = self.getRegister(eRegister.RG_DAC.value)

        hdmi = self.getRegister(eRegister.RG_HDMI.value)

        if hdmi == 1 and dac == 1:
            self.KernelVideoOut.setCurrentIndex(3)
        elif hdmi == 0 and dac == 1:
            self.KernelVideoOut.setCurrentIndex(2)
        elif hdmi == 1 and dac == 0:
            self.KernelVideoOut.setCurrentIndex(1)
        else:
            self.KernelVideoOut.setCurrentIndex(0)


        media = self.getRegister(eRegister.RG_MEDIA_FILES_CNT.value)
        self.KernelFolderCount.setCurrentIndex(media)



        beep = self.getRegister(eRegister.RG_BEEPER_ENABLE.value)
        if beep != 0:
            self.KernelBeep.setChecked(True)
        else:
            self.KernelBeep.setChecked(False)

        pwm = self.getRegister(eRegister.RG_PWM_TRIGGER.value)
        if pwm != 0:
            self.KernelPWMSignal.setChecked(True)
        else:
            self.KernelPWMSignal.setChecked(False)

        self.KernelPanel.clear()
        self.KernelPanel.append("Hardware ID: " + str(self.getRegister(eRegister.RG_HARDWARE_ID.value)))
        self.KernelPanel.append("Firmware version: " + str(self.getRegister(eRegister.RG_FIRMWARE_ID.value)))
        self.KernelPanel.append("Sensor: " + str(self.getRegister(eRegister.RG_SENSOR_ID.value)))
        self.KernelPanel.append("Lens: " + str(self.getRegister(eRegister.RG_LENS_ID.value)))
        if shutter == 0:
            self.KernelPanel.append("Shutter: Auto")
        else:
            self.KernelPanel.append("Shutter: " + self.KernelShutterSpeed.itemText(self.getRegister(eRegister.RG_SHUTTER.value) -1) + " sec")
        self.KernelPanel.append("ISO: " + str(self.getRegister(eRegister.RG_ISO.value)) + "00")
        self.KernelPanel.append("WB: " + str(self.getRegister(eRegister.RG_WHITE_BALANCE.value)))
        self.KernelPanel.append("EVC: " + str(self.getRegister(eRegister.RG_EV_CORRECTION.value)))
        self.KernelPanel.append("Video resolution: " + str(self.getRegister(eRegister.RG_VIDEO_RESOLUTION.value)))
        self.KernelPanel.append("Photo resolution: " + str(self.getRegister(eRegister.RG_PHOTO_RESOLUTION.value)/10) + " Mpix")
        buf = [0] * 512
        buf[0] = self.SET_REGISTER_READ_REPORT
        buf[1] = eRegister.RG_CAMERA_ARRAY_TYPE.value
        artype = self.writeToKernel(buf)[2]
        self.KernelPanel.append("Array Type: " + str(artype))
        buf = [0] * 512
        buf[0] = self.SET_REGISTER_READ_REPORT
        buf[1] = eRegister.RG_CAMERA_LINK_ID.value
        arid = self.writeToKernel(buf)[2]
        self.KernelPanel.append("Array ID: " + str(arid))

        self.KernelExposureMode.blockSignals(False)
        self.KernelShutterSpeed.blockSignals(False)
        self.KernelISO.blockSignals(False)
        self.KernelVideoOut.blockSignals(False)
        self.KernelFolderCount.blockSignals(False)
        self.KernelBeep.blockSignals(False)
        self.KernelPWMSignal.blockSignals(False)
    def on_KernelFolderButton_released(self):
        with open(modpath + os.sep + "instring.txt", "r+") as instring:
            self.KernelTransferFolder.setText(QtWidgets.QFileDialog.getExistingDirectory(directory=instring.read()))
            instring.truncate(0)
            instring.seek(0)
            instring.write(self.PreProcessInFolder.text())

    def on_KernelAutoTransfer_released(self):

        preconnect = False
        if self.camera is not None:
            current_path = self.camera
            preconnect = True
        try:
            self.ConnectKernels()
        except:
            QtWidgets.QApplication.processEvents()
            self.KernelLog.append("No Camera Found")
        count = 0
        drivesfound = []
        for path in self.paths:
            count += 1
            self.camera = path
            buf = [0] * 512
            buf[0] = self.SET_COMMAND_REPORT
            buf[1] = eCommand.CM_TRANSFER_MODE.value
            self.writeToKernel(buf)
        if preconnect == True:
            self.camera = current_path
        self.KernelLog.append("Looking for mounted cameras")
        QtWidgets.QApplication.processEvents()
        while len(drivesfound) < count:
            drv = 'C'
            while drv is not ']':
                if os.path.isdir(drv + r":" + os.sep + r"dcim"):
                    if drv in drivesfound:
                        pass
                    else:
                        drivesfound.append(drv)
                        files = glob.glob(drv + r":" + os.sep + r"dcim/*/*")
                        namepart = files[0].split(os.sep)[-1][1:4]
                        self.KernelLog.append("Found camera" + str(namepart))
                        drv = chr(ord(drv) + 1)
                        QtWidgets.QApplication.processEvents()
                else:
                    drv = chr(ord(drv) + 1)

        tmtf = r":/dcim/tmtf.txt"
        drv = 'C'

        count = 0
        while drv is not ']':
            QtWidgets.QApplication.processEvents()
            pathidx = -1
            if os.path.isdir(drv + r":" + os.sep + r"dcim"):
                # try:
                folders = glob.glob(drv + r":" + os.sep + r"dcim/*/")
                files = glob.glob(drv + r":" + os.sep + r"dcim/*/*")

                print(files)
                for idx, threechar in enumerate(self.pathnames):
                    print(threechar)
                    print(files[0].split(os.sep)[-1][1:4])
                    if files[0].split(os.sep)[-1][1:4] == threechar:
                        pathidx = idx
                        self.driveletters[idx] = drv
                        count += 1
                        self.KernelLog.append("Found " + str(threechar) + ". Extracting images.")
                        QtWidgets.QApplication.processEvents()
                if pathidx >= 0:
                    if os.path.exists(self.KernelTransferFolder.text() + os.sep + self.pathnames[pathidx]):
                        foldercount = 2
                        endloop = False
                        outdir = ""
                        while endloop is False:
                            outdir = self.KernelTransferFolder.text() + os.sep + self.pathnames[pathidx] + "_" + str(foldercount)
                            if os.path.exists(outdir):
                                foldercount += 1
                            else:
                                os.mkdir(outdir)
                                endloop = True
                        for fold in folders:
                            distutils.dir_util.copy_tree(fold, outdir)
                    else:
                        for fold in folders:
                            distutils.dir_util.copy_tree(fold, self.KernelTransferFolder.text() + os.sep + self.pathnames[pathidx])
                        raws = glob.glob(self.KernelTransferFolder.text() + os.sep + self.pathnames[pathidx] + r"*.mapir")
                        for raw in raws:
                            self.openMapir(raw, raw.split('.')[0] + ".tif")
                    self.KernelLog.append("Finished extracting " + str(self.pathnames[pathidx]) + ".")
                    QtWidgets.QApplication.processEvents()
                else:
                    pass
                drv = chr(ord(drv) + 1)
                # except:
                #     drv = chr(ord(drv) + 1)
                #     pass
            else:
                drv = chr(ord(drv) + 1)
    def on_KernelBandButton1_released(self):
        with open(modpath + os.sep + "instring.txt", "r+") as instring:
            self.KernelBand1.setText(QtWidgets.QFileDialog.getExistingDirectory(directory=instring.read()))
            instring.truncate(0)
            instring.seek(0)
            instring.write(self.KernelBand1.text())
    def on_KernelBandButton2_released(self):
        with open(modpath + os.sep + "instring.txt", "r+") as instring:
            self.KernelBand2.setText(QtWidgets.QFileDialog.getExistingDirectory(directory=instring.read()))
            instring.truncate(0)
            instring.seek(0)
            instring.write(self.KernelBand2.text())
    def on_KernelBandButton3_released(self):
        with open(modpath + os.sep + "instring.txt", "r+") as instring:
            self.KernelBand3.setText(QtWidgets.QFileDialog.getExistingDirectory(directory=instring.read()))
            instring.truncate(0)
            instring.seek(0)
            instring.write(self.KernelBand3.text())
    def on_KernelBandButton4_released(self):
        with open(modpath + os.sep + "instring.txt", "r+") as instring:
            self.KernelBand4.setText(QtWidgets.QFileDialog.getExistingDirectory(directory=instring.read()))
            instring.truncate(0)
            instring.seek(0)
            instring.write(self.KernelBand4.text())
    def on_KernelBandButton5_released(self):
        with open(modpath + os.sep + "instring.txt", "r+") as instring:
            self.KernelBand5.setText(QtWidgets.QFileDialog.getExistingDirectory(directory=instring.read()))
            instring.truncate(0)
            instring.seek(0)
            instring.write(self.KernelBand5.text())
    def on_KernelBandButton6_released(self):
        with open(modpath + os.sep + "instring.txt", "r+") as instring:
            self.KernelBand6.setText(QtWidgets.QFileDialog.getExistingDirectory(directory=instring.read()))
            instring.truncate(0)
            instring.seek(0)
            instring.write(self.KernelBand6.text())

    def on_KernelRenameOutputButton_released(self):
        with open(modpath + os.sep + "instring.txt", "r+") as instring:
            self.KernelRenameOutputFolder.setText(QtWidgets.QFileDialog.getExistingDirectory(directory=instring.read()))
            instring.truncate(0)
            instring.seek(0)
            instring.write(self.KernelRenameOutputFolder.text())
    def on_KernelRenameButton_released(self):
        try:
            folder1 = []
            folder2 = []
            folder3 = []
            folder4 = []
            folder5 = []
            folder6 = []
            if len(self.KernelBand1.text()) > 0:
                folder1.extend(glob.glob(self.KernelBand1.text() + os.sep + "*.tif?"))
            if len(self.KernelBand2.text()) > 0:
                folder2.extend(glob.glob(self.KernelBand2.text() + os.sep + "*.tif?"))
            if len(self.KernelBand3.text()) > 0:
                folder3.extend(glob.glob(self.KernelBand3.text() + os.sep + "*.tif?"))
            if len(self.KernelBand4.text()) > 0:
                folder4.extend(glob.glob(self.KernelBand4.text() + os.sep + "*.tif?"))
            if len(self.KernelBand5.text()) > 0:
                folder5.extend(glob.glob(self.KernelBand5.text() + os.sep + "*.tif?"))
            if len(self.KernelBand6.text()) > 0:
                folder6.extend(glob.glob(self.KernelBand6.text() + os.sep + "*.tif?"))
            folder1.sort()
            folder2.sort()
            folder3.sort()
            folder4.sort()
            folder5.sort()
            folder6.sort()
            outfolder = self.KernelRenameOutputFolder.text()
            if not os.path.exists(outfolder):
                os.mkdir(outfolder)
            all_folders = [folder1, folder2, folder3, folder4, folder5, folder6]
            underscore = 1
            for folder in all_folders:

                counter = 1

                if len(folder) > 0:
                    for tiff in folder:


                        shutil.copyfile(tiff, outfolder + os.sep + "IMG_" + str(counter).zfill(5) + '_' + str(
                            underscore) + '.' + tiff.split('.')[1])
                        counter = counter + 1
                    underscore = underscore + 1
            self.KernelLog.append("Finished Renaming All Files.")
        except Exception as e:
            self.KernelLog.append(str(e))
    def on_KernelTransferButton_toggled(self):

        if self.camera is None:
            raise ValueError('Device not found')


        if self.KernelTransferButton.isChecked():
            # if self.KernelArrayTransfer.isChecked():
            #     current_path = self.camera
            #     for path in self.paths:
            #         self.camera = path
            #         buf = [0] * 512
            #         buf[0] = self.SET_COMMAND_REPORT
            #         buf[1] = eCommand.CM_TRANSFER_MODE.value
            #         res = self.writeToKernel(buf)
            #     self.camera = current_path
            #     drv = 'C'
            #     while drv is not ']':
            #         if os.path.isdir(drv + r":" + os.sep + r"dcim"):
            #             # try:
            #
            #             shutil.copytree(drv + r":" + os.sep + r"dcim" + os.sep,
            #                             self.KernelTransferFolder.text() + os.sep + drv)
            #             drv = chr(ord(drv) + 1)
            #             # except:
            #             #     drv = chr(ord(drv) + 1)
            #             #     pass
            #         else:
            #             drv = chr(ord(drv) + 1)
            # else:\
            if self.KernelCameraSelect.currentIndex() == 0:
                for cam in self.paths:
                    self.camera = cam
                    buf = [0] * 512
                    buf[0] = self.SET_COMMAND_REPORT
                    buf[1] = eCommand.CM_TRANSFER_MODE.value
                    self.writeToKernel(buf)
                self.camera = self.paths[0]
            else:
                buf = [0] * 512
                buf[0] = self.SET_COMMAND_REPORT
                buf[1] = eCommand.CM_TRANSFER_MODE.value
                self.writeToKernel(buf)

        else:
            tmtf = r":/dcim/tmtf.txt"
            drv = 'C'
            while drv is not ']':
                if os.path.isdir(drv + r":/dcim/"):
                    try:
                        if not os.path.exists(drv + tmtf):
                            file = open(drv + tmtf, "w")
                            file.close()
                            if self.KernelArrayTransfer.isChecked():
                                drv = chr(ord(drv) + 1)
                    except:
                        pass
                else:
                    drv = chr(ord(drv) + 1)

    def on_KernelExposureMode_currentIndexChanged(self):
        if self.KernelExposureMode.currentIndex() == 1:
            self.KernelShutterSpeed.setEnabled(True)

            self.KernelISO.setEnabled(True)
        else:
            self.KernelShutterSpeed.setEnabled(False)

            self.KernelISO.setEnabled(False)
            buf = [0] * 512
            buf[0] = self.SET_REGISTER_WRITE_REPORT
            buf[1] = eRegister.RG_SHUTTER.value
            buf[2] = 0

            res = self.writeToKernel(buf)
            buf = [0] * 512
            buf[0] = self.SET_REGISTER_WRITE_REPORT
            buf[1] = eRegister.RG_ISO.value
            buf[2] = 8

            res = self.writeToKernel(buf)
            self.KernelUpdate()
    def on_KernelCaptureButton_released(self):


        buf = [0] * 512

        buf[0] = self.SET_COMMAND_REPORT
        if self.KernelCaptureMode.currentIndex() == 0:



            buf[1] = eCommand.CM_CAPTURE_PHOTO.value


        elif self.KernelCaptureMode.currentIndex() == 1:
            buf[1] = eCommand.CM_CONTINUOUS.value

        elif self.KernelCaptureMode.currentIndex() == 2:

            buf[1] = eCommand.CM_TIME_LAPSE.value

        elif self.KernelCaptureMode.currentIndex() == 3:

            buf[1] = eCommand.CM_RECORD_VIDEO.value
        elif self.KernelCaptureMode.currentIndex() == 4:

            buf[1] = eCommand.CM_RECORD_LOOPING_VIDEO.value
        else:
            self.KernelLog.append("Invalid capture mode.")

        if self.capturing == False:
            buf[2] = 1
            self.capturing = True
        else:
            buf[2] = 0
            self.capturing = False

        res = self.writeToKernel(buf)
        self.KernelUpdate()
    def on_KernelShutterSpeed_currentIndexChanged(self):
        buf = [0] * 512
        buf[0] = self.SET_REGISTER_WRITE_REPORT
        buf[1] = eRegister.RG_SHUTTER.value
        if self.KernelExposureMode.currentIndex() == 1:
            buf[2] = self.KernelShutterSpeed.currentIndex() + 1

        res = self.writeToKernel(buf)
        self.KernelUpdate()
    def on_KernelISO_currentIndexChanged(self):
        buf = [0] * 512
        buf[0] = self.SET_REGISTER_WRITE_REPORT
        buf[1] = eRegister.RG_ISO.value
        if self.KernelExposureMode.currentIndex() == 1:
            buf[2] = self.ISO_VALS[self.KernelISO.currentIndex()]
        else:
            buf[2] = self.ISO_VALS[3]

        res = self.writeToKernel(buf)
        self.KernelUpdate()

    def getRegister(self, code):
        if code < eRegister.RG_SIZE.value:
            return self.regs[code]
        else:
            return 0
    def setRegister(self, code, value):
        if code >= eRegister.RG_SIZE.value:
            return False
        elif value == self.regs[code]:
            return False
        else:
            self.regs[code] = value
            return True
    def on_TestButton_released(self):
        buf = [0] * 512
        buf[0] = self.SET_COMMAND_REPORT
        buf[1] = eRegister.RG_CAMERA_ARRAY_TYPE.value
        artype = self.writeToKernel(buf)[2]
        print(artype)
        self.KernelUpdate()
    def writeToKernel(self, buffer):
        if self.array_indicator == False:
            dev = hid.device()
            dev.open_path(self.camera)
            q = dev.write(buffer)
            r = dev.read(self.BUFF_LEN)
            dev.close()
            return r
        else:
            r = []
            q = []
            for path in self.paths:
                dev = hid.device()
                dev.open_path(path)
                q.append(dev.write(buffer))
                r.append(dev.read(self.BUFF_LEN))
                dev.close()

    def on_KernelBeep_toggled(self):
        buf = [0] * 512

        buf[0] = self.SET_REGISTER_WRITE_REPORT
        buf[1] = eRegister.RG_BEEPER_ENABLE.value
        if self.KernelBeep.isChecked():
            buf[2] = 1
        else:
            buf[2] = 0

        res = self.writeToKernel(buf)
        self.KernelUpdate()
    def on_KernelPWMSignal_toggled(self):
        buf = [0] * 512

        buf[0] = self.SET_REGISTER_WRITE_REPORT
        buf[1] = eRegister.RG_PWM_TRIGGER.value
        if self.KernelPWMSignal.isChecked():
            buf[2] = 1
        else:
            buf[2] = 0

        res = self.writeToKernel(buf)
        self.KernelUpdate()
    def on_KernelResetButton_released(self):
        buf = [0] * 512
        buf[0] = self.SET_COMMAND_REPORT
        buf[1] = eRegister.CM_RESET_CAMERA.value

        self.writeToKernel(buf)
        self.KernelUpdate()
    def on_KernelFolderCount_currentIndexChanged(self):
        buf = [0] * 512
        buf[0] = self.SET_REGISTER_WRITE_REPORT
        buf[1] = eRegister.RG_MEDIA_FILES_CNT.value
        buf[2] = self.KernelFolderCount.currentIndex()

        self.writeToKernel(buf)
        self.KernelUpdate()
    def on_KernelVideoOut_currentIndexChanged(self):
        if self.KernelVideoOut.currentIndex() == 0:  # No Output
            buf = [0] * 512

            buf[0] = self.SET_REGISTER_WRITE_REPORT
            buf[1] = eRegister.RG_DAC.value  # DAC Register
            buf[2] = 0
            self.writeToKernel(buf)

            buf = [0] * 512

            buf[0] = self.SET_REGISTER_WRITE_REPORT
            buf[1] = eRegister.RG_HDMI.value  # HDMI Register
            buf[2] = 0
            self.writeToKernel(buf)
        elif self.KernelVideoOut.currentIndex() == 1:  # HDMI
            buf = [0] * 512

            buf[0] = self.SET_REGISTER_WRITE_REPORT
            buf[1] = eRegister.RG_DAC.value  # DAC Register
            buf[2] = 0
            self.writeToKernel(buf)

            buf = [0] * 512

            buf[0] = self.SET_REGISTER_WRITE_REPORT
            buf[1] = eRegister.RG_HDMI.value  # HDMI Register
            buf[2] = 1
            self.writeToKernel(buf)
        elif self.KernelVideoOut.currentIndex() == 2:  # SD( DAC )
            buf = [0] * 512

            buf[0] = self.SET_REGISTER_WRITE_REPORT
            buf[1] = eRegister.RG_DAC.value  # DAC Register
            buf[2] = 1
            self.writeToKernel(buf)

            buf = [0] * 512

            buf[0] = self.SET_REGISTER_WRITE_REPORT
            buf[1] = eRegister.RG_HDMI.value  # HDMI Register
            buf[2] = 0
            self.writeToKernel(buf)
        else:  # Both outputs
            buf = [0] * 512

            buf[0] = self.SET_REGISTER_WRITE_REPORT
            buf[1] = eRegister.RG_DAC.value  # DAC Register
            buf[2] = 1
            self.writeToKernel(buf)

            buf = [0] * 512

            buf[0] = self.SET_REGISTER_WRITE_REPORT
            buf[1] = eRegister.RG_HDMI.value  # HDMI Register
            buf[2] = 1
            self.writeToKernel(buf)
        # self.camera.close()
        self.KernelUpdate()
    def on_KernelIntervalButton_released(self):
        self.modalwindow = KernelModal(self)
        self.modalwindow.resize(400, 200)
        self.modalwindow.show()

        num = self.seconds % 168
        if num == 0:
            num = 1
        self.seconds = num
        self.KernelUpdate()

    def on_KernelCANButton_released(self):
        self.modalwindow = KernelCAN(self)
        self.modalwindow.resize(400, 200)
        self.modalwindow.show()
        self.KernelUpdate()

    def on_KernelTimeButton_released(self):
        self.modalwindow = KernelTime(self)
        self.modalwindow.resize(400, 200)
        self.modalwindow.show()
        self.KernelUpdate()

    def writeToIntervalLine(self):
        self.KernelIntervalLine.clear()
        self.KernelIntervalLine.setText(
            str(self.weeks) + 'w, ' + str(self.days) + 'd, ' + str(self.hours) + 'h, ' + str(self.minutes) + 'm,' + str(
                self.seconds) + 's')

    #########Pre-Process Steps: Start#################
    def on_PreProcessCameraModel_currentIndexChanged(self, int):
        if self.PreProcessCameraModel.currentIndex() == 0 or self.PreProcessCameraModel.currentIndex() == 1 or \
                        self.PreProcessCameraModel.currentIndex() == 2:
            self.PreProcessFilter.clear()
            self.PreProcessFilter.addItems(["405", "450", "520", "550", "590", "632", "650", "615", "725", "808", "850"])
            self.PreProcessFilter.setEnabled(True)
            self.PreProcessLens.clear()
            self.PreProcessLens.setEnabled(False)
        elif self.PreProcessCameraModel.currentIndex() == 3:
            self.PreProcessFilter.clear()
            self.PreProcessFilter.addItems(["Red + NIR (NDVI)", "NIR", "Red", "Green", "Blue", "RGB"])
            self.PreProcessFilter.setEnabled(True)
            self.PreProcessLens.clear()
            self.PreProcessLens.addItems(["3.97mm"])
            self.PreProcessLens.setEnabled(False)
        elif self.PreProcessCameraModel.currentIndex() == 4:
            self.PreProcessFilter.clear()
            self.PreProcessFilter.addItems(["Blue + NIR (NDVI)"])
            self.PreProcessFilter.setEnabled(False)
            self.PreProcessLens.clear()
            self.PreProcessLens.addItems(["3.97mm"])
            self.PreProcessLens.setEnabled(False)
        elif self.PreProcessCameraModel.currentIndex() == 5:
            self.PreProcessFilter.clear()
            self.PreProcessFilter.addItems(["Red + NIR (NDVI)"])
            self.PreProcessFilter.setEnabled(False)
            self.PreProcessLens.clear()
            self.PreProcessLens.addItems(["3.97mm"])
            self.PreProcessLens.setEnabled(False)
        elif self.PreProcessCameraModel.currentIndex() == 6:
            self.PreProcessFilter.clear()
            self.PreProcessFilter.addItems(["Red + NIR (NDVI)"])
            self.PreProcessFilter.setEnabled(False)
            self.PreProcessLens.clear()
            self.PreProcessLens.addItems(["3.97mm"])
            self.PreProcessLens.setEnabled(False)
        elif self.PreProcessCameraModel.currentIndex() == 7:
            self.PreProcessFilter.clear()
            self.PreProcessFilter.addItems(["RGN"])
            self.PreProcessFilter.setEnabled(False)
            self.PreProcessLens.clear()
            self.PreProcessLens.addItems(["3.97mm"])
            self.PreProcessLens.setEnabled(False)
        elif self.PreProcessCameraModel.currentIndex() > 7:
            self.PreProcessFilter.clear()
            self.PreProcessFilter.addItems(["Red + NIR (NDVI)"])
            self.PreProcessFilter.setEnabled(False)
            self.PreProcessLens.clear()
            self.PreProcessLens.addItems(["3.97mm"])
            self.PreProcessLens.setEnabled(False)
        else:
            self.PreProcessLens.clear()
            self.PreProcessFilter.setEnabled(False)
            self.PreProcessLens.clear()
            self.PreProcessLens.setEnabled(False)

    def on_CalibrationCameraModel_currentIndexChanged(self, int):
        if self.CalibrationCameraModel.currentIndex() == 0 or self.CalibrationCameraModel.currentIndex() == 1 or \
                        self.CalibrationCameraModel.currentIndex() == 2:
            self.CalibrationFilter.clear()
            self.CalibrationFilter.addItems(["405", "450", "520", "550", "590", "632", "650", "615", "725", "808", "850", "550/660/850"])
            self.CalibrationFilter.setEnabled(True)
            self.CalibrationLens.clear()
            self.CalibrationLens.setEnabled(False)

        elif ((self.CalibrationCameraModel.currentIndex() == 3) or (self.CalibrationCameraModel.currentIndex() == 4)):
            self.CalibrationFilter.clear()
            self.CalibrationFilter.addItems(["Red + NIR (NDVI)", "NIR", "Red", "Green", "Blue", "RGB"])
            self.CalibrationFilter.setEnabled(True)
            self.CalibrationLens.clear()
            self.CalibrationLens.addItems(["3.97mm"])
            self.CalibrationLens.setEnabled(False)
        elif self.CalibrationCameraModel.currentIndex() == 5:
            self.CalibrationFilter.clear()
            self.CalibrationFilter.addItems(["Blue + NIR (NDVI)"])
            self.CalibrationFilter.setEnabled(False)
            self.CalibrationLens.clear()
            self.CalibrationLens.addItems(["3.97mm"])
            self.CalibrationLens.setEnabled(False)
        elif self.CalibrationCameraModel.currentIndex() == 5:
            self.CalibrationFilter.clear()
            self.CalibrationFilter.addItems(["Red + NIR (NDVI)"])
            self.CalibrationFilter.setEnabled(False)
            self.CalibrationLens.clear()
            self.CalibrationLens.addItems(["3.97mm"])
            self.CalibrationLens.setEnabled(False)

        elif self.CalibrationCameraModel.currentIndex() == 6:
            self.CalibrationFilter.clear()
            self.CalibrationFilter.addItems(["Red + NIR (NDVI)"])
            self.CalibrationFilter.setEnabled(False)
            self.CalibrationLens.clear()
            self.CalibrationLens.addItems(["3.97mm"])
            self.CalibrationLens.setEnabled(False)

        elif self.CalibrationCameraModel.currentIndex() == 7:
            self.CalibrationFilter.clear()
            self.CalibrationFilter.addItems(["RGN"])
            self.CalibrationFilter.setEnabled(False)
            self.CalibrationLens.clear()
            self.CalibrationLens.addItems(["3.97mm"])
            self.CalibrationLens.setEnabled(False)
        elif self.CalibrationCameraModel.currentIndex() > 7:
            self.CalibrationFilter.clear()
            self.CalibrationFilter.addItems(["Red + NIR (NDVI)"])
            self.CalibrationFilter.setEnabled(False)
            self.CalibrationLens.clear()
            self.CalibrationLens.addItems(["3.97mm"])
            self.CalibrationLens.setEnabled(False)


        else:
            self.CalibrationLens.clear()
            self.CalibrationFilter.setEnabled(False)
            self.CalibrationLens.clear()
            self.CalibrationLens.setEnabled(False)

    def on_PreProcessInButton_released(self):
        with open(modpath + os.sep + "instring.txt", "r+") as instring:
            self.PreProcessInFolder.setText(QtWidgets.QFileDialog.getExistingDirectory(directory=instring.read()))
            instring.truncate(0)
            instring.seek(0)
            instring.write(self.PreProcessInFolder.text())

    def on_PreProcessOutButton_released(self):
        with open(modpath + os.sep + "instring.txt", "r+") as instring:
            self.PreProcessOutFolder.setText(QtWidgets.QFileDialog.getExistingDirectory(directory=instring.read()))
            instring.truncate(0)
            instring.seek(0)
            instring.write(self.PreProcessOutFolder.text())


    def on_PreProcessButton_released(self):
        if self.PreProcessCameraModel.currentIndex() == -1:
            self.PreProcessLog.append("Attention! Please select a camera model.\n")
        else:
            # self.PreProcessLog.append(r'Extracting vignette corection data')


            infolder = self.PreProcessInFolder.text()
            outdir = self.PreProcessOutFolder.text()

            foldercount = 1
            endloop = False
            while endloop is False:
                outfolder = outdir + os.sep + "Processed_" + str(foldercount)
                if os.path.exists(outfolder):
                    foldercount += 1
                else:
                    os.mkdir(outfolder)
                    endloop = True

            self.PreProcessLog.append("Input folder: " + infolder)
            self.PreProcessLog.append("Output folder: " + outfolder)
            self.preProcessHelper(infolder, outfolder)
            self.PreProcessLog.append("Finished Processing Images.")
            # if os.path.exists(modpath + os.sep + 'Vig'):
            #     shutil.rmtree(modpath + os.sep + 'Vig')

                # Pre-Process Steps: End

                # Calibration Steps: Start

    def on_CalibrationInButton_released(self):
        with open(modpath + os.sep + "instring.txt", "r+") as instring:
            self.CalibrationInFolder.setText(QtWidgets.QFileDialog.getExistingDirectory(directory=instring.read()))
            instring.truncate(0)
            instring.seek(0)
            instring.write(self.CalibrationInFolder.text())
    def on_CalibrationInButton_2_released(self):
        with open(modpath + os.sep + "instring.txt", "r+") as instring:
            self.CalibrationInFolder_2.setText(QtWidgets.QFileDialog.getExistingDirectory(directory=instring.read()))
            instring.truncate(0)
            instring.seek(0)
            instring.write(self.CalibrationInFolder_2.text())
    def on_CalibrationInButton_3_released(self):
        with open(modpath + os.sep + "instring.txt", "r+") as instring:
            self.CalibrationInFolder_3.setText(QtWidgets.QFileDialog.getExistingDirectory(directory=instring.read()))
            instring.truncate(0)
            instring.seek(0)
            instring.write(self.CalibrationInFolder_3.text())
    def on_CalibrationInButton_4_released(self):
        with open(modpath + os.sep + "instring.txt", "r+") as instring:
            self.CalibrationInFolder_4.setText(QtWidgets.QFileDialog.getExistingDirectory(directory=instring.read()))
            instring.truncate(0)
            instring.seek(0)
            instring.write(self.CalibrationInFolder_4.text())
    def on_CalibrationInButton_5_released(self):
        with open(modpath + os.sep + "instring.txt", "r+") as instring:
            self.CalibrationInFolder_5.setText(QtWidgets.QFileDialog.getExistingDirectory(directory=instring.read()))
            instring.truncate(0)
            instring.seek(0)
            instring.write(self.CalibrationInFolder_5.text())
    def on_CalibrationInButton_6_released(self):
        with open(modpath + os.sep + "instring.txt", "r+") as instring:
            self.CalibrationInFolder_6.setText(QtWidgets.QFileDialog.getExistingDirectory(directory=instring.read()))
            instring.truncate(0)
            instring.seek(0)
            instring.write(self.CalibrationInFolder_6.text())


    def on_CalibrationQRButton_released(self):
        with open(modpath + os.sep + "instring.txt", "r+") as instring:
            self.CalibrationQRFile.setText(QtWidgets.QFileDialog.getOpenFileName(directory=instring.read())[0])
            instring.truncate(0)
            instring.seek(0)
            instring.write(self.CalibrationQRFile.text())
    def on_CalibrationQRButton_2_released(self):
        with open(modpath + os.sep + "instring.txt", "r+") as instring:
            self.CalibrationQRFile_2.setText(QtWidgets.QFileDialog.getOpenFileName(directory=instring.read())[0])
            instring.truncate(0)
            instring.seek(0)
            instring.write(self.CalibrationQRFile_2.text())
    def on_CalibrationQRButton_3_released(self):
        with open(modpath + os.sep + "instring.txt", "r+") as instring:
            self.CalibrationQRFile_3.setText(QtWidgets.QFileDialog.getOpenFileName(directory=instring.read())[0])
            instring.truncate(0)
            instring.seek(0)
            instring.write(self.CalibrationQRFile_3.text())
    def on_CalibrationQRButton_4_released(self):
        with open(modpath + os.sep + "instring.txt", "r+") as instring:
            self.CalibrationQRFile_4.setText(QtWidgets.QFileDialog.getOpenFileName(directory=instring.read())[0])
            instring.truncate(0)
            instring.seek(0)
            instring.write(self.CalibrationQRFile_4.text())
    def on_CalibrationQRButton_5_released(self):
        with open(modpath + os.sep + "instring.txt", "r+") as instring:
            self.CalibrationQRFile_5.setText(QtWidgets.QFileDialog.getOpenFileName(directory=instring.read())[0])
            instring.truncate(0)
            instring.seek(0)
            instring.write(self.CalibrationQRFile_5.text())
    def on_CalibrationQRButton_6_released(self):
        with open(modpath + os.sep + "instring.txt", "r+") as instring:
            self.CalibrationQRFile_6.setText(QtWidgets.QFileDialog.getOpenFileName(directory=instring.read())[0])
            instring.truncate(0)
            instring.seek(0)
            instring.write(self.CalibrationQRFile_6.text())

    def on_CalibrationGenButton_released(self):
        if self.CalibrationCameraModel.currentIndex() == -1:
            self.CalibrationLog.append("Attention! Please select a camera model.\n")
        elif len(self.CalibrationQRFile.text()) > 0:
            self.qrcoeffs = self.findQR(self.CalibrationQRFile.text())
            self.useqr = True
        else:
            self.CalibrationLog.append("Attention! Please select a target image.\n")
    def on_CalibrationGenButton_2_released(self):
        if self.CalibrationCameraModel.currentIndex() == -1:
            self.CalibrationLog.append("Attention! Please select a camera model.\n")
        elif len(self.CalibrationQRFile_2.text()) > 0:
            self.qrcoeffs2 = self.findQR(self.CalibrationQRFile_2.text())
            self.useqr = True
        else:
            self.CalibrationLog.append("Attention! Please select a target image.\n")
    def on_CalibrationGenButton_3_released(self):
        if self.CalibrationCameraModel.currentIndex() == -1:
            self.CalibrationLog.append("Attention! Please select a camera model.\n")
        elif len(self.CalibrationQRFile_3.text()) > 0:
            self.qrcoeffs3 = self.findQR(self.CalibrationQRFile_3.text())
            self.useqr = True
        else:
            self.CalibrationLog.append("Attention! Please select a target image.\n")
    def on_CalibrationGenButton_4_released(self):
        if self.CalibrationCameraModel.currentIndex() == -1:
            self.CalibrationLog.append("Attention! Please select a camera model.\n")
        elif len(self.CalibrationQRFile_4.text()) > 0:
            self.qrcoeffs4 = self.findQR(self.CalibrationQRFile_4.text())
            self.useqr = True
        else:
            self.CalibrationLog.append("Attention! Please select a target image.\n")
    def on_CalibrationGenButton_5_released(self):
        if self.CalibrationCameraModel.currentIndex() == -1:
            self.CalibrationLog.append("Attention! Please select a camera model.\n")
        elif len(self.CalibrationQRFile_5.text()) > 0:
            self.qrcoeffs5 = self.findQR(self.CalibrationQRFile_5.text())
            self.useqr = True
        else:
            self.CalibrationLog.append("Attention! Please select a target image.\n")
    def on_CalibrationGenButton_6_released(self):
        if self.CalibrationCameraModel.currentIndex() == -1:
            self.CalibrationLog.append("Attention! Please select a camera model.\n")
        elif len(self.CalibrationQRFile_6.text()) > 0:
            self.qrcoeffs6 = self.findQR(self.CalibrationQRFile_6.text())
            self.useqr = True
        else:
            self.CalibrationLog.append("Attention! Please select a target image.\n")

    def on_CalibrateButton_released(self):
        try:
            if self.CalibrationCameraModel.currentIndex() == -1:
                self.CalibrationLog.append("Attention! Please select a camera model.\n")
            elif len(self.CalibrationInFolder.text()) <= 0:
                self.CalibrationLog.append("Attention! Please select a calibration folder.\n")
            else:
                self.firstpass = True
                # self.CalibrationLog.append("CSV Input: \n" + str(self.refvalues))
                # self.CalibrationLog.append("Calibration button pressed.\n")
                calfolder = self.CalibrationInFolder.text()
                calfolder2 = self.CalibrationInFolder_2.text()
                calfolder3 = self.CalibrationInFolder_3.text()
                calfolder4 = self.CalibrationInFolder_4.text()
                calfolder5 = self.CalibrationInFolder_5.text()
                calfolder6 = self.CalibrationInFolder_6.text()
                pixel_min_max = {"redmax": 0.0, "redmin": 65535.0,
                                 "greenmax": 0.0, "greenmin": 65535.0,
                                 "bluemax": 0.0, "bluemin": 65535.0}
                # self.CalibrationLog.append("Calibration target folder is: " + calfolder + "\n")
                files_to_calibrate = []
                files_to_calibrate2 = []
                files_to_calibrate3 = []
                files_to_calibrate4 = []
                files_to_calibrate5 = []
                files_to_calibrate6 = []

                # self.CalibrationLog.append("Files to calibrate[0]: " + files_to_calibrate[0])







                if self.CalibrationCameraModel.currentIndex() > 2:
                    if os.path.exists(calfolder):
                        # print("Cal1")
                        files_to_calibrate = []
                        os.chdir(calfolder)
                        files_to_calibrate.extend(glob.glob("." + os.sep + "*.[tT][iI][fF]"))
                        files_to_calibrate.extend(glob.glob("." + os.sep + "*.[tT][iI][fF][fF]"))
                        files_to_calibrate.extend(glob.glob("." + os.sep + "*.[jJ][pP][gG]"))
                        files_to_calibrate.extend(glob.glob("." + os.sep + "*.[jJ][pP][eE][gG]"))
                        print(str(files_to_calibrate))
                        if "tif" or "TIF" or "jpg" or "JPG" in files_to_calibrate[0]:
                            # self.CalibrationLog.append("Found files to Calibrate.\n")
                            foldercount = 1
                            endloop = False
                            while endloop is False:
                                outdir = calfolder + os.sep + "Calibrated_" + str(foldercount)
                                if os.path.exists(outdir):
                                    foldercount += 1
                                else:
                                    os.mkdir(outdir)
                                    endloop = True
                            for calpixel in files_to_calibrate:
                                # print("MM1")
                                os.chdir(calfolder)
                                temp1 = cv2.imread(calpixel, -1)
                                self.monominmax["min"] = min(temp1.min(), self.monominmax["min"])
                                self.monominmax["max"] = max(temp1.max(), self.monominmax["max"])
                            # or calfile in files_to_calibrate:
                            # # print("cb1")
                            # os.chdir(calfolder)
                            # if self.useqr == True:
                            #     # self.CalibrationLog.append("Using QR")
                            #     self.CalibrateMono(calfile, self.qrcoeffs, outdir)
                            # else:
                            #     if self.CalibrationFilter.currentIndex() == 0:
                            #         self.CalibrateMono(calfile, self.BASE_COEFF_KERNEL_F590, outdir)
                            #     elif self.CalibrationFilter.currentIndex() == 1:
                            #         self.CalibrateMono(calfile, self.BASE_COEFF_KERNEL_F650, outdir)
                            #     elif self.CalibrationFilter.currentIndex() == 2:
                            #         self.CalibrateMono(calfile, self.BASE_COEFF_KERNEL_F850, outdir)

                    for calpixel in files_to_calibrate:

                        img = cv2.imread(calpixel, -1)
                        # imsize = np.shape(img)
                        # if imsize[0] > self.imcols or imsize[1] > self.imrows:
                        #     if "tif" or "TIF" in calpixel:
                        #         tempimg = np.memmap(calpixel, dtype=np.uint16, shape=(imsize))
                        #         refimg = None
                        #         refimg = tempimg
                        #     else:
                        #         tempimg = np.memmap(calpixel, dtype=np.uint8, shape=(imsize))
                        #         refimg = None
                        #         refimg = tempimg

                        if self.CalibrationCameraModel.currentIndex() == 5:  # Survey1_NDVI
                            # img = img.astype('float')

                            img[:, :, 0] = img[:, :, 0] - ((img[:, :, 2] / 5) * 4)
                        elif ((self.CalibrationCameraModel.currentIndex() == 3) or (self.CalibrationCameraModel.currentIndex() == 4)) and self.CalibrationFilter.currentIndex() == 0 \
                                or self.CalibrationCameraModel.currentIndex() > 4:  # Survey2 NDVI, DJI NDVI cameras
                            # img = img.astype('float')

                            img[:, :, 2] = img[:, :, 2] - ((img[:, :, 0] / 5) * 4)
                        # these are a little confusing, but the check to find the highest and lowest pixel value
                        # in each channel in each image and keep the highest/lowest value found.
                        pixel_min_max["redmax"] = max(img[:, :, 2].max(), pixel_min_max["redmax"])
                        pixel_min_max["redmin"] = min(img[:, :, 2].min(), pixel_min_max["redmin"])
                        pixel_min_max["greenmax"] = max(img[:, :, 1].max(), pixel_min_max["greenmax"])
                        pixel_min_max["greenmin"] = min(img[:, :, 1].min(), pixel_min_max["greenmin"])
                        pixel_min_max["bluemax"] = max(img[:, :, 0].max(), pixel_min_max["bluemax"])
                        pixel_min_max["bluemin"] = min(img[:, :, 0].min(), pixel_min_max["bluemin"])

                    if self.useqr == True:
                        pixel_min_max["redmax"] = pixel_min_max["redmax"] * self.qrcoeffs[1] + self.qrcoeffs[0]
                        pixel_min_max["redmin"] = pixel_min_max["redmin"] * self.qrcoeffs[1] + self.qrcoeffs[0]
                        pixel_min_max["greenmax"] = pixel_min_max["greenmax"] * self.qrcoeffs[3] + self.qrcoeffs[2]
                        pixel_min_max["greenmin"] = pixel_min_max["greenmin"] * self.qrcoeffs[3] + self.qrcoeffs[2]
                        pixel_min_max["bluemax"] = pixel_min_max["bluemax"] * self.qrcoeffs[5] + self.qrcoeffs[4]
                        pixel_min_max["bluemin"] = pixel_min_max["bluemin"] * self.qrcoeffs[5] + self.qrcoeffs[4]

                    else:
                        if self.CalibrationCameraModel.currentIndex() == 5:  # Survey1_NDVI
                                pixel_min_max["redmax"] = (pixel_min_max["redmax"] * self.BASE_COEFF_SURVEY1_NDVI_JPG[1]) \
                                                          + self.BASE_COEFF_SURVEY1_NDVI_JPG[0]
                                pixel_min_max["redmin"] = (pixel_min_max["redmin"] * self.BASE_COEFF_SURVEY1_NDVI_JPG[1]) \
                                                          + self.BASE_COEFF_SURVEY1_NDVI_JPG[0]
                                pixel_min_max["bluemin"] = (pixel_min_max["bluemin"] * self.BASE_COEFF_SURVEY1_NDVI_JPG[3]) \
                                                           + self.BASE_COEFF_SURVEY1_NDVI_JPG[2]
                                pixel_min_max["bluemax"] = (pixel_min_max["bluemax"] * self.BASE_COEFF_SURVEY1_NDVI_JPG[3]) \
                                                           + self.BASE_COEFF_SURVEY1_NDVI_JPG[2]
                        elif ((self.CalibrationCameraModel.currentIndex() == 3) or (self.CalibrationCameraModel.currentIndex() == 4)) and self.CalibrationFilter.currentIndex() == 0:
                            if "tif" or "TIF" in calpixel:
                                pixel_min_max["redmax"] = (pixel_min_max["redmax"] * self.BASE_COEFF_SURVEY2_NDVI_TIF[1]) \
                                                          + self.BASE_COEFF_SURVEY2_NDVI_TIF[0]
                                pixel_min_max["redmin"] = (pixel_min_max["redmin"] * self.BASE_COEFF_SURVEY2_NDVI_TIF[1]) \
                                                          + self.BASE_COEFF_SURVEY2_NDVI_TIF[0]
                                pixel_min_max["bluemin"] = (pixel_min_max["bluemin"] * self.BASE_COEFF_SURVEY2_NDVI_TIF[3]) \
                                                           + self.BASE_COEFF_SURVEY2_NDVI_TIF[2]
                                pixel_min_max["bluemax"] = (pixel_min_max["bluemax"] * self.BASE_COEFF_SURVEY2_NDVI_TIF[3]) \
                                                           + self.BASE_COEFF_SURVEY2_NDVI_TIF[2]
                            elif "jpg" or "JPG" in calpixel:
                                pixel_min_max["redmax"] = (pixel_min_max["redmax"] * self.BASE_COEFF_SURVEY2_NDVI_JPG[1]) \
                                                          + self.BASE_COEFF_SURVEY2_NDVI_JPG[0]
                                pixel_min_max["redmin"] = (pixel_min_max["redmin"] * self.BASE_COEFF_SURVEY2_NDVI_JPG[1]) \
                                                          + self.BASE_COEFF_SURVEY2_NDVI_JPG[0]
                                pixel_min_max["bluemin"] = (pixel_min_max["bluemin"] * self.BASE_COEFF_SURVEY2_NDVI_JPG[3]) \
                                                           + self.BASE_COEFF_SURVEY2_NDVI_JPG[2]
                                pixel_min_max["bluemax"] = (pixel_min_max["bluemax"] * self.BASE_COEFF_SURVEY2_NDVI_JPG[3]) \
                                                           + self.BASE_COEFF_SURVEY2_NDVI_JPG[2]
                        elif self.CalibrationCameraModel.currentIndex() == 8:
                            if "tif" or "TIF" in calpixel:
                                pixel_min_max["redmax"] = (pixel_min_max["redmax"] * self.BASE_COEFF_DJIX3_NDVI_TIF[1]) \
                                                          + self.BASE_COEFF_DJIX3_NDVI_TIF[0]
                                pixel_min_max["redmin"] = (pixel_min_max["redmin"] * self.BASE_COEFF_DJIX3_NDVI_TIF[1]) \
                                                          + self.BASE_COEFF_DJIX3_NDVI_TIF[0]
                                pixel_min_max["bluemin"] = (pixel_min_max["bluemin"] * self.BASE_COEFF_DJIX3_NDVI_TIF[3]) \
                                                           + self.BASE_COEFF_DJIX3_NDVI_TIF[2]
                                pixel_min_max["bluemax"] = (pixel_min_max["bluemax"] * self.BASE_COEFF_DJIX3_NDVI_TIF[3]) \
                                                           + self.BASE_COEFF_DJIX3_NDVI_TIF[2]
                            elif "jpg" or "JPG" in calpixel:
                                pixel_min_max["redmax"] = (pixel_min_max["redmax"] * self.BASE_COEFF_DJIX3_NDVI_JPG[1]) \
                                                          + self.BASE_COEFF_DJIX3_NDVI_JPG[0]
                                pixel_min_max["redmin"] = (pixel_min_max["redmin"] * self.BASE_COEFF_DJIX3_NDVI_JPG[1]) \
                                                          + self.BASE_COEFF_DJIX3_NDVI_JPG[0]
                                pixel_min_max["bluemin"] = (pixel_min_max["bluemin"] * self.BASE_COEFF_DJIX3_NDVI_JPG[3]) \
                                                           + self.BASE_COEFF_DJIX3_NDVI_JPG[2]
                                pixel_min_max["bluemax"] = (pixel_min_max["bluemax"] * self.BASE_COEFF_DJIX3_NDVI_JPG[3]) \
                                                           + self.BASE_COEFF_DJIX3_NDVI_JPG[2]
                        elif self.CalibrationCameraModel.currentIndex() == 5:
                            if "tif" or "TIF" in calpixel:
                                pixel_min_max["redmax"] = (
                                                          pixel_min_max["redmax"] * self.BASE_COEFF_DJIPHANTOM4_NDVI_TIF[1]) \
                                                          + self.BASE_COEFF_DJIPHANTOM4_NDVI_TIF[0]
                                pixel_min_max["redmin"] = (
                                                          pixel_min_max["redmin"] * self.BASE_COEFF_DJIPHANTOM4_NDVI_TIF[1]) \
                                                          + self.BASE_COEFF_DJIPHANTOM4_NDVI_TIF[0]
                                pixel_min_max["bluemin"] = (pixel_min_max["bluemin"] * self.BASE_COEFF_DJIPHANTOM4_NDVI_TIF[
                                    3]) \
                                                           + self.BASE_COEFF_DJIPHANTOM4_NDVI_TIF[2]
                                pixel_min_max["bluemax"] = (pixel_min_max["bluemax"] * self.BASE_COEFF_DJIPHANTOM4_NDVI_TIF[
                                    3]) \
                                                           + self.BASE_COEFF_DJIPHANTOM4_NDVI_TIF[2]
                            elif "jpg" or "JPG" in calpixel:
                                pixel_min_max["redmax"] = (
                                                          pixel_min_max["redmax"] * self.BASE_COEFF_DJIPHANTOM4_NDVI_JPG[1]) \
                                                          + self.BASE_COEFF_DJIPHANTOM4_NDVI_JPG[0]
                                pixel_min_max["redmin"] = (
                                                          pixel_min_max["redmin"] * self.BASE_COEFF_DJIPHANTOM4_NDVI_JPG[1]) \
                                                          + self.BASE_COEFF_DJIPHANTOM4_NDVI_JPG[0]
                                pixel_min_max["bluemin"] = (pixel_min_max["bluemin"] * self.BASE_COEFF_DJIPHANTOM4_NDVI_JPG[
                                    3]) \
                                                           + self.BASE_COEFF_DJIPHANTOM4_NDVI_JPG[2]
                                pixel_min_max["bluemax"] = (pixel_min_max["bluemax"] * self.BASE_COEFF_DJIPHANTOM4_NDVI_JPG[
                                    3]) \
                                                           + self.BASE_COEFF_DJIPHANTOM4_NDVI_JPG[2]
                        elif self.CalibrationCameraModel.currentIndex() == 6 or self.CalibrationCameraModel.currentIndex() > 7:
                            if "tif" or "TIF" in calpixel:
                                pixel_min_max["redmax"] = (
                                                          pixel_min_max["redmax"] * self.BASE_COEFF_DJIPHANTOM3_NDVI_TIF[1]) \
                                                          + self.BASE_COEFF_DJIPHANTOM3_NDVI_TIF[0]
                                pixel_min_max["redmin"] = (
                                                          pixel_min_max["redmin"] * self.BASE_COEFF_DJIPHANTOM3_NDVI_TIF[1]) \
                                                          + self.BASE_COEFF_DJIPHANTOM3_NDVI_TIF[0]
                                pixel_min_max["bluemin"] = (pixel_min_max["bluemin"] * self.BASE_COEFF_DJIPHANTOM3_NDVI_TIF[
                                    3]) \
                                                           + self.BASE_COEFF_DJIPHANTOM3_NDVI_TIF[2]
                                pixel_min_max["bluemax"] = (pixel_min_max["bluemax"] * self.BASE_COEFF_DJIPHANTOM3_NDVI_TIF[
                                    3]) \
                                                           + self.BASE_COEFF_DJIPHANTOM3_NDVI_TIF[2]
                            elif "jpg" or "JPG" in calpixel:
                                pixel_min_max["redmax"] = (
                                                          pixel_min_max["redmax"] * self.BASE_COEFF_DJIPHANTOM3_NDVI_TIF[1]) \
                                                          + self.BASE_COEFF_DJIPHANTOM3_NDVI_TIF[0]
                                pixel_min_max["redmin"] = (
                                                          pixel_min_max["redmin"] * self.BASE_COEFF_DJIPHANTOM3_NDVI_TIF[1]) \
                                                          + self.BASE_COEFF_DJIPHANTOM3_NDVI_TIF[0]
                                pixel_min_max["bluemin"] = (pixel_min_max["bluemin"] * self.BASE_COEFF_DJIPHANTOM3_NDVI_TIF[
                                    3]) \
                                                           + self.BASE_COEFF_DJIPHANTOM3_NDVI_TIF[2]
                                pixel_min_max["bluemax"] = (pixel_min_max["bluemax"] * self.BASE_COEFF_DJIPHANTOM3_NDVI_TIF[
                                    3]) \
                                                           + self.BASE_COEFF_DJIPHANTOM3_NDVI_TIF[2]

                    for calfile in files_to_calibrate:

                        cameramodel = self.CalibrationCameraModel.currentIndex()
                        if self.useqr == True:
                            # self.CalibrationLog.append("Using QR")
                            try:
                                self.CalibratePhotos(calfile, self.qrcoeffs, pixel_min_max, outdir)
                            except Exception as e:
                                print(str(e))
                        else:
                            # self.CalibrationLog.append("NOT Using QR")
                            if cameramodel == 3 and self.CalibrationFilter.currentIndex() == 0:  # Survey2 NDVI
                                if "TIF" in calfile.split('.')[2].upper():
                                    self.CalibratePhotos(calfile, self.BASE_COEFF_SURVEY2_NDVI_TIF, pixel_min_max, outdir)
                                elif "JPG" in calfile.split('.')[2].upper():
                                    self.CalibratePhotos(calfile, self.BASE_COEFF_SURVEY2_NDVI_JPG, pixel_min_max, outdir)
                            elif cameramodel == 3 and self.CalibrationFilter.currentIndex() == 1:  # Survey2 NIR
                                if "TIF" in calfile.split('.')[2].upper():
                                    self.CalibratePhotos(calfile, self.BASE_COEFF_SURVEY2_NIR_TIF, pixel_min_max, outdir)
                                elif "JPG" in calfile.split('.')[2].upper():
                                    self.CalibratePhotos(calfile, self.BASE_COEFF_SURVEY2_NIR_JPG, pixel_min_max, outdir)
                            elif cameramodel == 3 and self.CalibrationFilter.currentIndex() == 2:  # Survey2 RED
                                if "TIF" in calfile.split('.')[2].upper():
                                    self.CalibratePhotos(calfile, self.BASE_COEFF_SURVEY2_RED_TIF, pixel_min_max, outdir)
                                elif "JPG" in calfile.split('.')[2].upper():
                                    self.CalibratePhotos(calfile, self.BASE_COEFF_SURVEY2_RED_JPG, pixel_min_max, outdir)
                            elif cameramodel == 3 and self.CalibrationFilter.currentIndex() == 3:  # Survey2 GREEN
                                if "TIF" in calfile.split('.')[2].upper():
                                    self.CalibratePhotos(calfile, self.BASE_COEFF_SURVEY2_GREEN_TIF, pixel_min_max, outdir)
                                elif "JPG" in calfile.split('.')[2].upper():
                                    self.CalibratePhotos(calfile, self.BASE_COEFF_SURVEY2_GREEN_JPG, pixel_min_max, outdir)
                            elif cameramodel == 3 and self.CalibrationFilter.currentIndex() == 4:  # Survey2 BLUE
                                if "TIF" in calfile.split('.')[2].upper():
                                    self.CalibratePhotos(calfile, self.BASE_COEFF_SURVEY2_BLUE_TIF, pixel_min_max, outdir)
                                elif "JPG" in calfile.split('.')[2].upper():
                                    self.CalibratePhotos(calfile, self.BASE_COEFF_SURVEY2_BLUE_JPG, pixel_min_max, outdir)
                            elif cameramodel == 4:  # Survey1 NDVI
                                if "JPG" in calfile.split('.')[2].upper():
                                    self.CalibratePhotos(calfile, self.BASE_COEFF_SURVEY1_NDVI_JPG, pixel_min_max, outdir)
                            elif cameramodel == 8:  # DJI X3 NDVI
                                if "TIF" in calfile.split('.')[2].upper():
                                    self.CalibratePhotos(calfile, self.BASE_COEFF_DJIX3_NDVI_TIF, pixel_min_max, outdir)
                                elif "JPG" in calfile.split('.')[2].upper():
                                    self.CalibratePhotos(calfile, self.BASE_COEFF_DJIX3_NDVI_JPG, pixel_min_max, outdir)
                            elif cameramodel == 5:  # DJI Phantom4 NDVI
                                if "TIF" in calfile.split('.')[2].upper():
                                    self.CalibratePhotos(calfile, self.BASE_COEFF_DJIPHANTOM4_NDVI_TIF, pixel_min_max,
                                                         outdir)
                                elif "JPG" in calfile.split('.')[2].upper():
                                    self.CalibratePhotos(calfile, self.BASE_COEFF_DJIPHANTOM4_NDVI_JPG, pixel_min_max,
                                                         outdir)
                            elif cameramodel == 6 or cameramodel == 7:  # DJI PHANTOM3 NDVI
                                if "TIF" in calfile.split('.')[2].upper():
                                    self.CalibratePhotos(calfile, self.BASE_COEFF_DJIPHANTOM3_NDVI_TIF, pixel_min_max,
                                                         outdir)
                                elif "JPG" in calfile.split('.')[2].upper():
                                    self.CalibratePhotos(calfile, self.BASE_COEFF_DJIPHANTOM3_NDVI_JPG, pixel_min_max,
                                                         outdir)
                            else:
                                self.CalibrationLog.append(
                                    "No default calibration data for selected camera model. Please please supply a MAPIR Reflectance Target to proceed.\n")
                                break
                else:
                    if os.path.exists(calfolder):
                        # print("Cal1")
                        files_to_calibrate = []
                        os.chdir(calfolder)
                        files_to_calibrate.extend(glob.glob("." + os.sep + "*.[tT][iI][fF]"))
                        files_to_calibrate.extend(glob.glob("." + os.sep + "*.[tT][iI][fF][fF]"))
                        files_to_calibrate.extend(glob.glob("." + os.sep + "*.[jJ][pP][gG]"))
                        files_to_calibrate.extend(glob.glob("." + os.sep + "*.[jJ][pP][eE][gG]"))
                        print(str(files_to_calibrate))
                        if "tif" or "TIF" or "jpg" or "JPG" in files_to_calibrate[0]:
                            # self.CalibrationLog.append("Found files to Calibrate.\n")
                            foldercount = 1
                            endloop = False
                            while endloop is False:
                                outdir = calfolder + os.sep + "Calibrated_" + str(foldercount)
                                if os.path.exists(outdir):
                                    foldercount += 1
                                else:
                                    os.mkdir(outdir)
                                    endloop = True
                            for calpixel in files_to_calibrate:
                                # print("MM1")
                                os.chdir(calfolder)
                                temp1 = cv2.imread(calpixel, -1)
                                self.monominmax["min"] = min(temp1.min(), self.monominmax["min"])
                                self.monominmax["max"] = max(temp1.max(), self.monominmax["max"])
                            for calfile in files_to_calibrate:
                                # print("cb1")
                                os.chdir(calfolder)
                                if self.useqr == True:
                                    # self.CalibrationLog.append("Using QR")
                                    self.CalibrateMono(calfile, self.qrcoeffs, outdir)
                                else:
                                    if self.CalibrationFilter.currentIndex() == 0:
                                        self.CalibrateMono(calfile, self.BASE_COEFF_KERNEL_F590, outdir)
                                    elif self.CalibrationFilter.currentIndex() == 1:
                                        self.CalibrateMono(calfile, self.BASE_COEFF_KERNEL_F650, outdir)
                                    elif self.CalibrationFilter.currentIndex() == 2:
                                        self.CalibrateMono(calfile, self.BASE_COEFF_KERNEL_F850, outdir)
                    if os.path.exists(calfolder2):
    #                     # print("Cal2")
                        files_to_calibrate2 = []
                        os.chdir(calfolder2)
                        files_to_calibrate2.extend(glob.glob("." + os.sep + "*.[tT][iI][fF]"))
                        files_to_calibrate2.extend(glob.glob("." + os.sep + "*.[tT][iI][fF][fF]"))
                        files_to_calibrate2.extend(glob.glob("." + os.sep + "*.[jJ][pP][gG]"))
                        files_to_calibrate2.extend(glob.glob("." + os.sep + "*.[jJ][pP][eE][gG]"))
                        print(str(files_to_calibrate2))
                        if "tif" or "TIF" or "jpg" or "JPG" in files_to_calibrate2[0]:
                            foldercount = 1
                            endloop = False
                            while endloop is False:
                                outdir2 = calfolder2 + os.sep + "Calibrated_" + str(foldercount)
                                if os.path.exists(outdir2):
                                    foldercount += 1
                                else:
                                    os.mkdir(outdir2)
                                    endloop = True
                            for calpixel2 in files_to_calibrate2:
                                # print("MM2")
                                os.chdir(calfolder2)
                                temp2 = cv2.imread(calpixel2, -1)

                                self.monominmax["min"] = min(temp2.min(), self.monominmax["min"])
                                self.monominmax["max"] = max(temp2.max(), self.monominmax["max"])
                            for calfile2 in files_to_calibrate2:
                                # print("cb2")
                                os.chdir(calfolder2)
                                if self.useqr == True:
                                    # self.CalibrationLog.append("Using QR")
                                    self.CalibrateMono(calfile2, self.qrcoeffs2, outdir2)
                                else:
                                    if self.CalibrationFilter.currentIndex() == 0:
                                        self.CalibrateMono(calfile2, self.BASE_COEFF_KERNEL_F590, outdir2)
                                    elif self.CalibrationFilter.currentIndex() == 1:
                                        self.CalibrateMono(calfile2, self.BASE_COEFF_KERNEL_F650, outdir2)
                                    elif self.CalibrationFilter.currentIndex() == 2:
                                        self.CalibrateMono(calfile2, self.BASE_COEFF_KERNEL_F850, outdir2)
                    if os.path.exists(calfolder3):
    #                     # print("Cal3")
                        files_to_calibrate3 = []
                        os.chdir(calfolder3)
                        files_to_calibrate3.extend(glob.glob("." + os.sep + "*.[tT][iI][fF]"))
                        files_to_calibrate3.extend(glob.glob("." + os.sep + "*.[tT][iI][fF][fF]"))
                        files_to_calibrate3.extend(glob.glob("." + os.sep + "*.[jJ][pP][gG]"))
                        files_to_calibrate3.extend(glob.glob("." + os.sep + "*.[jJ][pP][eE][gG]"))
                        print(str(files_to_calibrate3))
                        if "tif" or "TIF" or "jpg" or "JPG" in files_to_calibrate3[0]:
                            foldercount = 1
                            endloop = False
                            while endloop is False:
                                outdir3 = calfolder3 + os.sep + "Calibrated_" + str(foldercount)
                                if os.path.exists(outdir3):
                                    foldercount += 1
                                else:
                                    os.mkdir(outdir3)
                                    endloop = True
                            for calpixel3 in files_to_calibrate3:
                                # print("MM3")
                                os.chdir(calfolder3)
                                temp3 = cv2.imread(calpixel3, -1)

                                self.monominmax["min"] = min(temp3.min(), self.monominmax["min"])
                                self.monominmax["max"] = max(temp3.max(), self.monominmax["max"])
                            for calfile3 in files_to_calibrate3:
                                # print("cb3")
                                os.chdir(calfolder3)
                                if self.useqr == True:
                                    # self.CalibrationLog.append("Using QR")
                                    self.CalibrateMono(calfile3, self.qrcoeffs3, outdir3)
                                else:
                                    if self.CalibrationFilter.currentIndex() == 0:
                                        self.CalibrateMono(calfile3, self.BASE_COEFF_KERNEL_F590, outdir3)
                                    elif self.CalibrationFilter.currentIndex() == 1:
                                        self.CalibrateMono(calfile3, self.BASE_COEFF_KERNEL_F650, outdir3)
                                    elif self.CalibrationFilter.currentIndex() == 2:
                                        self.CalibrateMono(calfile3, self.BASE_COEFF_KERNEL_F850, outdir3)
                    if os.path.exists(calfolder4):
                        # print("Cal4")
                        files_to_calibrate4 = []
                        os.chdir(calfolder4)
                        files_to_calibrate4.extend(glob.glob("." + os.sep + "*.[tT][iI][fF]"))
                        files_to_calibrate4.extend(glob.glob("." + os.sep + "*.[tT][iI][fF][fF]"))
                        files_to_calibrate4.extend(glob.glob("." + os.sep + "*.[jJ][pP][gG]"))
                        files_to_calibrate4.extend(glob.glob("." + os.sep + "*.[jJ][pP][eE][gG]"))
                        print(str(files_to_calibrate4))
                        if "tif" or "TIF" or "jpg" or "JPG" in files_to_calibrate4[0]:
                            foldercount = 1
                            endloop = False
                            while endloop is False:
                                outdir4 = calfolder4 + os.sep + "Calibrated_" + str(foldercount)
                                if os.path.exists(outdir4):
                                    foldercount += 1
                                else:
                                    os.mkdir(outdir4)
                                    endloop = True
                            for calpixel4 in files_to_calibrate4:
                                # print("MM4")
                                os.chdir(calfolder4)
                                temp4 = cv2.imread(calpixel4, -1)

                                self.monominmax["min"] = min(temp4.min(), self.monominmax["min"])
                                self.monominmax["max"] = max(temp4.max(), self.monominmax["max"])
                            for calfile4 in files_to_calibrate4:
                                # print("cb4")
                                os.chdir(calfolder4)
                                if self.useqr == True:
                                    # self.CalibrationLog.append("Using QR")
                                    self.CalibrateMono(calfile4, self.qrcoeffs4, outdir4)
                                else:
                                    if self.CalibrationFilter.currentIndex() == 0:
                                        self.CalibrateMono(calfile4, self.BASE_COEFF_KERNEL_F590, outdir4)
                                    elif self.CalibrationFilter.currentIndex() == 1:
                                        self.CalibrateMono(calfile4, self.BASE_COEFF_KERNEL_F650, outdir4)
                                    elif self.CalibrationFilter.currentIndex() == 2:
                                        self.CalibrateMono(calfile4, self.BASE_COEFF_KERNEL_F850, outdir4)
                    if os.path.exists(calfolder5):
                        # print("Cal5")
                        files_to_calibrate5 = []
                        os.chdir(calfolder5)
                        files_to_calibrate5.extend(glob.glob("." + os.sep + "*.[tT][iI][fF]"))
                        files_to_calibrate5.extend(glob.glob("." + os.sep + "*.[tT][iI][fF][fF]"))
                        files_to_calibrate5.extend(glob.glob("." + os.sep + "*.[jJ][pP][gG]"))
                        files_to_calibrate5.extend(glob.glob("." + os.sep + "*.[jJ][pP][eE][gG]"))
                        print(str(files_to_calibrate5))
                        if "tif" or "TIF" or "jpg" or "JPG" in files_to_calibrate5[0]:
                            foldercount = 1
                            endloop = False
                            while endloop is False:
                                outdir5 = calfolder5 + os.sep + "Calibrated_" + str(foldercount)
                                if os.path.exists(outdir5):
                                    foldercount += 1
                                else:
                                    os.mkdir(outdir5)
                                    endloop = True
                            for calpixel5 in files_to_calibrate5:
                                # print("MM5")
                                os.chdir(calfolder5)
                                temp5 = cv2.imread(calpixel5, -1)

                                self.monominmax["min"] = min(temp5.min(), self.monominmax["min"])
                                self.monominmax["max"] = max(temp5.max(), self.monominmax["max"])
                            for calfile5 in files_to_calibrate5:
                                # print("cb5")
                                os.chdir(calfolder5)
                                if self.useqr == True:
                                    # self.CalibrationLog.append("Using QR")
                                    self.CalibrateMono(calfile5, self.qrcoeffs5, outdir5)
                                else:
                                    if self.CalibrationFilter.currentIndex() == 0:
                                        self.CalibrateMono(calfile5, self.BASE_COEFF_KERNEL_F590, outdir5)
                                    elif self.CalibrationFilter.currentIndex() == 1:
                                        self.CalibrateMono(calfile5, self.BASE_COEFF_KERNEL_F650, outdir5)
                                    elif self.CalibrationFilter.currentIndex() == 2:
                                        self.CalibrateMono(calfile5, self.BASE_COEFF_KERNEL_F850, outdir5)
                    if os.path.exists(calfolder6):
                        # print("Cal6")
                        files_to_calibrate6 = []
                        os.chdir(calfolder6)
                        files_to_calibrate6.extend(glob.glob("." + os.sep + "*.[tT][iI][fF]"))
                        files_to_calibrate6.extend(glob.glob("." + os.sep + "*.[tT][iI][fF][fF]"))
                        files_to_calibrate6.extend(glob.glob("." + os.sep + "*.[jJ][pP][gG]"))
                        files_to_calibrate6.extend(glob.glob("." + os.sep + "*.[jJ][pP][eE][gG]"))
                        print(str(files_to_calibrate6))
                        if "tif" or "TIF" or "jpg" or "JPG" in files_to_calibrate6[0]:
                            foldercount = 1
                            endloop = False
                            while endloop is False:
                                outdir6 = calfolder6 + os.sep + "Calibrated_" + str(foldercount)
                                if os.path.exists(outdir6):
                                    foldercount += 1
                                else:
                                    os.mkdir(outdir6)
                                    endloop = True

                            for calpixel6 in files_to_calibrate6:
                                # print("MM6")
                                os.chdir(calfolder6)
                                temp6 = cv2.imread(calpixel6, -1)

                                self.monominmax["min"] = min(temp6.min(), self.monominmax["min"])
                                self.monominmax["max"] = max(temp6.max(), self.monominmax["max"])

                            for calfile6 in files_to_calibrate6:
                                # print("cb6")
                                os.chdir(calfolder6)
                                if self.useqr == True:
                                    # self.CalibrationLog.append("Using QR")
                                    self.CalibrateMono(calfile6, self.qrcoeffs6, outdir6)
                                else:
                                    if self.CalibrationFilter.currentIndex() == 0:
                                        self.CalibrateMono(calfile6, self.BASE_COEFF_KERNEL_F590, outdir6)
                                    elif self.CalibrationFilter.currentIndex() == 1:
                                        self.CalibrateMono(calfile6, self.BASE_COEFF_KERNEL_F650, outdir6)
                                    elif self.CalibrationFilter.currentIndex() == 2:
                                        self.CalibrateMono(calfile6, self.BASE_COEFF_KERNEL_F850, outdir6)


                self.CalibrationLog.append("Finished Calibrating " + str(len(files_to_calibrate) + len(files_to_calibrate2) + len(files_to_calibrate3) + len(files_to_calibrate4) + len(files_to_calibrate5) + len(files_to_calibrate6)) + " images\n")
        except Exception as e:
            self.CalibrationLog.append(str(e))
    def CalibrateMono(self, photo, coeffs, output_directory):
        refimg = cv2.imread(photo, -1)
        print(str(refimg))
        if len(refimg.shape) > 2:
            refimg = refimg[:,:,0]
        refimg = refimg.astype("uint16")
        pixmin = (self.monominmax["min"] * coeffs[1]) + coeffs[0]
        pixmax = (self.monominmax["max"] * coeffs[1]) + coeffs[0]
        tempim = (refimg * coeffs[1]) + coeffs[0]
        tempim -= pixmin
        tempim /= (pixmax - pixmin)
        tempim *= 65535.0

        tempim = tempim.astype("uint16")
        print(str(tempim))
        # tempim = np.floor((refimg * coeffs[1]) + coeffs[0]).astype("uint16")
        # tempim[tempim > 65535] = 65535
        # tempim[tempim < 0] = 0
        #
        # tempimg = tempim / tempim.max()
        #
        # tempimg *= 65535
        #
        # tempimg = tempimg.astype("uint16")

        refimg = tempim

        newimg = output_directory + photo.split('.')[1] + "_CALIBRATED." + photo.split('.')[2]

        cv2.imencode(".tiff", refimg)
        cv2.imwrite(newimg, refimg)
        srin = gdal.Open(photo)
        inproj = srin.GetProjection()
        transform = srin.GetGeoTransform()
        gcpcount = srin.GetGCPs()
        srout = gdal.Open(newimg, gdal.GA_Update)
        srout.SetProjection(inproj)
        srout.SetGeoTransform(transform)
        srout.SetGCPs(gcpcount, srin.GetGCPProjection())
        self.copyExif(photo, newimg)

    def CalibratePhotos(self, photo, coeffs, minmaxes, output_directory):
        refimg = cv2.imread(photo, -1)
        # imsize = np.shape(refimg)
        # if imsize[0] > self.imcols or imsize[1] > self.imrows:
        #     if "tif" or "TIF" in photo:
        #             tempimg = np.memmap(photo, dtype=np.uint16, shape=(imsize))
        #             refimg = None
        #             refimg = tempimg
        #     else:
        #             tempimg = np.memmap(photo, dtype=np.uint8, shape=(imsize))
        #             refimg = None
        #             refimg = tempimg

        ### split channels (using cv2.split caused too much overhead and made the host program crash)
        blue = refimg[:, :, 0]
        green = refimg[:, :, 1]
        red = refimg[:, :, 2]
        if refimg.shape[2] > 3:
            alpha = refimg[:, :, 3]
            refimg = refimg[:, :, :3]

        ### find the maximum and minimum pixel values over the entire directory.
        if self.CalibrationCameraModel.currentIndex() == 5:  ###Survey1 NDVI
            maxpixel = minmaxes["redmax"] if minmaxes["redmax"] > minmaxes["bluemax"] else minmaxes["bluemax"]
            minpixel = minmaxes["redmin"] if minmaxes["redmin"] < minmaxes["bluemin"] else minmaxes["bluemin"]
            blue = refimg[:, :, 0] - (refimg[:, :, 2] * 0.80)  # Subtract the NIR bleed over from the blue channel
        elif (((self.CalibrationCameraModel.currentIndex() == 3) or (self.CalibrationCameraModel.currentIndex() == 4)) and self.CalibrationFilter.currentIndex() == 1) \
                or (((self.CalibrationCameraModel.currentIndex() == 3) or (self.CalibrationCameraModel.currentIndex() == 4)) and self.CalibrationFilter.currentIndex() == 2):
            ### red and NIR
            maxpixel = minmaxes["redmax"]
            minpixel = minmaxes["redmin"]
        elif ((self.CalibrationCameraModel.currentIndex() == 3) or (self.CalibrationCameraModel.currentIndex() == 4)) and self.CalibrationFilter.currentIndex() == 3:
            ### green
            maxpixel = minmaxes["greenmax"]
            minpixel = minmaxes["greenmin"]
        elif ((self.CalibrationCameraModel.currentIndex() == 3) or (self.CalibrationCameraModel.currentIndex() == 4)) and self.CalibrationFilter.currentIndex() == 4:
            ### blue
            maxpixel = minmaxes["bluemax"]
            minpixel = minmaxes["bluemin"]
        elif (self.CalibrationCameraModel.currentIndex() < 3 and self.CalibrationFilter.currentIndex() == 10) \
                or self.CalibrationCameraModel.currentIndex() == 7:
            ### Kernel RGN
            maxpixel = minmaxes["redmax"] if minmaxes["redmax"] > minmaxes["bluemax"] else minmaxes["bluemax"]
            maxpixel = minmaxes["greenmax"] if minmaxes["greenmax"] > maxpixel else maxpixel
            minpixel = minmaxes["redmax"] if minmaxes["redmax"] < minmaxes["bluemax"] else minmaxes["bluemax"]
            minpixel = minmaxes["greenmax"] if minmaxes["greenmax"] < minpixel else minpixel
        else:  ###Survey2 NDVI or any DJI ndvi
            maxpixel = minmaxes["redmax"] if minmaxes["redmax"] > minmaxes["bluemax"] else minmaxes["bluemax"]
            minpixel = minmaxes["redmin"] if minmaxes["redmin"] < minmaxes["bluemin"] else minmaxes["bluemin"]
            red = refimg[:, :, 2] - (refimg[:, :, 0] * 0.80)  # Subtract the NIR bleed over from the red channel



            ### Calibrate pixels based on the default reflectance values (or the values gathered from the MAPIR reflectance target)
        red = (red * coeffs[1]) + coeffs[0]
        green = (green * coeffs[3]) + coeffs[2]
        blue = (blue * coeffs[5]) + coeffs[4]

        ### Scale calibrated values back down to a useable range (Adding 1 to avaoid 0 value pixels, as they will cause a
        #### devide by zero case when creating an index image.
        if photo.split('.')[2].upper() == "JPG" or photo.split('.')[
            2].upper() == "JPEG" or self.Tiff2JpgBox.checkState() > 0:
            self.CalibrationLog.append("Entering JPG")
            red = (((red - minpixel + 1) / (maxpixel - minpixel + 1)))
            green = (((green - minpixel + 1) / (maxpixel - minpixel + 1)))
            blue = (((blue - minpixel + 1) / (maxpixel - minpixel + 1)))
            self.CalibrationLog.append("Removing Gamma")
            # red = np.power(red, 0.455)
            # green = np.power(green, 0.455)
            # blue = np.power(blue, 0.455)
            red = red * 255
            green = green * 255
            blue = blue * 255
        else:
            red = (((red - minpixel + 1) / (maxpixel - minpixel + 1)) * 65535)
            green = (((green - minpixel + 1) / (maxpixel - minpixel + 1)) * 65535)
            blue = (((blue - minpixel + 1) / (maxpixel - minpixel + 1)) * 65535)

        # if photo.split('.')[2].upper() == "JPG":  # Remove the gamma correction that is automaticall applied to JPGs


            ### Merge the channels back into a single image
        refimg = cv2.merge((blue, green, red))
        if refimg.shape[2] > 3:
            white_background_image = np.ones_like(refimg, dtype=np.uint8) * 255
            a_factor = alpha[:, :, np.newaxis].astype(np.float32) / 255.0
            a_factor = np.concatenate((a_factor, a_factor, a_factor), axis=2)
            base = refimg.astype(np.float32) * a_factor
            white = white_background_image.astype(np.float32) * (1 - a_factor)
            refimg = base + white
            ### If the image is a .tiff then change it to a 16 bit color image
        if "TIF" in photo.split('.')[2].upper() and not self.Tiff2JpgBox.checkState() > 0:
            refimg = refimg.astype("uint16")

        if (((self.CalibrationCameraModel.currentIndex() == 3) or (self.CalibrationCameraModel.currentIndex() == 4)) and self.CalibrationFilter.currentIndex() == 0) \
                or self.CalibrationCameraModel.currentIndex() >= 4:
            ### Remove green information if NDVI camera
            refimg[:, :, 1] = 1
        elif (((self.CalibrationCameraModel.currentIndex() == 3) or (self.CalibrationCameraModel.currentIndex() == 4)) and self.CalibrationFilter.currentIndex() == 1) \
                or ((self.CalibrationCameraModel.currentIndex() == 3) or (self.CalibrationCameraModel.currentIndex() == 4)) and self.CalibrationFilter.currentIndex() == 2:
            ### Remove blue and green information if NIR or Red camera
            refimg[:, :, 0] = 1
            refimg[:, :, 1] = 1
        elif ((self.CalibrationCameraModel.currentIndex() == 3) or (self.CalibrationCameraModel.currentIndex() == 4)) and self.CalibrationFilter.currentIndex() == 3:
            ### Remove blue and red information if GREEN camera
            refimg[:, :, 0] = 1
            refimg[:, :, 2] = 1
        elif ((self.CalibrationCameraModel.currentIndex() == 3) or (self.CalibrationCameraModel.currentIndex() == 4)) and self.CalibrationFilter.currentIndex() == 4:
            ### Remove red and green information if BLUE camera
            refimg[:, :, 1] = 1
            refimg[:, :, 2] = 1

        if self.Tiff2JpgBox.checkState() > 0:
            self.CalibrationLog.append("Making JPG")
            cv2.imencode(".jpg", refimg)
            cv2.imwrite(output_directory + photo.split('.')[1] + "_CALIBRATED.JPG", refimg,
                        [int(cv2.IMWRITE_JPEG_QUALITY), 100])

            self.copyExif(photo, output_directory + photo.split('.')[1] + "_CALIBRATED.JPG")

        else:
            newimg = output_directory + photo.split('.')[1] + "_CALIBRATED." + photo.split('.')[2]
            if 'tif' in photo.split('.')[2].lower():
                cv2.imencode(".tiff", refimg)
                cv2.imwrite(newimg, refimg)
                srin = gdal.Open(photo)
                inproj = srin.GetProjection()
                transform = srin.GetGeoTransform()
                gcpcount = srin.GetGCPs()
                srout = gdal.Open(newimg, gdal.GA_Update)
                srout.SetProjection(inproj)
                srout.SetGeoTransform(transform)
                srout.SetGCPs(gcpcount, srin.GetGCPProjection())
                srout = None
                srin = None
            else:
                cv2.imwrite(newimg, refimg, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
            self.copyExif(photo, newimg)



####Function for finding he QR target and calculating the calibration coeficients
    def findQR(self, image):
        subprocess.call([modpath + os.sep + r'FiducialFinder.exe', image])
        list = None
        if os.path.exists(r'.' + os.sep + r'calib.txt'):
            with open(r'.' + os.sep + r'calib.txt', 'r+') as cornerfile:
                list = cornerfile.read()
                list = list.split('[')[1].split(']')[0]
        if list is not None and len(list) > 0:
            self.CalibrationLog.append(list)
            temp = np.fromstring(str(list), dtype=int, sep=',')
            coords = [[temp[0],temp[1]],[temp[2],temp[3]],[temp[6],temp[7]],[temp[4],temp[5]]]
            self.CalibrationLog.append(str(coords))
        else:
            if self.CalibrationCameraModel.currentIndex() > 2:
                im = cv2.imread(image)
                grayscale = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

                clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
                cl1 = clahe.apply(grayscale)
            else:
                self.CalibrationLog.append("Looking for QR target")
                im = cv2.imread(image, 0)
                clahe2 = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
                cl1 = clahe2.apply(im)
            denoised = cv2.fastNlMeansDenoising(cl1, None, 14, 7, 21)

            threshcounter = 17
            while threshcounter <= 255:
                ret, thresh = cv2.threshold(denoised, threshcounter, 255, 0)
                if os.name == "nt":
                    _, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
                else:
                    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
                coords = []
                count = 0

                for i in hierarchy[0]:
                    self.traverseHierarchy(hierarchy, contours, count, im, 0, coords)

                    count += 1
                if len(coords) == 3:
                    break
                else:
                    threshcounter += 17

            if len(coords) is not 3:
                self.CalibrationLog.append("Could not find MAPIR ground target.")
                return

        line1 = np.sqrt(np.power((coords[0][0] - coords[1][0]), 2) + np.power((coords[0][1] - coords[1][1]),
                                                                              2))  # Getting the distance between each centroid
        line2 = np.sqrt(np.power((coords[1][0] - coords[2][0]), 2) + np.power((coords[1][1] - coords[2][1]), 2))
        line3 = np.sqrt(np.power((coords[2][0] - coords[0][0]), 2) + np.power((coords[2][1] - coords[0][1]), 2))

        hypotenuse = line1 if line1 > line2 else line2
        hypotenuse = line3 if line3 > hypotenuse else hypotenuse

        if hypotenuse == line1:

            slope = (coords[1][1] - coords[0][1]) / (coords[1][0] - coords[0][0])
            dist = coords[2][1] - (slope * coords[2][0]) + ((slope * coords[1][0]) - coords[1][1])
            dist /= np.sqrt(np.power(slope, 2) + 1)
            center = coords[2]
            if (slope < 0 and dist < 0) or (slope >= 0 and dist >= 0):

                bottom = coords[0]
                right = coords[1]
            else:

                bottom = coords[1]
                right = coords[0]
        elif hypotenuse == line2:

            slope = (coords[2][1] - coords[1][1]) / (coords[2][0] - coords[1][0])
            dist = coords[0][1] - (slope * coords[0][0]) + ((slope * coords[2][0]) - coords[2][1])
            dist /= np.sqrt(np.power(slope, 2) + 1)
            center = coords[0]
            if (slope < 0 and dist < 0) or (slope >= 0 and dist >= 0):

                bottom = coords[1]
                right = coords[2]
            else:

                bottom = coords[2]
                right = coords[1]
        else:

            slope = (coords[0][1] - coords[2][1]) / (coords[0][0] - coords[2][0])
            dist = coords[1][1] - (slope * coords[1][0]) + ((slope * coords[0][0]) - coords[0][1])
            dist /= np.sqrt(np.power(slope, 2) + 1)
            center = coords[1]
            if (slope < 0 and dist < 0) or (slope >= 0 and dist >= 0):
                # self.CalibrationLog.append("slope and dist share sign")
                bottom = coords[0]
                right = coords[2]
            else:

                bottom = coords[2]
                right = coords[0]
        if list is not None and len(list) > 0:
            guidelength = np.sqrt(np.power((center[0] - right[0]), 2) + np.power((center[1] - right[1]), 2))
            pixelinch = guidelength / self.CORNER_TO_CORNER
            rad = (pixelinch * self.CORNER_TO_TARG)
            vx = center[0] - right[0]
            vy = center[1] - right[1]
        else:
            guidelength = np.sqrt(np.power((center[0] - bottom[0]), 2) + np.power((center[1] - bottom[1]), 2))
            pixelinch = guidelength / self.SQ_TO_SQ
            rad = (pixelinch * self.SQ_TO_TARG)
            vx = center[0] - bottom[0]
            vy = center[1] - bottom[1]

        newlen = np.sqrt(vx * vx + vy * vy)

        if list is not None and len(list) > 0:
            targ1x = (rad * (vx / newlen)) + coords[0][0]
            targ1y = (rad * (vy / newlen)) + coords[0][1]
            targ2x = (rad * (vx / newlen)) + coords[1][0]
            targ2y = (rad * (vy / newlen)) + coords[1][1]
            targ3x = (rad * (vx / newlen)) + coords[2][0]
            targ3y = (rad * (vy / newlen)) + coords[2][1]
            targ4x = (rad * (vx / newlen)) + coords[3][0]
            targ4y = (rad * (vy / newlen)) + coords[3][1]

            target1 = (int(targ1x), int(targ1y))
            target2 = (int(targ2x), int(targ2y))
            target3 = (int(targ3x), int(targ3y))
            target4 = (int(targ4x), int(targ4y))
        else:
            targ1x = (rad * (vx / newlen)) + center[0]
            targ1y = (rad * (vy / newlen)) + center[1]
            targ3x = (rad * (vx / newlen)) + right[0]
            targ3y = (rad * (vy / newlen)) + right[1]

            target1 = (int(targ1x), int(targ1y))
            target3 = (int(targ3x), int(targ3y))
            target2 = (int((np.abs(target1[0] + target3[0])) / 2), int(np.abs((target1[1] + target3[1])) / 2))

        im2 = cv2.imread(image, -1)
        if self.CalibrationCameraModel.currentIndex() > 2 or ((self.CalibrationCameraModel.currentIndex() <= 2) and (self.CalibrationFilter.currentIndex() > 10)):
            blue = im2[:, :, 0]
            green = im2[:, :, 1]
            red = im2[:, :, 2] - ((im2[:, :, 0] / 5) * 4)

            red = np.floor(red)
            if "TIF" in image.split('.')[1].upper():
                red = red.astype("uint16")
                blue = blue.astype("uint16")
                green = green.astype("uint16")
            else:
                red = red.astype("uint8")
                blue = blue.astype("uint8")
                green = green.astype("uint8")
            im2 = cv2.merge((blue, green, red))
            try:
                targ1values = im2[(target1[1] - int((pixelinch * 0.75) / 2)):(target1[1] + int((pixelinch * 0.75) / 2)),
                              (target1[0] - int((pixelinch * 0.75) / 2)):(target1[0] + int((pixelinch * 0.75) / 2))]
                targ2values = im2[(target2[1] - int((pixelinch * 0.75) / 2)):(target2[1] + int((pixelinch * 0.75) / 2)),
                              (target2[0] - int((pixelinch * 0.75) / 2)):(target2[0] + int((pixelinch * 0.75) / 2))]
                targ3values = im2[(target3[1] - int((pixelinch * 0.75) / 2)):(target3[1] + int((pixelinch * 0.75) / 2)),
                              (target3[0] - int((pixelinch * 0.75) / 2)):(target3[0] + int((pixelinch * 0.75) / 2))]
            except Exception as e:
                print(e)
            t1redmean = np.mean(targ1values[:, :, 2]) / 100
            t1greenmean = np.mean(targ1values[:, :, 1]) / 100
            t1bluemean = np.mean(targ1values[:, :, 0]) / 100
            t2redmean = np.mean(targ2values[:, :, 2]) / 100
            t2greenmean = np.mean(targ2values[:, :, 1]) / 100
            t2bluemean = np.mean(targ2values[:, :, 0]) / 100
            t3redmean = np.mean(targ3values[:, :, 2]) / 100
            t3greenmean = np.mean(targ3values[:, :, 1]) / 100
            t3bluemean = np.mean(targ3values[:, :, 0]) / 100
            if list is not None and len(list) > 0:
                targ4values = im2[(target4[1] - int((pixelinch * 0.75) / 2)):(target4[1] + int((pixelinch * 0.75) / 2)),
                              (target4[0] - int((pixelinch * 0.75) / 2)):(target4[0] + int((pixelinch * 0.75) / 2))]
                t4redmean = np.mean(targ4values[:, :, 2]) / 100
                t4greenmean = np.mean(targ4values[:, :, 1]) / 100
                t4bluemean = np.mean(targ4values[:, :, 0]) / 100
                yred = [0.87, 0.51, 0.23, 0.0]
                yblue = [0.87, 0.51, 0.23, 0.0]
                ygreen = [0.87, 0.51, 0.23, 0.0]
                xred = [t1redmean, t2redmean, t3redmean, t4redmean]
                xgreen = [t1greenmean, t2greenmean, t3greenmean, t4greenmean]
                xblue = [t1bluemean, t2bluemean, t3bluemean, t4bluemean]

            else:
                yred = [0.87, 0.51, 0.23]
                yblue = [0.87, 0.51, 0.23]
                ygreen = [0.87, 0.51, 0.23]


                if self.CalibrationFilter.currentIndex() == 1 and (self.CalibrationCameraModel.currentIndex() == 3 or self.CalibrationCameraModel.currentIndex() == 4):
                    yred = self.refvalues["850"][0]
                    ygreen = self.refvalues["850"][1]
                    yblue = self.refvalues["850"][2]
                elif self.CalibrationFilter.currentIndex() == 2 and (self.CalibrationCameraModel.currentIndex() == 3 or self.CalibrationCameraModel.currentIndex() == 4):
                    yred = self.refvalues["650"][0]
                    ygreen = self.refvalues["650"][1]
                    yblue = self.refvalues["650"][2]
                elif self.CalibrationFilter.currentIndex() == 3 and (self.CalibrationCameraModel.currentIndex() == 3 or self.CalibrationCameraModel.currentIndex() == 4):
                    yred = self.refvalues["550"][0]
                    ygreen = self.refvalues["550"][1]
                    yblue = self.refvalues["550"][2]
                elif self.CalibrationFilter.currentIndex() == 4 and (self.CalibrationCameraModel.currentIndex() == 3 or self.CalibrationCameraModel.currentIndex() == 4):
                    yred = self.refvalues["450"][0]
                    ygreen = self.refvalues["450"][1]
                    yblue = self.refvalues["450"][2]
                elif (self.CalibrationCameraModel.currentIndex() <= 2) and (self.CalibrationFilter.currentIndex() > 10) or self.CalibrationCameraModel.currentIndex() == 7:
                    yred = self.refvalues["550/660/850"][0]
                    ygreen = self.refvalues["550/660/850"][1]
                    yblue = self.refvalues["550/660/850"][2]
                else:
                    yred = self.refvalues["660/850"][0]
                    ygreen = self.refvalues["660/850"][1]
                    yblue = self.refvalues["660/850"][2]

                xred = [t1redmean, t2redmean, t3redmean]
                xgreen = [t1greenmean, t2greenmean, t3greenmean]
                xblue = [t1bluemean, t2bluemean, t3bluemean]

            redslope, redintcpt, r_value, p_value, std_err = stats.linregress(xred, yred)

            greenslope, greenintcpt, r_value, p_value, std_err = stats.linregress(xgreen, ygreen)

            blueslope, blueintcpt, r_value, p_value, std_err = stats.linregress(xblue, yblue)

            # self.CalibrationLog.append("Red Slope: " + str(redslope))
            # self.CalibrationLog.append("Red Intcpt: " + str(redintcpt))
            # self.CalibrationLog.append("Green Slope: " + str(greenslope))
            # self.CalibrationLog.append("Green Intcpt: " + str(greenintcpt))
            # self.CalibrationLog.append("Blue Slope: " + str(blueslope))
            # self.CalibrationLog.append("Blue Intcpt: " + str(blueintcpt))
            self.CalibrationLog.append("Found QR Target, please proceed with calibration.")

            return [redintcpt, redslope, greenintcpt, greenslope, blueintcpt, blueslope]
        else:
            if list is not None and len(list) > 0:
                targ1values = im2[(target1[1] - int((pixelinch * 0.75) / 2)):(target1[1] + int((pixelinch * 0.75) / 2)),
                              (target1[0] - int((pixelinch * 0.75) / 2)):(target1[0] + int((pixelinch * 0.75) / 2))]
                targ2values = im2[(target2[1] - int((pixelinch * 0.75) / 2)):(target2[1] + int((pixelinch * 0.75) / 2)),
                              (target2[0] - int((pixelinch * 0.75) / 2)):(target2[0] + int((pixelinch * 0.75) / 2))]
                targ3values = im2[(target3[1] - int((pixelinch * 0.75) / 2)):(target3[1] + int((pixelinch * 0.75) / 2)),
                              (target3[0] - int((pixelinch * 0.75) / 2)):(target3[0] + int((pixelinch * 0.75) / 2))]
                targ4values = im2[(target4[1] - int((pixelinch * 0.75) / 2)):(target4[1] + int((pixelinch * 0.75) / 2)),
                              (target4[0] - int((pixelinch * 0.75) / 2)):(target4[0] + int((pixelinch * 0.75) / 2))]
                if len(im2.shape) > 2:
                    t1mean = np.mean(targ1values[:,:,0]) / 100
                    t2mean = np.mean(targ2values[:,:,0]) / 100
                    t3mean = np.mean(targ3values[:,:,0]) / 100
                    t4mean = np.mean(targ4values[:,:,0]) / 100
                else:
                    t1mean = np.mean(targ1values) / 100
                    t2mean = np.mean(targ2values) / 100
                    t3mean = np.mean(targ3values) / 100
                    t4mean = np.mean(targ4values) / 100
                y = [0.87, 0.51, 0.23, 0.0]
                if self.CalibrationFilter.currentIndex() == 0:
                    y = self.refvalues["Mono405"]

                elif self.CalibrationFilter.currentIndex() == 1:
                    y = self.refvalues["Mono450"]


                elif self.CalibrationFilter.currentIndex() == 2:
                    y = self.refvalues["Mono518"]


                elif self.CalibrationFilter.currentIndex() == 3:
                    y = self.refvalues["Mono550"]


                elif self.CalibrationFilter.currentIndex() == 4:
                    y = self.refvalues["Mono590"]
                elif self.CalibrationFilter.currentIndex() == 5:
                    y = self.refvalues["Mono632"]
                elif self.CalibrationFilter.currentIndex() == 6:
                    y = self.refvalues["Mono650"]
                elif self.CalibrationFilter.currentIndex() == 7:
                    y = self.refvalues["Mono615"]
                elif self.CalibrationFilter.currentIndex() == 8:
                    y = self.refvalues["Mono725"]
                elif self.CalibrationFilter.currentIndex() == 9:
                    y = self.refvalues["Mono808"]
                elif self.CalibrationFilter.currentIndex() == 10:
                    y = self.refvalues["Mono850"]

                x = [t1mean, t2mean, t3mean, t4mean]
            else:
                targ1values = im2[int(target1[1] - ((pixelinch * 0.75) / 2)):(target1[1] + ((pixelinch * 0.75) / 2)),
                              int(target1[0] - ((pixelinch * 0.75) / 2)):(target1[0] + ((pixelinch * 0.75) / 2))]
                targ2values = im2[int(target2[1] - ((pixelinch * 0.75) / 2)):(target2[1] + ((pixelinch * 0.75) / 2)),
                              int(target2[0] - ((pixelinch * 0.75) / 2)):(target2[0] + ((pixelinch * 0.75) / 2))]
                targ3values = im2[int(target3[1] - ((pixelinch * 0.75) / 2)):(target3[1] + ((pixelinch * 0.75) / 2)),
                              int(target3[0] - ((pixelinch * 0.75) / 2)):(target3[0] + ((pixelinch * 0.75) / 2))]
                if len(im2.shape) > 2:
                    t1mean = np.mean(targ1values[:,:,0]) / 100
                    t2mean = np.mean(targ2values[:,:,0]) / 100
                    t3mean = np.mean(targ3values[:,:,0]) / 100
                else:
                    t1mean = np.mean(targ1values) / 100
                    t2mean = np.mean(targ2values) / 100
                    t3mean = np.mean(targ3values) / 100
                y = [0.87, 0.51, 0.23]
                if self.CalibrationFilter.currentIndex() == 0:
                    y = self.refvalues["Mono405"]

                elif self.CalibrationFilter.currentIndex() == 1:
                    y = self.refvalues["Mono450"]


                elif self.CalibrationFilter.currentIndex() == 2:
                    y = self.refvalues["Mono518"]


                elif self.CalibrationFilter.currentIndex() == 3:
                    y = self.refvalues["Mono550"]


                elif self.CalibrationFilter.currentIndex() == 4:
                    y = self.refvalues["Mono590"]
                elif self.CalibrationFilter.currentIndex() == 5:
                    y = self.refvalues["Mono632"]
                elif self.CalibrationFilter.currentIndex() == 6:
                    y = self.refvalues["Mono650"]
                elif self.CalibrationFilter.currentIndex() == 7:
                    y = self.refvalues["Mono615"]
                elif self.CalibrationFilter.currentIndex() == 8:
                    y = self.refvalues["Mono725"]
                elif self.CalibrationFilter.currentIndex() == 9:
                    y = self.refvalues["Mono808"]
                elif self.CalibrationFilter.currentIndex() == 10:
                    y = self.refvalues["Mono850"]




                x = [t1mean, t2mean, t3mean]
            slope, intcpt, r_value, p_value, std_err = stats.linregress(x, y)
            self.CalibrationLog.append("Found QR Target, please proceed with calibration.")

            return [intcpt, slope]
    # Calibration Steps: End


    # Helper functions
    def preProcessHelper(self, infolder, outfolder, customerdata=True):

        if 5 <= self.PreProcessCameraModel.currentIndex() <= 10:
            os.chdir(infolder)
            infiles = []
            infiles.extend(glob.glob("." + os.sep + "*.DNG"))
            infiles.sort()
            counter = 0
            for input in infiles:
                self.PreProcessLog.append(
                    "processing image: " + str((counter) + 1) + " of " + str(len(infiles)) +
                    " " + input.split(os.sep)[1])
                QtWidgets.QApplication.processEvents()
                self.openDNG(infolder + input.split('.')[1] + "." + input.split('.')[2], outfolder, customerdata)

                counter += 1
        elif 0 <= self.PreProcessCameraModel.currentIndex() <= 2:
            os.chdir(infolder)
            infiles = []
            infiles.extend(glob.glob("." + os.sep + "*.[mM][aA][pP][iI][rR]"))
            infiles.extend(glob.glob("." + os.sep + "*.[tT][iI][fF]"))
            infiles.extend(glob.glob("." + os.sep + "*.[tT][iI][fF][fF]"))
            counter = 0
            for input in infiles:
                self.PreProcessLog.append(
                    "processing image: " + str((counter) + 1) + " of " + str(len(infiles)) +
                    " " + input.split(os.sep)[1])
                QtWidgets.QApplication.processEvents()
                filename = input.split('.')
                outputfilename = filename[1] + '.tiff'
                print(infolder + input.split('.')[1] + "." + input.split('.')[2])
                print(outfolder + outputfilename)
                self.openMapir(infolder + input.split('.')[1] + "." + input.split('.')[2], outfolder + outputfilename)


                counter += 1
        else:
            os.chdir(infolder)
            infiles = []
            infiles.extend(glob.glob("." + os.sep + "*.[rR][aA][wW]"))
            infiles.extend(glob.glob("." + os.sep + "*.[jJ][pP][gG]"))
            infiles.extend(glob.glob("." + os.sep + "*.[jJ][pP][eE][gG]"))
            infiles.sort()
            if len(infiles) > 1:
                if ("RAW" in infiles[0].upper()) and ("JPG" in infiles[1].upper()):
                    counter = 0
                    for input in infiles[::2]:
                        if customerdata == True:
                            self.PreProcessLog.append(
                                "processing image: " + str((counter / 2) + 1) + " of " + str(len(infiles) / 2) +
                                " " + input.split(os.sep)[1])
                            QtWidgets.QApplication.processEvents()
                        with open(input, "rb") as rawimage:
                            img = np.fromfile(rawimage, np.dtype('u2'), self.imsize).reshape((self.imrows, self.imcols))
                            color = cv2.cvtColor(img, cv2.COLOR_BAYER_RG2RGB)

                            filename = input.split('.')
                            outputfilename = filename[1] + '.tiff'
                            cv2.imencode(".tiff", color)
                            cv2.imwrite(outfolder + outputfilename, color)
                            if customerdata == True:
                                self.copyExif(infolder + infiles[counter + 1], outfolder + outputfilename)
                        counter += 2

                else:
                    self.PreProcessLog.append(
                        "Incorrect file structure. Please arrange files in a RAW, JPG, RAW, JGP... format.")


    def traverseHierarchy(self, tier, cont, index, image, depth, coords):

        if tier[0][index][2] != -1:
            self.traverseHierarchy(tier, cont, tier[0][index][2], image, depth + 1, coords)
            return
        elif depth >= 2:
            c = cont[index]
            moment = cv2.moments(c)
            if int(moment['m00']) != 0:
                x = int(moment['m10'] / moment['m00'])
                y = int(moment['m01'] / moment['m00'])
                coords.append([x, y])
            return

    def openDNG(self, inphoto, outfolder, customerdata=True):
        inphoto = str(inphoto)
        newfile = inphoto.split(".")[0] + ".tiff"
        if not os.path.exists(outfolder + os.sep + newfile.rsplit(os.sep, 1)[1]):
            if sys.platform == "win32":
                subprocess.call([modpath + os.sep + 'dcraw.exe', '-6', '-T', inphoto], startupinfo=si)
            else:
                subprocess.call([r'/usr/local/bin/dcraw', '-6', '-T', inphoto])
            if customerdata == True:
                self.copyExif(os.path.abspath(inphoto), newfile)
            shutil.move(newfile, outfolder)
        else:
            self.PreProcessLog.append("Attention!: " + str(newfile) + " already exists.")

    def openMapir(self, inphoto, outphoto):
        if "tif" in inphoto.split('.')[1]:
            img = cv2.imread(inphoto, -1)

            color = cv2.cvtColor(img, cv2.COLOR_BAYER_GR2RGB)

            cv2.imencode(".tiff", color)
            cv2.imwrite(outphoto, color)
            self.copyExif(inphoto, outphoto)
        else:
            if self.PreProcessCameraModel.currentIndex() == 0:
                if self.PreProcessDarkBox.isChecked():
                    subprocess.call(
                        [modpath + os.sep + r'Mapir_Converter_dark.exe', os.path.abspath(inphoto),
                         os.path.abspath(outphoto)])
                else:
                    subprocess.call(
                        [modpath + os.sep + r'Mapir_Converter.exe', os.path.abspath(inphoto),
                         os.path.abspath(outphoto)])
            else:
                subprocess.call(
                    [modpath + os.sep + r'Mapir_Converter.exe', os.path.abspath(inphoto),
                     os.path.abspath(outphoto)])
    def copyExif(self, inphoto, outphoto):
        if sys.platform == "win32":
            # with exiftool.ExifTool() as et:
            #     et.execute(r' -overwrite_original -tagsFromFile ' + os.path.abspath(inphoto) + ' ' + os.path.abspath(outphoto))

            subprocess.call(
                [modpath + os.sep + r'exiftool.exe', r'-overwrite_original', r'-tagsFromFile',
                 os.path.abspath(inphoto),
                 r'-all:all<all:all',
                 os.path.abspath(outphoto)], startupinfo=si)
        else:
            subprocess.call(
                [r'exiftool', r'-overwrite_original', r'-addTagsFromFile', os.path.abspath(inphoto),
                 r'-all:all<all:all',
                 os.path.abspath(outphoto)])
    def on_DarkCurrentInputButton_released(self):
        with open(modpath + os.sep + "instring.txt", "r+") as instring:
            self.DarkCurrentInput.setText(QtWidgets.QFileDialog.getExistingDirectory(directory=instring.read()))
            instring.truncate(0)
            instring.seek(0)
            instring.write(self.DarkCurrentInput.text())
    def on_DarkCurrentOutputButton_released(self):
        with open(modpath + os.sep + "instring.txt", "r+") as instring:
            self.DarkCurrentOutput.setText(QtWidgets.QFileDialog.getExistingDirectory(directory=instring.read()))
            instring.truncate(0)
            instring.seek(0)
            instring.write(self.DarkCurrentOutput.text())
    def on_DarkCurrentGoButton_released(self):
        folder1 = []
        folder1.extend(glob.glob(self.DarkCurrentInput.text() + os.sep + "*.tif?"))
        for img in folder1:
            QtWidgets.QApplication.processEvents()
            self.KernelLog.append("Updating " + str(img))
            subprocess.call(
                [modpath + os.sep + r'exiftool.exe', r'-overwrite_original', r'-ifd0:blacklevelrepeatdim=2 2',  img], startupinfo=si)

        self.KernelLog.append("Finished updating")

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

