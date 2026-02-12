from collections import Counter
import json

def calculate_edital_sections(traces, edital_number, exclusive=True):
    # analisa os traces para contar quantas vezes cada seção de um edital específico foi consultada
    section_counts = Counter()

    for trace in traces:
        # usa busca recursiva
        found_tool_calls = find_tool_calls(trace)
        
        for tc in found_tool_calls:
            parse_tool_call(tc, edital_number, section_counts=section_counts, query_counts=None, exclusive=exclusive)

    return dict(section_counts)

def calculate_edital_queries(traces, edital_number, exclusive=True):
    # analisa os traces para contar quantas vezes cada query foi feita para um edital específico
    query_counts = Counter()
    
    for trace in traces:
        found_tool_calls = find_tool_calls(trace)
        
        for tc in found_tool_calls:
            parse_tool_call(tc, edital_number, section_counts=None, query_counts=query_counts, exclusive=exclusive)

    return dict(query_counts)

def find_tool_calls(obj):
    # busca recursivamente por tool_calls
    results = []
    
    if isinstance(obj, dict):
        # verifica chave direta
        if 'tool_calls' in obj and isinstance(obj['tool_calls'], list):
            results.extend(obj['tool_calls'])
        
        # recursão nos valores
        for key, value in obj.items():
            # evita recursão infinita ou desnecessária
            if isinstance(value, (dict, list)):
                results.extend(find_tool_calls(value))
                
    elif isinstance(obj, list):
        for item in obj:
            results.extend(find_tool_calls(item))
            
    return results

def parse_tool_call(tool_call, target_edital_number, section_counts=None, query_counts=None, exclusive=True):
    try:
        fn = tool_call.get('function', {})
        if fn.get('name') != 'EditalTool':
            return
            
        args_str = fn.get('arguments', '{}')
        if isinstance(args_str, str):
            try:
                args = json.loads(args_str)
            except:
                return
        else:
            args = args_str
            
        # pega parâmetros
        edital_numbers = args.get('edital_numbers', [])
        sections = args.get('sections', [])
        query = args.get('query', '')
        
        # verifica relevância
        is_relevant = False
        
        if exclusive:
            # modo exclusivo: a lista deve conter apenas o edital alvo
            if isinstance(edital_numbers, list) and len(edital_numbers) == 1 and edital_numbers[0] == target_edital_number:
                is_relevant = True
        else:
            # modo inclusivo
            if not edital_numbers: 
                is_relevant = True
            elif target_edital_number in edital_numbers:
                is_relevant = True
            
        if not is_relevant:
            return

        # contar seções
        if section_counts is not None:
            if not sections:
                section_counts["(Todas)"] += 1
            else:
                for s in sections:
                    section_counts[s] += 1
                    
        # contar queries
        if query_counts is not None:
            if query:
                # normalizar query
                query_counts[query.strip().lower()] += 1

    except Exception:
        pass
