from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from app.domain.catalogo_service import CatalogoService
from app.application.catalog_use_cases import GetCareersByProfileUC, GetFinancialReportUC

router = APIRouter(tags=["Catalog"])

@router.get("/careers/{profile}", response_model=List[Dict[str, Any]])
def get_careers_by_profile(profile: str):
    """
    Endpoint to retrieve universities and careers filtered strictly by a specific RIASEC profile.
    
    :param profile: The RIASEC profile letter (e.g., 'R', 'I', 'A').
    :return: A list of universities and careers matching the profile.
    """
    try:
        # Dependency Injection at the Infrastructure level
        catalog_service = CatalogoService()
        use_case = GetCareersByProfileUC(catalog_service)
        
        results = use_case.execute(profile)
        
        if not results:
            # We return 404 if no results are found for a given profile
            raise HTTPException(status_code=404, detail=f"No careers found for profile '{profile}'")
            
        return results
    
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error occurred while processing the request.")


@router.get("/reports/financial", response_model=List[Dict[str, Any]])
def get_financial_report():
    """
    Endpoint to generate a financial report containing cost summaries 
    (minimum and maximum tuition fees) for the universities in Trujillo.
    
    :return: A list of financial summaries per university.
    """
    try:
        # Dependency Injection at the Infrastructure level
        catalog_service = CatalogoService()
        use_case = GetFinancialReportUC(catalog_service)
        
        results = use_case.execute()
        return results
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error occurred while processing the request.")
