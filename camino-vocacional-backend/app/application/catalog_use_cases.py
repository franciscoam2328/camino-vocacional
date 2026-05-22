from typing import List, Dict, Any
# Using absolute import assuming 'app' is the root package of the backend
from app.domain.catalogo_service import CatalogoService

class GetCareersByProfileUC:
    """
    Use case to retrieve universities and careers filtered strictly by a specific RIASEC profile.
    This class belongs to the Application Layer in a Clean/Hexagonal Architecture.
    """
    def __init__(self, catalog_service: CatalogoService):
        """
        Initializes the use case with the required domain service.
        
        :param catalog_service: Instance of CatalogoService (Dependency Injection).
        """
        self._catalog_service = catalog_service

    def execute(self, profile: str) -> List[Dict[str, Any]]:
        """
        Executes the use case to get careers by RIASEC profile.
        
        :param profile: The RIASEC profile letter (e.g., 'R', 'I', 'A').
        :return: A list of universities and their respective careers matching the profile.
        """
        return self._catalog_service.obtener_por_perfil_riasec(profile)


class GetFinancialReportUC:
    """
    Use case to generate a financial report containing cost summaries (minimum and maximum tuition fees)
    for the universities in Trujillo.
    This class belongs to the Application Layer in a Clean/Hexagonal Architecture.
    """
    def __init__(self, catalog_service: CatalogoService):
        """
        Initializes the use case with the required domain service.
        
        :param catalog_service: Instance of CatalogoService (Dependency Injection).
        """
        self._catalog_service = catalog_service

    def execute(self) -> List[Dict[str, Any]]:
        """
        Executes the use case to obtain the financial summary.
        
        :return: A list of financial summaries per university, including min and max costs.
        """
        return self._catalog_service.obtener_resumen_costos()
