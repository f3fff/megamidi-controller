# midi_device.py - Clase base para todos los dispositivos MIDI
import rtmidi
import time
from typing import List, Dict, Optional, Tuple, Union, Any
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class MidiDevice:
    """
    Clase base para todos los dispositivos MIDI.
    Proporciona funcionalidad básica para enviar y recibir mensajes MIDI.
    """
    
    def __init__(self, device_name: str, port_in: Optional[int] = None, port_out: Optional[int] = None):
        """
        Inicializa un dispositivo MIDI.
        
        Args:
            device_name: Nombre identificativo del dispositivo
            port_in: Índice del puerto de entrada MIDI (None para selección interactiva)
            port_out: Índice del puerto de salida MIDI (None para selección interactiva)
        """
        self.device_name = device_name
        self.logger = logging.getLogger(f"MidiDevice.{device_name}")
        
        # Inicializar MIDI in/out
        self.midiin = rtmidi.MidiIn()
        self.midiout = rtmidi.MidiOut()
        
        # Obtener puertos disponibles
        self.in_ports = self.midiin.get_ports()
        self.out_ports = self.midiout.get_ports()
        
        if not self.out_ports:
            raise RuntimeError("No hay puertos MIDI de salida disponibles.")
        
        # Mostrar puertos disponibles
        self.logger.info("Puertos MIDI de salida disponibles:")
        for i, name in enumerate(self.out_ports):
            self.logger.info(f"{i}: {name}")
        
        if self.in_ports:
            self.logger.info("Puertos MIDI de entrada disponibles:")
            for i, name in enumerate(self.in_ports):
                self.logger.info(f"{i}: {name}")
        
        # Configurar puertos
        self.configure_ports(port_in, port_out)
    
    def configure_ports(self, port_in: Optional[int] = None, port_out: Optional[int] = None):
        """
        Configura los puertos MIDI de entrada y salida.
        
        Args:
            port_in: Índice del puerto de entrada
            port_out: Índice del puerto de salida
        """
        # Configurar puerto de salida
        if port_out is None:
            port_out = int(input('Seleccione el puerto de salida MIDI (número entero): '))
        
        if 0 <= port_out < len(self.out_ports):
            self.port_out = port_out
            self.midiout.open_port(self.port_out)
            self.logger.info(f"Puerto MIDI de salida abierto: {self.out_ports[self.port_out]}")
        else:
            raise ValueError(f"Puerto de salida inválido: {port_out}")
        
        # Configurar puerto de entrada si hay disponibles
        if self.in_ports:
            if port_in is None:
                port_in = int(input('Seleccione el puerto de entrada MIDI (número entero): '))
            
            if 0 <= port_in < len(self.in_ports):
                self.port_in = port_in
                self.midiin.open_port(self.port_in)
                self.logger.info(f"Puerto MIDI de entrada abierto: {self.in_ports[self.port_in]}")
            else:
                self.logger.warning(f"Puerto de entrada inválido: {port_in}")
                self.port_in = None
        else:
            self.logger.warning("No hay puertos MIDI de entrada disponibles.")
            self.port_in = None
    
    def send_message(self, message: List[int]):
        """
        Envía un mensaje MIDI.
        
        Args:
            message: Lista de enteros que representan el mensaje MIDI
        """
        try:
            self.midiout.send_message(message)
            self.logger.debug(f"Mensaje enviado: {message}")
        except Exception as e:
            self.logger.error(f"Error al enviar mensaje MIDI: {e}")
    
    def read_message(self) -> Optional[Tuple[List[int], float]]:
        """
        Lee un mensaje MIDI de entrada si está disponible.
        
        Returns:
            Tupla con el mensaje y el tiempo desde el último mensaje, o None si no hay mensaje
        """
        if self.port_in is None:
            return None
        
        msg_n_time = self.midiin.get_message()
        if msg_n_time:
            return msg_n_time
        return None
    
    def close(self):
        """Cierra los puertos MIDI abiertos."""
        self.midiout.close_port()
        if self.port_in is not None:
            self.midiin.close_port()
        self.logger.info("Puertos MIDI cerrados.")
    
    def __enter__(self):
        """Soporte para el uso con 'with'."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cierra automáticamente los puertos al salir del bloque 'with'."""
        self.close()
        
    # Métodos comunes para mensajes MIDI
    def note_on(self, note: int, velocity: int, channel: int = 0):
        """
        Envía un mensaje de Note On.
        
        Args:
            note: Número de nota MIDI (0-127)
            velocity: Velocidad (1-127)
            channel: Canal MIDI (0-15)
        """
        if not 0 <= note <= 127:
            raise ValueError(f"Nota fuera de rango (0-127): {note}")
        if not 1 <= velocity <= 127:
            raise ValueError(f"Velocidad fuera de rango (1-127): {velocity}")
        if not 0 <= channel <= 15:
            raise ValueError(f"Canal fuera de rango (0-15): {channel}")
            
        message = [0x90 + channel, note, velocity]
        self.send_message(message)
    
    def note_off(self, note: int, channel: int = 0):
        """
        Envía un mensaje de Note Off.
        
        Args:
            note: Número de nota MIDI (0-127)
            channel: Canal MIDI (0-15)
        """
        if not 0 <= note <= 127:
            raise ValueError(f"Nota fuera de rango (0-127): {note}")
        if not 0 <= channel <= 15:
            raise ValueError(f"Canal fuera de rango (0-15): {channel}")
            
        message = [0x90 + channel, note, 0]  # Note On con velocidad 0 = Note Off
        self.send_message(message)
    
    def program_change(self, program: int, channel: int = 0):
        """
        Envía un mensaje de Program Change.
        
        Args:
            program: Número de programa (0-127)
            channel: Canal MIDI (0-15)
        """
        if not 0 <= program <= 127:
            raise ValueError(f"Programa fuera de rango (0-127): {program}")
        if not 0 <= channel <= 15:
            raise ValueError(f"Canal fuera de rango (0-15): {channel}")
            
        message = [0xC0 + channel, program]
        self.send_message(message)
    
    def control_change(self, controller: int, value: int, channel: int = 0):
        """
        Envía un mensaje de Control Change.
        
        Args:
            controller: Número de controlador (0-127)
            value: Valor (0-127)
            channel: Canal MIDI (0-15)
        """
        if not 0 <= controller <= 127:
            raise ValueError(f"Controlador fuera de rango (0-127): {controller}")
        if not 0 <= value <= 127:
            raise ValueError(f"Valor fuera de rango (0-127): {value}")
        if not 0 <= channel <= 15:
            raise ValueError(f"Canal fuera de rango (0-15): {channel}")
            
        message = [0xB0 + channel, controller, value]
        self.send_message(message)