import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import config

def _get_api_url(endpoint):
    host = config.LANGFUSE_HOST.rstrip("/")
    if not endpoint.startswith("/"):
        endpoint = "/" + endpoint
    return f"{host}{endpoint}"

def _fetch_page_with_retry(url, params, page, max_retries=3):
    local_params = params.copy()
    local_params["page"] = page
    delay = 1
    
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(
                url, auth=config.AUTH, params=local_params, 
                headers=config.HEADERS, timeout=60
            )
            if response.status_code == 200: 
                return response.json()
            if 400 <= response.status_code < 500: 
                print(f"[x] Erro cliente pag {page}: {response.status_code}")
                return None
            response.raise_for_status()
        except Exception as e:
            if attempt == max_retries:
                print(f"[x] Falha definitiva pag {page}: {e}")
                return None
            time.sleep(delay)
            delay *= 2
    return None

def fetch_all_data_parallel(endpoint, params=None):
    if params is None: params = {}
    if "limit" not in params: params["limit"] = 100
    
    url = _get_api_url(endpoint)
    all_items = []

    print(f"[i] Iniciando download de {url}...")
    first_page = _fetch_page_with_retry(url, params, 1)
    if not first_page: return []

    all_items.extend(first_page.get("data", []))
    total_pages = first_page.get("meta", {}).get("totalPages", 1)

    if total_pages > 1:
        workers = min(config.MAX_WORKERS, 10)
        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_page = {
                executor.submit(_fetch_page_with_retry, url, params, p): p 
                for p in range(2, total_pages + 1)
            }
            for future in as_completed(future_to_page):
                res = future.result()
                if res: all_items.extend(res.get("data", []))
            
    print(f"[*] Download concluido. Total: {len(all_items)}")
    return all_items