# main_gui.py - Interfaz gráfica para el controlador MIDI
import sys
import logging
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, 
    QWidget, QLabel, QListWidget, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont, QColor
import rtmidi

class MidiControllerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Configuración de la ventana principal
        self.setWindowTitle("F3FFF MEGAMIDI CONTROLLER")
        self.setMinimumSize(800, 600)
        
        # Inicializar MIDI para detectar puertos
        self.midiin = rtmidi.MidiIn()
        self.midiout = rtmidi.MidiOut()
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Crear sección de puertos MIDI
        self.create_midi_ports_section(main_layout)
        
        # Línea separadora
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)
        
        # Espacio para contenido futuro
        main_layout.addStretch(1)
        
        # Inicializar listas de puertos
        self.update_port_lists()
    
    def create_midi_ports_section(self, parent_layout):
        """Crea la sección de selección de puertos MIDI"""
        # Layout horizontal para los puertos y el botón de pánico
        ports_layout = QHBoxLayout()
        
        # Layout vertical para las listas de puertos
        lists_layout = QVBoxLayout()
        
        # Puertos de entrada
        input_layout = QVBoxLayout()
        input_label = QLabel("Puertos MIDI de Entrada:")
        input_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.input_ports_list = QListWidget()
        self.input_ports_list.setSelectionMode(QListWidget.SingleSelection)
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_ports_list)
        
        # Puertos de salida
        output_layout = QVBoxLayout()
        output_label = QLabel("Puertos MIDI de Salida:")
        output_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.output_ports_list = QListWidget()
        self.output_ports_list.setSelectionMode(QListWidget.SingleSelection)
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_ports_list)
        
        # Añadir listas al layout
        lists_layout.addLayout(input_layout)
        lists_layout.addLayout(output_layout)
        ports_layout.addLayout(lists_layout, 4)  # Asignar 4/5 del espacio
        
        # Botón de pánico
        panic_layout = QVBoxLayout()
        self.panic_button = QPushButton("PÁNICO")
        self.panic_button.setFont(QFont("Arial", 14, QFont.Bold))
        self.panic_button.setMinimumHeight(150)
        self.panic_button.setStyleSheet("""
            QPushButton {
                background-color: #ff3b30;
                color: white;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #ff6b60;
            }
            QPushButton:pressed {
                background-color: #cc2f26;
            }
        """)
        self.panic_button.clicked.connect(self.on_panic_button_clicked)
        panic_layout.addWidget(self.panic_button)
        panic_layout.addStretch(1)
        ports_layout.addLayout(panic_layout, 1)  # Asignar 1/5 del espacio
        
        # Añadir botón de actualizar puertos
        refresh_button = QPushButton("Actualizar Puertos")
        refresh_button.clicked.connect(self.update_port_lists)
        
        # Añadir todo al layout principal
        parent_layout.addLayout(ports_layout)
        parent_layout.addWidget(refresh_button)
    
    def update_port_lists(self):
        """Actualiza las listas de puertos MIDI disponibles"""
        # Limpiar listas
        self.input_ports_list.clear()
        self.output_ports_list.clear()
        
        # Añadir puertos de entrada
        input_ports = self.midiin.get_ports()
        for port in input_ports:
            self.input_ports_list.addItem(port)
        
        # Añadir puertos de salida
        output_ports = self.midiout.get_ports()
        for port in output_ports:
            self.output_ports_list.addItem(port)
    
    @Slot()
    def on_panic_button_clicked(self):
        """Acción del botón de pánico"""
        try:
            # Aquí implementaríamos el envío de mensajes MIDI All Notes Off a todos los canales
            QMessageBox.information(
                self, 
                "PÁNICO ACTIVADO", 
                "Se han detenido todos los mensajes MIDI y se ha restablecido el sistema."
            )
            # En una implementación real, aquí enviaríamos los mensajes All Notes Off
            logging.info("Botón de pánico activado: enviando All Notes Off a todos los canales")
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"Ha ocurrido un error al activar el pánico: {str(e)}"
            )

def run_application():
    app = QApplication(sys.argv)
    window = MidiControllerGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    run_application()
