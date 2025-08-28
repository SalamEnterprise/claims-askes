"""
Web BFF (Backend for Frontend)
Aggregates and optimizes APIs for web applications
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import httpx
import logging
from typing import Optional

from src.config import settings
from src.aggregators import claims_aggregator, member_aggregator
from src.cache import cache_manager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    logger.info("Starting Web BFF...")
    await cache_manager.connect()
    
    yield
    
    # Shutdown
    logger.info("Shutting down Web BFF...")
    await cache_manager.disconnect()


app = FastAPI(
    title="Web BFF",
    description="Backend for Frontend - Web Applications",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== AGGREGATED ENDPOINTS ====================

@app.get("/api/claims/dashboard/{member_id}")
async def get_member_claims_dashboard(member_id: str):
    """
    Aggregate endpoint for member claims dashboard
    Combines data from multiple services
    """
    try:
        # Fetch data from multiple services in parallel
        async with httpx.AsyncClient() as client:
            # Get member details
            member_response = await client.get(
                f"{settings.MEMBER_SERVICE_URL}/api/v1/members/{member_id}"
            )
            
            # Get claims
            claims_response = await client.get(
                f"{settings.CLAIMS_SERVICE_URL}/api/v1/claims",
                params={"member_id": member_id, "limit": 10}
            )
            
            # Get coverage
            coverage_response = await client.get(
                f"{settings.MEMBER_SERVICE_URL}/api/v1/members/{member_id}/coverage"
            )
            
            # Get accumulators
            accumulator_response = await client.get(
                f"{settings.ADJUDICATION_SERVICE_URL}/api/v1/accumulators/{member_id}"
            )
        
        # Check responses
        if member_response.status_code != 200:
            raise HTTPException(status_code=404, detail="Member not found")
        
        # Aggregate and transform data
        dashboard_data = {
            "member": member_response.json(),
            "recent_claims": claims_response.json() if claims_response.status_code == 200 else [],
            "coverage": coverage_response.json() if coverage_response.status_code == 200 else {},
            "benefit_usage": accumulator_response.json() if accumulator_response.status_code == 200 else {},
            "summary": {
                "total_claims": len(claims_response.json().get("claims", [])),
                "pending_claims": sum(1 for c in claims_response.json().get("claims", []) 
                                    if c.get("status") == "pending"),
                "total_spent": sum(c.get("total_paid_amount", 0) 
                                 for c in claims_response.json().get("claims", []))
            }
        }
        
        return dashboard_data
        
    except httpx.RequestError as e:
        logger.error(f"Error fetching data: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")


@app.post("/api/claims/submit-with-validation")
async def submit_claim_with_validation(claim_data: dict):
    """
    Submit claim with pre-validation
    Aggregates validation from multiple services before submission
    """
    try:
        async with httpx.AsyncClient() as client:
            # Step 1: Validate member eligibility
            eligibility_response = await client.get(
                f"{settings.MEMBER_SERVICE_URL}/api/v1/members/{claim_data['member_id']}/eligibility"
            )
            
            if eligibility_response.status_code != 200 or not eligibility_response.json().get("is_eligible"):
                return {"success": False, "error": "Member not eligible"}
            
            # Step 2: Validate provider
            provider_response = await client.get(
                f"{settings.PROVIDER_SERVICE_URL}/api/v1/providers/{claim_data['provider_id']}"
            )
            
            if provider_response.status_code != 200:
                return {"success": False, "error": "Invalid provider"}
            
            # Step 3: Check if authorization required
            auth_check_response = await client.post(
                f"{settings.AUTHORIZATION_SERVICE_URL}/api/v1/authorization/check",
                json={
                    "service_type": claim_data.get("service_type"),
                    "procedure_codes": [item.get("procedure_code") 
                                       for item in claim_data.get("items", [])]
                }
            )
            
            if auth_check_response.json().get("authorization_required"):
                return {"success": False, "error": "Authorization required", 
                       "authorization_details": auth_check_response.json()}
            
            # Step 4: Submit claim
            claim_response = await client.post(
                f"{settings.CLAIMS_SERVICE_URL}/api/v1/claims",
                json=claim_data
            )
            
            if claim_response.status_code == 201:
                return {
                    "success": True,
                    "claim": claim_response.json(),
                    "message": "Claim submitted successfully"
                }
            else:
                return {"success": False, "error": "Failed to submit claim", 
                       "details": claim_response.json()}
                
    except httpx.RequestError as e:
        logger.error(f"Error submitting claim: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")


@app.get("/api/providers/network-search")
async def search_network_providers(
    specialty: Optional[str] = None,
    city: Optional[str] = None,
    provider_class: Optional[str] = None,
    limit: int = 20
):
    """
    Search for network providers with enriched data
    """
    try:
        async with httpx.AsyncClient() as client:
            # Search providers
            providers_response = await client.get(
                f"{settings.PROVIDER_SERVICE_URL}/api/v1/providers/search",
                params={
                    "specialty": specialty,
                    "city": city,
                    "provider_class": provider_class,
                    "is_network": True,
                    "limit": limit
                }
            )
            
            if providers_response.status_code != 200:
                return {"providers": []}
            
            providers = providers_response.json().get("providers", [])
            
            # Enrich with additional data (e.g., ratings, availability)
            enriched_providers = []
            for provider in providers:
                # Could fetch additional data here
                enriched_provider = {
                    **provider,
                    "rating": 4.5,  # Placeholder
                    "available_slots": 10,  # Placeholder
                    "distance_km": 5.2  # Placeholder
                }
                enriched_providers.append(enriched_provider)
            
            return {
                "providers": enriched_providers,
                "total": len(enriched_providers)
            }
            
    except httpx.RequestError as e:
        logger.error(f"Error searching providers: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")


@app.get("/api/benefits/calculator")
async def calculate_benefits(
    member_id: str,
    service_type: str,
    benefit_code: str,
    charged_amount: float
):
    """
    Calculate estimated benefits for a service
    """
    try:
        async with httpx.AsyncClient() as client:
            # Get member's plan
            coverage_response = await client.get(
                f"{settings.MEMBER_SERVICE_URL}/api/v1/members/{member_id}/coverage"
            )
            
            if coverage_response.status_code != 200:
                raise HTTPException(status_code=404, detail="Coverage not found")
            
            plan_id = coverage_response.json().get("plan_id")
            
            # Get benefit details
            benefit_response = await client.get(
                f"{settings.BENEFIT_SERVICE_URL}/api/v1/plans/{plan_id}/benefits/{benefit_code}"
            )
            
            if benefit_response.status_code != 200:
                raise HTTPException(status_code=404, detail="Benefit not found")
            
            benefit = benefit_response.json()
            
            # Get current accumulator
            accumulator_response = await client.get(
                f"{settings.ADJUDICATION_SERVICE_URL}/api/v1/accumulators/{member_id}",
                params={"benefit_code": benefit_code}
            )
            
            accumulator = accumulator_response.json() if accumulator_response.status_code == 200 else {}
            
            # Calculate estimated coverage
            calculation = {
                "charged_amount": charged_amount,
                "benefit_limit": benefit.get("limit_amount"),
                "used_amount": accumulator.get("used_amount", 0),
                "remaining_benefit": benefit.get("limit_amount", 0) - accumulator.get("used_amount", 0),
                "coinsurance_rate": benefit.get("coinsurance_percentage", 0),
                "estimated_coverage": min(
                    charged_amount * (1 - benefit.get("coinsurance_percentage", 0) / 100),
                    benefit.get("limit_amount", charged_amount) - accumulator.get("used_amount", 0)
                ),
                "estimated_member_responsibility": charged_amount * (benefit.get("coinsurance_percentage", 0) / 100)
            }
            
            return calculation
            
    except httpx.RequestError as e:
        logger.error(f"Error calculating benefits: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")


# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "web-bff"}