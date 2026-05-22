import unittest
import os
import json

from app.domain.catalogo_service import CatalogoService
from app.application.catalog_use_cases import GetCareersByProfileUC, GetFinancialReportUC

class TestCatalogoService(unittest.TestCase):
    """
    Unit tests for the Domain layer: CatalogoService.
    Validates business logic and proper data extraction from the catalog.
    """

    def setUp(self):
        """
        Sets up a temporary dummy JSON file to isolate domain tests from the real database/file.
        """
        self.dummy_catalog = {
            "areas_vocacionales": {
                "1": {
                    "nombre": "Realista",
                    "perfil_riasec": "R",
                    "universidades": [
                        {
                            "nombre": "Tech University",
                            "tipo": "Privada",
                            "matricula_ciclo": 150.00,
                            "carreras": [
                                {"nombre": "Software Engineering", "pension_mensual": 500.00},
                                {"nombre": "Civil Engineering", "pension_mensual": 600.00}
                            ]
                        }
                    ]
                },
                "2": {
                    "nombre": "Artístico",
                    "perfil_riasec": "A",
                    "universidades": [
                        {
                            "nombre": "Arts College",
                            "tipo": "Pública",
                            "matricula_ciclo": 50.00,
                            "carreras": [
                                {"nombre": "Graphic Design", "pension_mensual": 0.00}
                            ]
                        }
                    ]
                }
            }
        }
        
        self.dummy_file_path = "dummy_test_catalog.json"
        with open(self.dummy_file_path, "w", encoding="utf-8") as f:
            json.dump(self.dummy_catalog, f)
            
        self.service = CatalogoService(file_path=self.dummy_file_path)

    def tearDown(self):
        """
        Cleans up the dummy JSON file after tests run.
        """
        if os.path.exists(self.dummy_file_path):
            os.remove(self.dummy_file_path)

    def test_load_catalog_success(self):
        """
        Validates that the catalog loads correctly from a valid JSON file.
        """
        catalog = self.service.cargar_catalogo()
        self.assertIn("areas_vocacionales", catalog)
        self.assertEqual(len(catalog["areas_vocacionales"]), 2)

    def test_load_catalog_file_not_found(self):
        """
        Validates the error handling when the JSON file does not exist.
        """
        invalid_service = CatalogoService(file_path="non_existent_file.json")
        with self.assertRaises(FileNotFoundError):
            invalid_service.cargar_catalogo()

    def test_load_catalog_invalid_json(self):
        """
        Validates the error handling when the JSON file has invalid format.
        """
        invalid_json_path = "invalid_format.json"
        with open(invalid_json_path, "w", encoding="utf-8") as f:
            f.write("{invalid json format")
        
        invalid_service = CatalogoService(file_path=invalid_json_path)
        with self.assertRaises(ValueError):
            invalid_service.cargar_catalogo()
            
        os.remove(invalid_json_path)

    def test_get_by_riasec_profile_exists(self):
        """
        Validates that filtering by an existing RIASEC profile returns the correct universities and careers.
        """
        results = self.service.obtener_por_perfil_riasec("R")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["nombre"], "Tech University")
        self.assertEqual(len(results[0]["carreras"]), 2)

    def test_get_by_riasec_profile_case_insensitive(self):
        """
        Validates that the RIASEC profile filtering is case insensitive.
        """
        results = self.service.obtener_por_perfil_riasec("r")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["nombre"], "Tech University")

    def test_get_by_riasec_profile_not_exists(self):
        """
        Validates that searching for a non-existent profile returns an empty list.
        """
        results = self.service.obtener_por_perfil_riasec("Z")
        self.assertEqual(len(results), 0)

    def test_get_financial_report(self):
        """
        Validates that the financial report properly calculates minimum and maximum tuitions per university.
        """
        results = self.service.obtener_resumen_costos()
        self.assertEqual(len(results), 2)
        
        tech_uni = next((r for r in results if r["universidad"] == "Tech University"), None)
        self.assertIsNotNone(tech_uni)
        self.assertEqual(tech_uni["pension_minima"], 500.00)
        self.assertEqual(tech_uni["pension_maxima"], 600.00)
        self.assertEqual(tech_uni["matricula_ciclo"], 150.00)
        
        arts_uni = next((r for r in results if r["universidad"] == "Arts College"), None)
        self.assertIsNotNone(arts_uni)
        self.assertEqual(arts_uni["pension_minima"], 0.00)
        self.assertEqual(arts_uni["pension_maxima"], 0.00)


class TestCatalogUseCases(unittest.TestCase):
    """
    Unit tests for the Application layer: Use Cases.
    Validates the orchestration and dependency injection.
    """

    def setUp(self):
        """
        Sets up the environment by mocking the Domain Service to isolate the Application layer.
        """
        # Using a dummy path, but we will mock the methods to prevent real file I/O
        self.mock_service = CatalogoService(file_path="dummy.json")
        
        self.mock_universities = [
            {
                "nombre": "Mocked University",
                "carreras": [{"nombre": "Mocked Career", "pension_mensual": 300.0}]
            }
        ]
        
        self.mock_financial_summary = [
            {
                "universidad": "Mocked University", 
                "pension_minima": 300.0, 
                "pension_maxima": 300.0,
                "matricula_ciclo": 100.0
            }
        ]
        
        # Monkey-patching the domain service methods for testing purposes
        self.mock_service.obtener_por_perfil_riasec = lambda profile: self.mock_universities if profile == "R" else []
        self.mock_service.obtener_resumen_costos = lambda: self.mock_financial_summary

    def test_get_careers_by_profile_uc_success(self):
        """
        Validates the successful execution of the GetCareersByProfileUC use case.
        """
        use_case = GetCareersByProfileUC(catalog_service=self.mock_service)
        results = use_case.execute("R")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["nombre"], "Mocked University")

    def test_get_careers_by_profile_uc_empty(self):
        """
        Validates the use case execution when the profile does not exist.
        """
        use_case = GetCareersByProfileUC(catalog_service=self.mock_service)
        results = use_case.execute("X")
        self.assertEqual(len(results), 0)

    def test_get_financial_report_uc(self):
        """
        Validates the successful execution of the GetFinancialReportUC use case.
        """
        use_case = GetFinancialReportUC(catalog_service=self.mock_service)
        results = use_case.execute()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["universidad"], "Mocked University")
        self.assertEqual(results[0]["pension_minima"], 300.0)
        self.assertEqual(results[0]["pension_maxima"], 300.0)

if __name__ == "__main__":
    unittest.main()
