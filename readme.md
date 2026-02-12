# API de Métricas Langfuse

Esta API é responsável por coletar, cachear e expor métricas dos traces do Langfuse de forma otimizada. Ela funciona baixando os dados em background e salvando-os comprimidos no Redis, permitindo consultas rápidas de custo, tokens e latência.

## Como começar

A forma mais simples de rodar o projeto é utilizando o Docker Compose:

```bash
docker compose up --build
```
Isso iniciará a API na porta `8003` e o Redis na porta `6379`.

## Configuração

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis (baseado no `.env.example`):

```ini
# Configurações do Langfuse
LANGFUSE_HOST=https://cloud.langfuse.com
PUBLIC_KEY=pk-lf-...
SECRET_KEY=sk-lf-...

# Configurações do Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Configurações Gerais
GLOBAL_START_DATE=2025-01-01
CACHE_TTL_SECONDS=86400  # 24 horas em segundos

# Performance e Autenticação
MAX_WORKERS=10
DJANGO_AUTH_URL=http://django:8000/api/validate-token/
```

## Endpoints Disponíveis

A API roda em `http://localhost:8003/api-langfuse`. Todos os endpoints exigem os parâmetros `start_date` e `end_date` (formato YYYY-MM-DD) e o header `Authorization: Token ...`.

### Custos
- `GET /cost/total`: Custo total no período.
- `GET /cost/by-user`: Custo detalhado por usuário.

### Tokens
- `GET /tokens/total`: Total de tokens utilizados (input, output e total).
- `GET /tokens/by-user`: Uso de tokens por usuário.

### Latência
- `GET /latency/global`: Média de latência global.
- `GET /latency/by-user`: Latência média por usuário.

### Editais
- `GET /edital/sections`: Seções mais acessadas de um edital.
- `GET /edital/queries`: Perguntas mais frequentes sobre um edital.
  - Parâmetros adicionais: `edital_number` (ex: 26/2025) e `exclusive` (padrão `true`, filtra apenas chamadas focadas).

### Funcionalidades Extras

- **Filtro Exclusivo**: Nos endpoints de editais, o parâmetro `exclusive=true` garante que apenas interações onde o edital foi o **único** contexto sejam contabilizadas.

## Funcionamento Interno

1. Ao iniciar, a API dispara uma tarefa em background que baixa os traces do Langfuse a partir da `GLOBAL_START_DATE`.
2. Os dados são agrupados por dia e armazenados comprimidos no Redis para eficiência.
3. As consultas buscam diretamente do cache, descomprimindo e calculando as métricas em tempo real.
