from datetime import datetime
import config
from clients.langfuse import fetch_all_data_parallel
from services import cache

def _filter_traces_by_date(traces, start_date_str, end_date_str):
    filtered = []
    try:
        start = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except ValueError:
        print("[!] Formato de data invalido recebido.")
        return []
    
    for t in traces:
        ts = t.get("timestamp")
        if not ts: continue
        try:
            # pega yyyy-mm-dd da string iso
            t_date = datetime.strptime(ts[:10], "%Y-%m-%d").date()
            if start <= t_date <= end:
                filtered.append(t)
        except:
            continue
    return filtered

def update_master_dataset():
    # baixa tudo do langfuse e atualiza o redis
    # roda em background
    print(f"[i] Iniciando atualizacao background (Desde {config.GLOBAL_START_DATE})...")
    try:
        today_str = datetime.now().strftime("%Y-%m-%d")
        params = {
            "fromTimestamp": f"{config.GLOBAL_START_DATE}T00:00:00Z",
            "toTimestamp": f"{today_str}T23:59:59Z",
            "tags": None
        }
        
        traces = fetch_all_data_parallel("/api/public/traces", params)
        
        if traces:
            # usa o novo metodo particionado
            cache.set_traces_by_date(traces)
        else:
            print("[!] Nenhum trace baixado.")
            
    except Exception as e:
        print(f"[x] Erro critico na atualizacao: {e}")

def get_traces(start_date, end_date):
    # busca direto do redis pelo range de datas
    # a filtragem fina ja e feita pelas chaves, mas o _filter_traces_by_date
    # garante hora/minuto se necessário
    # e tambem valida o formato
    
    # primeiro valida as datas
    try:
        # apenas teste de formato
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        print("[!] Data invalida em get_traces")
        return []

    return cache.get_traces_by_range(start_date, end_date)