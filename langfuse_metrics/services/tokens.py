from collections import defaultdict

def _extract(obj):
    if not isinstance(obj, dict): return 0,0,0
    i = obj.get("input", 0) or obj.get("promptTokens", 0) or obj.get("input_tokens", 0)
    o = obj.get("output", 0) or obj.get("completionTokens", 0) or obj.get("output_tokens", 0)
    t = obj.get("total", 0) or obj.get("totalTokens", 0) or obj.get("total_tokens", 0)
    if t == 0 and (i>0 or o>0): t = i+o
    return i, o, t

def _get_usage(trace):
    raw = trace.get("usage")
    if raw:
        if isinstance(raw, dict): return _extract(raw)
        if isinstance(raw, list):
            ti,to,tt = 0,0,0
            for u in raw: 
                i,o,t = _extract(u)
                ti+=i; to+=o; tt+=t
            return ti,to,tt
            
    out = trace.get("output")
    if isinstance(out, dict):
        if "usage_metadata" in out: return _extract(out["usage_metadata"])
        msgs = out.get("messages", [])
        if isinstance(msgs, list):
            ti,to,tt = 0,0,0
            found=False
            for m in msgs:
                if not isinstance(m, dict): continue
                meta = m.get("usage_metadata") or m.get("response_metadata", {}).get("token_usage")
                if meta:
                    i,o,t = _extract(meta)
                    ti+=i; to+=o; tt+=t
                    found=True
            if found: return ti,to,tt
    return 0,0,0

def calculate(traces):
    general = {"input": 0, "output": 0, "total": 0}
    by_user = defaultdict(lambda: {"input": 0, "output": 0, "total": 0})

    for t in traces:
        uid = t.get("userId") or "Anonymous"
        i, o, tot = _get_usage(t)
        
        general["input"] += i
        general["output"] += o
        general["total"] += tot
        
        by_user[uid]["input"] += i
        by_user[uid]["output"] += o
        by_user[uid]["total"] += tot
        
    users_list = [{"user_id": k, **v} for k,v in by_user.items()]
    users_list.sort(key=lambda x: x["total"], reverse=True)
    
    return {"total": general, "by_user": users_list}