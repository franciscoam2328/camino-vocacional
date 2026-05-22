import json
import os
from typing import Dict, List, Any

class CatalogoService:
    """
    Servicio de Dominio que maneja la lógica de negocio y el acceso al catálogo de carreras y universidades.
    Implementación pura en Python sin dependencias de infraestructura externas.
    """

    def __init__(self, file_path: str = None):
        """
        Inicializa el servicio.
        :param file_path: Ruta opcional al archivo JSON. Por defecto buscará catalogo.json en el mismo directorio.
        """
        if file_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.file_path = os.path.join(base_dir, "catalogo.json")
        else:
            self.file_path = file_path

    def cargar_catalogo(self) -> Dict[str, Any]:
        """
        Carga el catálogo completo desde el archivo JSON de forma segura.
        Controla las excepciones en caso de que el archivo no exista o el formato sea inválido.
        """
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"El archivo de catálogo no se encontró en la ruta: {self.file_path}")
        
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"El archivo de catálogo contiene un formato JSON inválido: {e}")
        except Exception as e:
            raise RuntimeError(f"Ocurrió un error inesperado al intentar leer el catálogo: {e}")

    def obtener_por_perfil_riasec(self, perfil: str) -> List[Dict[str, Any]]:
        """
        Obtiene las universidades y carreras filtradas estrictamente por un perfil RIASEC específico.
        :param perfil: Letra del perfil RIASEC (ej: 'R', 'I', 'A').
        :return: Lista de universidades con sus carreras que corresponden al perfil.
        """
        catalogo = self.cargar_catalogo()
        areas = catalogo.get("areas_vocacionales", {})
        
        universidades_filtradas = []
        
        for _, area_data in areas.items():
            if area_data.get("perfil_riasec", "").upper() == perfil.upper():
                universidades_filtradas.extend(area_data.get("universidades", []))
                
        return universidades_filtradas

    def obtener_resumen_costos(self) -> List[Dict[str, Any]]:
        """
        Obtiene un resumen de costos (pensión y matrícula) por universidad.
        Consolida la información de rangos de pensiones para ayudar en decisiones financieras.
        """
        catalogo = self.cargar_catalogo()
        areas = catalogo.get("areas_vocacionales", {})
        
        resumen_dict = {}
        
        for _, area_data in areas.items():
            for uni in area_data.get("universidades", []):
                nombre_uni = uni.get("nombre")
                if not nombre_uni:
                    continue
                
                if nombre_uni not in resumen_dict:
                    resumen_dict[nombre_uni] = {
                        "tipo": uni.get("tipo"),
                        "matricula_ciclo": uni.get("matricula_ciclo"),
                        "pensiones": set() # Usamos set para coleccionar las distintas tarifas
                    }
                
                # Coleccionar todas las pensiones de las carreras en esta universidad
                for carrera in uni.get("carreras", []):
                    pension = carrera.get("pension_mensual")
                    if pension is not None:
                        resumen_dict[nombre_uni]["pensiones"].add(pension)

        # Formatear el resultado final calculando mínimos y máximos
        resultado = []
        for nombre, datos in resumen_dict.items():
            pensiones = list(datos["pensiones"])
            pension_min = min(pensiones) if pensiones else 0.0
            pension_max = max(pensiones) if pensiones else 0.0
            
            resultado.append({
                "universidad": nombre,
                "tipo": datos["tipo"],
                "matricula_ciclo": datos["matricula_ciclo"],
                "pension_minima": pension_min,
                "pension_maxima": pension_max
            })
            
        return resultado
