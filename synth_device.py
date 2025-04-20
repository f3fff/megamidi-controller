# synth_device.py - Clase para dispositivos de sintetizadores
from midi_device import MidiDevice
from typing import Dict, Any, Optional, List
import json
import logging
import time
import os

class SynthDevice(MidiDevice):
    """
    Clase para controlar un sintetizador basado en su configuración JSON.
    """
    
    def __init__(self, config: Dict[str, Any], port_in: Optional[int] = None, port_out: Optional[int] = None):
        """
        Inicializa un dispositivo de sintetizador usando una configuración.
        
        Args:
            config: Diccionario con la configuración del sintetizador
            port_in: Índice del puerto de entrada MIDI
            port_out: Índice del puerto de salida MIDI
        """
        device_name = f"{config.get('manufacturer', '')} {config.get('model', '')}"
        super().__init__(device_name.strip(), port_in, port_out)
        
        self.config = config
        self.default_channel = config.get('default_channel', 0)
        self.logger = logging.getLogger(f"SynthDevice.{device_name}")
    
    @classmethod
    def from_json_file(cls, json_file: str, port_in: Optional[int] = None, port_out: Optional[int] = None):
        """
        Crea una instancia desde un archivo JSON.
        
        Args:
            json_file: Ruta al archivo JSON de configuración
            port_in: Índice del puerto de entrada MIDI
            port_out: Índice del puerto de salida MIDI
            
        Returns:
            Instancia de SynthDevice
        """
        with open(json_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return cls(config, port_in, port_out)
    
    def get_patch_value(self, patch_name: str, patch_type: str = 'single') -> Optional[int]:
        """
        Obtiene el valor numérico de un patch por su nombre.
        
        Args:
            patch_name: Nombre del patch
            patch_type: Tipo de patch ('single', 'multi', etc.)
            
        Returns:
            Valor numérico del patch o None si no existe
        """
        try:
            # Buscar el patch en la configuración
            patches = self.config.get('patches', {}).get(patch_type, {})
            if patch_name in patches:
                # Convertir el valor hexadecimal a entero
                value = patches[patch_name]
                if isinstance(value, str) and value.startswith('0x'):
                    return int(value, 16)
                return int(value)
            return None
        except Exception as e:
            self.logger.error(f"Error al obtener valor de patch {patch_name}: {e}")
            return None
    
    def get_effect_value(self, effect_name: str) -> Optional[int]:
        """
        Obtiene el valor numérico de un efecto por su nombre.
        
        Args:
            effect_name: Nombre del efecto
            
        Returns:
            Valor numérico del efecto o None si no existe
        """
        try:
            effects = self.config.get('effects', {})
            if effect_name in effects:
                value = effects[effect_name].get('code')
                if isinstance(value, str) and value.startswith('0x'):
                    return int(value, 16)
                return int(value)
            return None
        except Exception as e:
            self.logger.error(f"Error al obtener valor de efecto {effect_name}: {e}")
            return None
    
    def get_controller_info(self, controller_name: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información de un controlador por su nombre.
        
        Args:
            controller_name: Nombre del controlador
            
        Returns:
            Diccionario con información del controlador o None si no existe
        """
        return self.config.get('controllers', {}).get(controller_name)
    
    def select_patch(self, patch_name: str, patch_type: str = 'single'):
        """
        Selecciona un patch por su nombre.
        
        Args:
            patch_name: Nombre del patch
            patch_type: Tipo de patch ('single', 'multi', etc.)
        """
        value = self.get_patch_value(patch_name, patch_type)
        if value is not None:
            self.logger.info(f"Seleccionando {patch_type} patch: {patch_name} ({hex(value)})")
            self.program_change(value, self.default_channel)
        else:
            self.logger.error(f"Patch no encontrado: {patch_name} ({patch_type})")
    
    def select_effect(self, effect_name: str):
        """
        Selecciona un efecto por su nombre.
        
        Args:
            effect_name: Nombre del efecto
        """
        value = self.get_effect_value(effect_name)
        if value is not None:
            self.logger.info(f"Seleccionando efecto: {effect_name} ({hex(value)})")
            self.program_change(value, self.default_channel)
        else:
            self.logger.error(f"Efecto no encontrado: {effect_name}")
    
    def set_controller(self, controller_name: str, value: int):
        """
        Establece el valor de un controlador.
        
        Args:
            controller_name: Nombre del controlador
            value: Valor a establecer
        """
        controller_info = self.get_controller_info(controller_name)
        if controller_info:
            cc_number = controller_info.get('cc_number')
            min_value = controller_info.get('min_value', 0)
            max_value = controller_info.get('max_value', 127)
            
            # Validar valor
            if value < min_value:
                value = min_value
            elif value > max_value:
                value = max_value
            
            self.logger.info(f"Estableciendo controlador {controller_name} ({cc_number}): {value}")
            self.control_change(cc_number, value, self.default_channel)
        else:
            self.logger.error(f"Controlador no encontrado: {controller_name}")
    
    def test_patches(self, patch_type: str = 'single', note: int = 60, duration: float = 1.0):
        """
        Prueba todos los patches de un tipo determinado.
        
        Args:
            patch_type: Tipo de patch ('single', 'multi', etc.)
            note: Número de nota MIDI a tocar
            duration: Duración de cada nota en segundos
        """
        patches = self.config.get('patches', {}).get(patch_type, {})
        self.logger.info(f"Probando {len(patches)} patches de tipo {patch_type}...")
        
        try:
            for patch_name in patches:
                self.select_patch(patch_name, patch_type)
                time.sleep(0.5)  # Esperar a que el patch se cargue
                
                self.logger.info(f"Tocando nota en {patch_name}")
                self.note_on(note, 100, self.default_channel)
                time.sleep(duration)
                self.note_off(note, self.default_channel)
                time.sleep(0.5)
                
            self.logger.info(f"Prueba de patches {patch_type} completada.")
        except Exception as e:
            self.logger.error(f"Error durante la prueba: {e}")
    
    def get_available_patches(self, patch_type: str = 'single') -> List[str]:
        """
        Obtiene la lista de patches disponibles de un tipo determinado.
        
        Args:
            patch_type: Tipo de patch ('single', 'multi', etc.)
            
        Returns:
            Lista de nombres de patches
        """
        return list(self.config.get('patches', {}).get(patch_type, {}).keys())
    
    def get_available_effects(self) -> List[str]:
        """
        Obtiene la lista de efectos disponibles.
        
        Returns:
            Lista de nombres de efectos
        """
        return list(self.config.get('effects', {}).keys())
