import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QGroupBox, QTextEdit
from PyQt5.QtGui import QFont, QPainter, QPen
from PyQt5.QtCore import Qt, QSize, QTimer
import random
import serial

port = "COM3"
baud = 9600
updateFreq = 1000
mission_Time, packet_Count, Mode, State, Altitude, air_Speed, hs_Deployed, pc_Deployed, Temperature, Pressure, Voltage, GPS_Time, GPS_Altitude, GPS_Longitude, GPS_stats, Tilt_X, Tilt_Y, Rot_Z, CMD_Echo = "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""

class GraphWidget(QWidget):
    def __init__(self, label, parent=None):
        super(GraphWidget, self).__init__(parent)
        self.label = label
        self.data = [random.randint(0, 100) for _ in range(50)]

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        self.titleLabel = QLabel(self.label)
        layout.addWidget(self.titleLabel, alignment=Qt.AlignCenter)

    def paintEvent(self, event):
        qp = QPainter(self)
        self.drawGraph(qp)

    def drawGraph(self, qp):
        pen = QPen(Qt.black)
        pen.setWidth(2)
        qp.setPen(pen)

        graph_width = self.width() - 20
        graph_height = self.height() - 20
        qp.drawLine(10, graph_height + 10, graph_width + 10, graph_height + 10)
        qp.drawLine(10, 10, 10, graph_height + 10)

        step_x = graph_width / (len(self.data) - 1)
        x_tick_interval = max(1, len(self.data) // 10)
        for i in range(0, len(self.data), x_tick_interval):
            x = int(i * step_x) + 10
            qp.drawLine(x, graph_height + 10, x, graph_height + 15)
            qp.drawText(x - 10, graph_height + 25, str(i))

        max_data = max(self.data) if self.data else 1
        y_tick_interval = max(1, max_data // 10)
        step_y = graph_height / max_data
        for i in range(0, max_data + 1, y_tick_interval):
            y = int(graph_height - i * step_y) + 10
            qp.drawLine(5, y, 10, y)
            qp.drawText(0, y + 5, str(i))

        for i in range(1, len(self.data)):
            x1 = int((i - 1) * step_x) + 10
            y1 = int(graph_height - (self.data[i - 1] * step_y)) + 10
            x2 = int(i * step_x) + 10
            y2 = int(graph_height - (self.data[i] * step_y)) + 10
            qp.drawLine(x1, y1, x2, y2)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # Left side graphs
        graph_layout = QVBoxLayout()

        graphs = ["Altitude", "GPS Data", "Temperature", "Velocity", "Tilt"]
        for graph_label in graphs:
            graph_widget = GraphWidget("")
            graph_box = QGroupBox(graph_label)
            graph_box_layout = QVBoxLayout()
            graph_box_layout.addWidget(graph_widget)
            graph_box.setLayout(graph_box_layout)
            graph_layout.addWidget(graph_box)

        main_layout.addLayout(graph_layout)

        # Right side widgets
        right_layout = QVBoxLayout()

        # Simulation mode box
        simulation_box = QGroupBox("Simulation Mode")
        simulation_layout = QVBoxLayout()

        sim_enable_button = QPushButton("Sim Enable")
        sim_enable_button.setFont(QFont("Arial", 14))
        sim_enable_button.clicked.connect(self.enableSimStart)  # Connect clicked signal to enableSimStart method
        simulation_layout.addWidget(sim_enable_button)

        sim_disable_button = QPushButton("Sim Disable", objectName = "Sim Disable")
        sim_disable_button.setFont(QFont("Arial", 14))
        sim_disable_button.clicked.connect(self.disableSimStart)
        simulation_layout.addWidget(sim_disable_button)

        sim_start_button = QPushButton("Sim Start", objectName="Sim Start")
        sim_start_button.setFont(QFont("Arial", 14))
        sim_start_button.setEnabled(False)  # Initially disabled
        sim_start_button.clicked.connect(self.sendXbeeData)
        simulation_layout.addWidget(sim_start_button)

        sim_stop_button = QPushButton("Sim Stop")
        sim_stop_button.setFont(QFont("Arial", 14))
        simulation_layout.addWidget(sim_stop_button)
        
        retry_button = QPushButton("Retry Xbee Connection")
        retry_button.setFont(QFont("Arial", 14))
        retry_button.clicked.connect(self.retryXbeeConnection)
        right_layout.addWidget(retry_button)

        simulation_box.setLayout(simulation_layout)
        right_layout.addWidget(simulation_box)

        # Labels box
        labels_box = QGroupBox("Labels")
        labels_layout = QVBoxLayout()

        labels = ["UTC", "Flight State", "Sim State", "Packet count"]
        for label in labels:
            label_widget = QLabel(label)
            label_widget.setFont(QFont("Arial", 14))
            labels_layout.addWidget(label_widget)

        labels_box.setLayout(labels_layout)
        right_layout.addWidget(labels_box)

        main_layout.addLayout(right_layout)
        
        # Set stretch factor for right_layout
        right_layout.addStretch(1)
       
        data_display_box = QGroupBox("XBee Data")
        data_display_layout = QVBoxLayout()

        self.data_display_text = QTextEdit()
        self.data_display_text.setReadOnly(True)
        data_display_layout.addWidget(self.data_display_text)

        data_display_box.setLayout(data_display_layout)
        right_layout.addWidget(data_display_box)
          # Flight States box
        flight_states_box = QGroupBox("Flight States")
        flight_states_layout = QVBoxLayout()

        flight_state_buttons = ["Launch Wait", "Ascent", "Rocket Separation", "Deploy HS", "Descent", "HS Separation"]
        for state in flight_state_buttons:
            button = QPushButton(state)
            button.setFont(QFont("Arial", 14))
            flight_states_layout.addWidget(button)

        flight_states_box.setLayout(flight_states_layout)
        right_layout.addWidget(flight_states_box)
        


        # Misc Commands box
        misc_commands_box = QGroupBox("Misc Commands")
        misc_commands_layout = QVBoxLayout()

        misc_commands_buttons = ["Calibrate", "Beacon"]
        for command in misc_commands_buttons:
            button = QPushButton(command)
            button.setFont(QFont("Arial", 14))
            misc_commands_layout.addWidget(button)
        
   
        misc_commands_box.setLayout(misc_commands_layout)
        right_layout.addWidget(misc_commands_box)
        main_layout.addLayout(right_layout)
        
       
        
        self.timer = QTimer(self)
        #self.timer.timeout.connect(self.checkXbeeData)
        self.timer.start(1000) 
        self.timer.timeout.connect(self.updateDataDisplay) 
        self.serial_port = None
        self.file_data = []

    def enableSimStart(self):

        self.findChild(QPushButton, "Sim Start").setEnabled(True)
    
    def disableSimStart(self):

        self.findChild(QPushButton, "Sim Start").setEnabled(False)

    def checkXbeeData(self):
        if self.serial_port is None or not self.serial_port.is_open:
            try:
                self.serial_port = serial.Serial(port, baud)
                print("XBee connection established.")
            except serial.SerialException as e:
                print("Failed to establish XBee connection:", e)
                return

        data = self.serial_port.readline().decode().strip()
        rawDataList = data.split(',')
        mission_Time, packet_Count, Mode, State, Altitude, air_Speed, hs_Deployed, pc_Deployed, Temperature, Pressure, Voltage, GPS_Time, GPS_Altitude, GPS_Longitude, GPS_stats, Tilt_X, Tilt_Y, Rot_Z, CMD_Echo = rawDataList[2], rawDataList[3], rawDataList[4], rawDataList[5], rawDataList[6], rawDataList[7], rawDataList[8], rawDataList[9], rawDataList[10], rawDataList[11], rawDataList[12], rawDataList[13], rawDataList[14], rawDataList[15], rawDataList[16], rawDataList[17], rawDataList[18], rawDataList[19], rawDataList[20], rawDataList[21]
        with open(r"C:\Users\ollie\OneDrive\Desktop\CanSat GroundStation\2024-CanSat-GroundStation\received_data.txt", "a") as file:
            file.write(data + "\n")
        # print(rawDataList)

    def updateDataDisplay(self):
        # Read data from XBee and update display
        RawDisplay = {
            "Team Designation" : "2079",
            "Mission Time" : mission_Time,
            "Packet Count" : packet_Count,
            "Mode" : Mode,
            "State" : State,
            "Altitude" : Altitude,
            "Air Speed" : air_Speed,
            "Heat Shield Deployed?" : hs_Deployed,
            "PC Deployed?" : pc_Deployed,
            "Temperature" : Temperature,
            "Pressure" : Pressure,
            "Voltage" : Voltage,
            "GPS Time" : GPS_Time,
            "GPS Altitude" : GPS_Altitude,
            "GPS Longitude" : GPS_Longitude,
            "Tilt X" : Tilt_X,
            "Tilt Y" : Tilt_Y,
            "Rot Z" : Rot_Z,
            "Command Echo": CMD_Echo,
            "Satellites connected" : GPS_stats
        }

        # Update text in data display box
        self.data_display_text.clear()
        self.data_display_text.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        for key, value in RawDisplay.items():
            self.data_display_text.append(f"{key}: {value}")

    def sendXbeeData(self):
        filename = r"C:\Users\ollie\OneDrive\Desktop\CanSat GroundStation\2024-CanSat-GroundStation\cansat_2023_simp.txt"
        with open(filename, "r") as file:
            self.file_data = file.readlines()

        self.timer_single_shot = QTimer(self)
        self.timer_single_shot.timeout.connect(self.sendDataLine)
        self.timer_single_shot.start(1000)

    def sendDataLine(self):
        if self.file_data:
            line = self.file_data.pop(0).strip()
            if line.startswith("CMD"):
                command = line.split(",")[-1]
                if self.serial_port is not None:
                    self.serial_port.write(command.encode() + b"\n")
                    print("Sent:", command)
            else:
                print("Invalid line format. Skipping:", line)
        else:
            self.timer_single_shot.stop()
            print("Simulation complete.")

    def retryXbeeConnection(self):
        if self.serial_port is not None:
            try:
                self.serial_port.close()
                print("XBee connection closed.")
            except serial.SerialException as e:
                print("Failed to close XBee connection:", e)

            self.serial_port = None
        self.checkXbeeData()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())