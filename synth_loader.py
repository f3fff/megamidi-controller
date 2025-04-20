# synth_loader.py - Carga configuraciones de sintetizadores desde archivos JSON
import json
import os
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

class SynthLoader:
    """
    Clase para cargar y gestionar configuraciones de sintetizadores desde archivos JSON.
    """
    
    def __init__(self, config_dir: str = "configs"):
        """
        Inicializa el cargador de configuraciones.
        
        Args:
            config_dir: Directorio donde se encuentran los archivos de configuración JSON
        """
        self.config_dir = config_dir
        self.logger = logging.getLogger("SynthLoader")
        self.synths = {}
        
        # Crear directorio de configuraciones si no existe
        os.makedirs(config_dir, exist_ok=True)
    
    def load_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        Carga todas las configuraciones de sintetizadores disponibles.
        
        Returns:
            Diccionario con las configuraciones cargadas
        """
        try:
            # Buscar todos los archivos JSON en el directorio de configuraciones
            config_files = list(Path(self.config_dir).glob("*.json"))
            self.logger.info(f"Encontrados {len(config_files)} archivos de configuración")
            
            # Cargar cada archivo
            for config_file in config_files:
                synth_name = config_file.stem  # Nombre del archivo sin extensión
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        synth_config = json.load(f)
                        self.synths[synth_name] = synth_config
                        self.logger.info(f"Configuración cargada: {synth_name}")
                except Exception as e:
                    self.logger.error(f"Error al cargar {config_file}: {e}")
            
            return self.synths
        except Exception as e:
            self.logger.error(f"Error al cargar configuraciones: {e}")
            return {}
    
    def get_synth_config(self, synth_name: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene la configuración de un sintetizador específico.
        
        Args:
            synth_name: Nombre del sintetizador
            
        Returns:
            Configuración del sintetizador o None si no existe
        """
        return self.synths.get(synth_name)
    
    def get_available_synths(self) -> List[str]:
        """
        Obtiene la lista de sintetizadores disponibles.
        
        Returns:
            Lista de nombres de sintetizadores
        """
        return list(self.synths.keys())
    
    def save_synth_config(self, synth_name: str, config: Dict[str, Any]) -> bool:
        """
        Guarda una configuración de sintetizador en un archivo JSON.
        
        Args:
            synth_name: Nombre del sintetizador
            config: Configuración a guardar
            
        Returns:
            True si se guardó correctamente, False en caso contrario
        """
        try:
            # Asegurar que el directorio existe
            os.makedirs(self.config_dir, exist_ok=True)
            
            # Construir la ruta del archivo
            file_path = os.path.join(self.config_dir, f"{synth_name}.json")
            
            # Guardar configuración
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            # Actualizar el diccionario interno
            self.synths[synth_name] = config
            
            self.logger.info(f"Configuración guardada: {synth_name}")
            return True
        except Exception as e:
            self.logger.error(f"Error al guardar configuración {synth_name}: {e}")
            return False
