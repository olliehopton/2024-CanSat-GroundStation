from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QTimer
import sys

import serial
import time

sim = 0
#xbee = serial.Serial("/dev/ttyUSB0")
xbee = serial.Serial("COM4")
xbee.timeout = 1

f = open("packets.txt", "a")
f.write("")
f.write("")
f.close()

class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow,self).__init__()
        self.initUI()
        self.readTimer = QTimer()
        self.readTimer.setInterval(1000)
        self.readTimer.timeout.connect(self.read_packet)
        self.readTimer.start()
        
    def read_packet(self):
        p = ""
        p += xbee.read_until(b'!').decode()
        self.currentPacket.setText(p)
        f = open("packets.txt", "a")
        f.write(p)

    def sim_enable(self):
        xbee.write(b"CMD,2079,SIM,ENABLE")
    
    def sim_activate(self):
        xbee.write(b"CMD,2079,SIM,ACTIVATE")
        sim = 1
    
    def sim_disable(self):
        xbee.write(b"CMD,2079,SIM,DISABLE")
    
    def change_separate(self):
        xbee.write(b"CMD,2079,STATE,SEPARATE")
    
    def change_hs_release(self):
        xbee.write(b"CMD,2079,STATE,HS_RELEASE")
    
    def change_landed(self):
        xbee.write(b"CMD,2079,STATE,LANDED")

    def initUI(self):
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowTitle("Temporary GCS")

        self.currentPacket = QtWidgets.QLabel(self)
        self.currentPacket.setText("my first label!")
        self.currentPacket.move(0, 180)
        self.currentPacket.resize(1600, 50)

        self.sim_enable_btn = QtWidgets.QPushButton(self)
        self.sim_enable_btn.setText("Simulation enable")
        self.sim_enable_btn.clicked.connect(self.sim_enable)
        self.sim_enable_btn.setGeometry(0, 0, 160, 20)

        self.sim_activate_btn = QtWidgets.QPushButton(self)
        self.sim_activate_btn.setText("Simulation activate")
        self.sim_activate_btn.clicked.connect(self.sim_activate)
        self.sim_activate_btn.setGeometry(0, 30, 160, 20)

        self.sim_disable_btn = QtWidgets.QPushButton(self)
        self.sim_disable_btn.setText("Simulation disable")
        self.sim_disable_btn.clicked.connect(self.sim_disable)
        self.sim_disable_btn.setGeometry(0, 60, 160, 20)
        
        self.change_separate_btn = QtWidgets.QPushButton(self)
        self.change_separate_btn.setText("Separate")
        self.change_separate_btn.clicked.connect(self.change_separate)
        self.change_separate_btn.setGeometry(180, 0, 160, 20)
        
        self.change_hs_release_btn = QtWidgets.QPushButton(self)
        self.change_hs_release_btn.setText("Heat Shield Release")
        self.change_hs_release_btn.clicked.connect(self.change_hs_release)
        self.change_hs_release_btn.setGeometry(180, 30, 160, 20)
        
        self.change_landed_btn = QtWidgets.QPushButton(self)
        self.change_landed_btn.setText("Land")
        self.change_landed_btn.clicked.connect(self.change_landed)
        self.change_landed_btn.setGeometry(180, 60, 160, 20)

def window():
    app = QApplication(sys.argv)
    win = MyWindow()
    win.show()
    sys.exit(app.exec_())

window()

xbee.close()
