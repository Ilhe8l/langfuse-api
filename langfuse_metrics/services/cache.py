import json
import redis
from config import REDIS_HOST, REDIS_PORT, CACHE_TTL_SECONDS

# conexao com redis
r = redis.Redis(
    host=REDIS_HOST, 
    port=REDIS_PORT, 
    decode_responses=False,
    health_check_interval=30,
    socket_keepalive=True,
    retry_on_timeout=True,
    socket_connect_timeout=5
)

import zlib
from datetime import datetime, timedelta

MASTER_KEY_PREFIX = "langfuse:traces:"

def set_traces_by_date(traces):
    # agrupa traces por data e salva comprimido no redis.
    # chave: langfuse:traces:yyyy-mm-dd
    try:
        # agrupa por data
        by_date = {}
        for t in traces:
            ts = t.get("timestamp")
            if not ts: continue
            date_str = ts[:10] # YYYY-MM-DD
            if date_str not in by_date:
                by_date[date_str] = []
            by_date[date_str].append(t)
            
        # pipeline para salvar em lote
        pipe = r.pipeline()
        count_keys = 0
        
        for date_str, daily_traces in by_date.items():
            key = f"{MASTER_KEY_PREFIX}{date_str}"
            json_data = json.dumps(daily_traces)
            compressed = zlib.compress(json_data.encode('utf-8'))
            
            # expira em cache_ttl_seconds (padrao 24h ou conforme config)
            pipe.setex(key, CACHE_TTL_SECONDS, compressed)
            count_keys += 1
            
        pipe.execute()
        print(f"[*] Redis atualizado: {len(traces)} traces distribuidos em {count_keys} chaves de data.")
        
    except Exception as e:
        print(f"[x] Erro de escrita no Redis (particionado): {e}")

def get_traces_by_range(start_date, end_date):
    # busca chaves de start_date a end_date, desconprime e retorna lista unica.
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        # gera lista de chaves
        keys = []
        curr = start
        while curr <= end:
            keys.append(f"{MASTER_KEY_PREFIX}{curr.strftime('%Y-%m-%d')}")
            curr += timedelta(days=1)
            
        if not keys:
            return []
            
        # busca em batch
        # mget retorna lista de valores na mesma ordem
        values = r.mget(keys)
        
        all_traces = []
        for val in values:
            if val:
                try:
                    decompressed = zlib.decompress(val).decode('utf-8')
                    daily_traces = json.loads(decompressed)
                    all_traces.extend(daily_traces)
                except Exception as e:
                    print(f"[!] Erro ao descomprimir/ler chave: {e}")
                    continue
                    
        return all_traces

    except Exception as e:
        print(f"[x] Erro de leitura do Redis (range): {e}")
        return []