from collections import defaultdict

def calculate(traces):
    total = 0.0
    by_user = defaultdict(float)

    for t in traces:
        c = t.get("totalCost") or 0.0
        uid = t.get("userId") or "Anonymous"
        
        total += c
        by_user[uid] += c

    users_list = [{"user_id": k, "cost": v} for k,v in by_user.items()]
    users_list.sort(key=lambda x: x["cost"], reverse=True)

    return {"total": total, "by_user": users_list}