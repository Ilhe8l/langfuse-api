from collections import defaultdict

def calculate(traces):
    gen_sum, gen_count = 0.0, 0
    user_agg = defaultdict(lambda: [0.0, 0])

    for t in traces:
        lat = t.get("latency")
        uid = t.get("userId") or "Anonymous"
        
        if lat is not None:
            gen_sum += lat
            gen_count += 1
            user_agg[uid][0] += lat
            user_agg[uid][1] += 1
            
    avg_gen = (gen_sum / gen_count) if gen_count > 0 else 0.0
    
    users_list = []
    for uid, val in user_agg.items():
        avg = (val[0] / val[1]) if val[1] > 0 else 0.0
        users_list.append({"user_id": uid, "avg_latency": avg, "count": val[1]})
        
    users_list.sort(key=lambda x: x["avg_latency"], reverse=True)
    
    return {
        "global_average": avg_gen,
        "sample_size": gen_count,
        "by_user": users_list
    }