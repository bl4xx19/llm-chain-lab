# LLM Chain Lab

Aplicación web experimental con cuatro escenarios simulados (Salud, E-commerce, Soporte técnico y Banca). Cada escenario integra un asistente con LLM y function calling, y permite probar cadenas de vulnerabilidades de dos eslabones. Todos los datos son ficticios.

## Requisitos

- Docker y Docker Compose v2 (el comando `docker compose`).
- Una clave de API de un proveedor compatible con el formato de OpenAI (Groq por defecto).
- Acceso a Internet desde el contenedor del backend, solo hacia el proveedor LLM.

## Estructura

```
llm-chain-lab/
  docker-compose.yml
  .env.example
  backend/    FastAPI, escenarios, funciones vulnerables, ejecutor LLM, indicadores y scripts
  frontend/   React con Vite
  nginx/      proxy inverso, único punto expuesto
```

Servicios: `db` (PostgreSQL 16), `backend` (FastAPI en el puerto 8000 interno), `frontend` (Vite en el puerto 5173 interno) y `nginx`, que publica la aplicación solo en `127.0.0.1:8080`.

## Levantar la aplicación

1. Entra a la carpeta del proyecto:

```
cd llm-chain-lab
```

2. Crea el archivo de configuración a partir del ejemplo:

```
cp .env.example .env
```

3. Edita `.env` y pon tu clave en `LLM_API_KEY`. Si usas otro proveedor, cambia también `LLM_BASE_URL` y `LLM_MODEL` (ver la sección de proveedores).

4. Construye y arranca todo:

```
docker compose up -d --build
```

5. Comprueba que los cuatro servicios estén activos:

```
docker compose ps
```

6. Abre en el navegador:

```
http://127.0.0.1:8080
```

La primera vez, el backend crea las tablas y carga los datos iniciales de los cuatro escenarios de forma automática.

## Comandos útiles

Ver los logs del backend:

```
docker compose logs -f backend
```

Comprobar que el backend responde:

```
docker compose exec backend python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/health').read())"
```

Detener la aplicación conservando los datos:

```
docker compose down
```

Detenerla y borrar también la base de datos (se vuelve a sembrar al arrancar):

```
docker compose down -v
```

Reiniciar solo el backend:

```
docker compose restart backend
```

## Cambiar el proveedor o el modelo

El backend lee el archivo `.env` solo cuando se crea el contenedor. Después de editarlo hay que recrearlo:

```
docker compose up -d --force-recreate backend
```

Variables principales del `.env`:

| Variable | Descripción |
|---|---|
| `LLM_BASE_URL` | URL base de la API compatible con OpenAI |
| `LLM_API_KEY` | Clave del proveedor |
| `LLM_MODEL` | Nombre del modelo |
| `LLM_TEMPERATURE` | Temperatura, 0 por defecto |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Credenciales de la base de datos |
| `LLM_MIN_INTERVAL_SECONDS` | Opcional. Segundos mínimos entre dos llamadas al proveedor. Sin esta variable no hay pausa. |
| `LLM_MAX_RETRIES` | Opcional. Reintentos del SDK. Sin esta variable se usa el valor por defecto del SDK. Con `0` no hay reintentos silenciosos. |

Ejemplos:

Groq con gpt-oss-20b (valores por defecto):

```
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=openai/gpt-oss-20b
```

Groq con gpt-oss-120b:

```
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=openai/gpt-oss-120b
```

Gemini, con pausa entre llamadas para respetar el límite por minuto de la capa gratuita:

```
LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
LLM_MODEL=gemini-3.5-flash-lite
LLM_MIN_INTERVAL_SECONDS=4.5
LLM_MAX_RETRIES=0
```

Las variables `GROQ_API_KEY`, `GEMINI_API_KEY` y `OPENROUTER_API_KEY` del ejemplo solo las usa el script `pilot_multi_model.py`.

## Rutas expuestas por nginx

| Ruta | Contenido |
|---|---|
| `/` | Interfaz web |
| `/chat/{salud,ecommerce,soporte,banca}` | Chat de cada escenario |
| `/chat/{escenario}/reset` | Restaura los datos iniciales del escenario |
| `/logs/` | Registro de interacciones |
| `/admin/{escenario}/estado` | Estado actual de la base de datos de cada escenario, de solo lectura, para el panel de verificación |
| `/resolucion` | Guía de resolución de cada cadena |

## Ejecutar una campaña experimental

Las campañas se ejecutan dentro del contenedor del backend. Con la aplicación levantada:

Las 16 cadenas con 5 intentos cada una, repartidas por rondas:

```
docker compose exec backend python -m app.scripts.run_experiment --order round_robin
```

Opciones disponibles:

| Opción | Descripción |
|---|---|
| `--chain 1.1` | Corre solo esa cadena |
| `--attempts N` | Cambia el número de intentos |
| `--technique {directa,autoridad,forzada}` | Técnica de persuasión, `forzada` por defecto |
| `--order {block,round_robin}` | `block` hace todos los intentos de una cadena seguidos, `round_robin` hace un intento de cada cadena por ronda |
| `--skip-control-checks` | No ejecuta IND-3 e IND-4 |

Cada intento restaura los datos del escenario antes de ejecutarse. Los resultados se guardan en `backend/app/scripts/experiment_runs/`, que queda visible en tu máquina porque la carpeta `backend/app` está montada dentro del contenedor.

## Seguridad

La aplicación es deliberadamente vulnerable. Úsala solo en un entorno aislado.

- No expone puertos de la base de datos ni del backend al host. Solo nginx, en `127.0.0.1:8080`.
- Los endpoints `/admin/*` no tienen autenticación.
- No subas el archivo `.env` a ningún repositorio, porque contiene tu clave de API.
