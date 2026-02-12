from fastapi import FastAPI, Query
from fastapi import APIRouter, Depends
from contextlib import asynccontextmanager
import asyncio
import time
from services.data import update_master_dataset, get_traces
from services.cost import calculate as calculate_cost
from services.tokens import calculate as calculate_tokens
from services.latency import calculate as calculate_latency
from services.editais import calculate_edital_sections, calculate_edital_queries
from auth.django_auth import validate_django_token
from config import CACHE_TTL_SECONDS

# background task
async def background_task_loop():
    print("[i] Servico de Background iniciado.")
    while True:
        # roda o download em thread separada
        await asyncio.to_thread(update_master_dataset)
        print(f"[i] Dormindo por {CACHE_TTL_SECONDS/3600} horas...")
        await asyncio.sleep(CACHE_TTL_SECONDS)

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(background_task_loop())
    yield
    task.cancel()

app = FastAPI(title="Langfuse Analytics API", version="4.0", lifespan=lifespan)
router = APIRouter()

# custo

@router.get("/cost/total")
def get_cost_total(
    start_date: str = Query(..., description="YYYY-MM-DD"),
    end_date: str = Query(..., description="YYYY-MM-DD")
):
    traces = get_traces(start_date, end_date)
    result = calculate_cost(traces)
    return {"total_cost_usd": result["total"]}

@router.get("/cost/by-user")
def get_cost_by_user(
    start_date: str = Query(..., description="YYYY-MM-DD"),
    end_date: str = Query(..., description="YYYY-MM-DD")
):
    traces = get_traces(start_date, end_date)
    result = calculate_cost(traces)
    return {"users": result["by_user"]}

# tokens

@router.get("/tokens/total")
def get_tokens_total(
    start_date: str = Query(..., description="YYYY-MM-DD"),
    end_date: str = Query(..., description="YYYY-MM-DD")
):
    traces = get_traces(start_date, end_date)
    result = calculate_tokens(traces)
    return {"total_usage": result["total"]}

@router.get("/tokens/by-user")
def get_tokens_by_user(
    start_date: str = Query(..., description="YYYY-MM-DD"),
    end_date: str = Query(..., description="YYYY-MM-DD")
):
    traces = get_traces(start_date, end_date)
    result = calculate_tokens(traces)
    return {"users": result["by_user"]}

# latência

@router.get("/latency/global")
def get_latency_global(
    start_date: str = Query(..., description="YYYY-MM-DD"),
    end_date: str = Query(..., description="YYYY-MM-DD")
):
    traces = get_traces(start_date, end_date)
    result = calculate_latency(traces)
    return {
        "average_latency_seconds": result["global_average"],
        "sample_size": result["sample_size"]
    }

@router.get("/latency/by-user")
def get_latency_by_user(
    start_date: str = Query(..., description="YYYY-MM-DD"),
    end_date: str = Query(..., description="YYYY-MM-DD")
):
    traces = get_traces(start_date, end_date)
    result = calculate_latency(traces)
    return {"users": result["by_user"]}

# editais

@router.get("/edital/sections")
def get_edital_sections(
    edital_number: str = Query(..., description="Numero do edital (ex: 26/2025)"),
    start_date: str = Query(..., description="YYYY-MM-DD"),
    end_date: str = Query(..., description="YYYY-MM-DD"),
    exclusive: bool = Query(True, description="Se True, considera apenas chamadas onde ESTE edital foi o unico alvo.")
):
    traces = get_traces(start_date, end_date)
    result = calculate_edital_sections(traces, edital_number, exclusive=exclusive)
    return result

@router.get("/edital/queries")
def get_edital_queries(
    edital_number: str = Query(..., description="Numero do edital (ex: 26/2025)"),
    start_date: str = Query(..., description="YYYY-MM-DD"),
    end_date: str = Query(..., description="YYYY-MM-DD"),
    exclusive: bool = Query(True, description="Se True, considera apenas chamadas onde ESTE edital foi o unico alvo.")
):
    traces = get_traces(start_date, end_date)
    result = calculate_edital_queries(traces, edital_number, exclusive=exclusive)
    return result

# health

@router.get("/health")
def health():
    return {"status": "ok", "service": "langfuse-analytics"}

app.include_router(router, prefix="/api-langfuse", dependencies=[Depends(validate_django_token)])