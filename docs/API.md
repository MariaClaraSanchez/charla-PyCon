# API pública de Hugging Face Hub

Referencia de la fuente de datos que usa el panel (`app.py`).

## Qué es

**Hugging Face Hub** (https://huggingface.co) es como un "GitHub de la IA". Es donde empresas, universidades y la comunidad publican:

- **Modelos**: redes ya entrenadas (Llama, Whisper, BERT…)
- **Datasets**: conjuntos de datos para entrenar y evaluar modelos (FineWeb, Common Voice, SQuAD…)
- **Spaces**: apps de demostración

La **API pública** permite consultar ese catálogo desde un programa. Responde en JSON y no pide clave ni registro para los datos públicos.

> **La API devuelve metadatos sobre los datasets, no los datos en sí.**
> Es como la ficha de un libro en la biblioteca, no el libro. El panel monitorea
> el *ecosistema* de datos de entrenamiento (cuáles se usan más, de qué tipo,
> con qué licencia), no el contenido de esos datos.

## Endpoint que usa el panel

```
GET https://huggingface.co/api/datasets?sort=downloads&direction=-1&limit=100
```

Es decir: "dame los 100 datasets más descargados, de mayor a menor".

```python
import requests

params = {"sort": "downloads", "direction": -1, "limit": 100}
respuesta = requests.get("https://huggingface.co/api/datasets", params=params, timeout=10)
datasets = respuesta.json()  # lista de diccionarios
```

### Parámetros útiles

| Parámetro | Ejemplo | Para qué sirve |
|---|---|---|
| `sort` | `downloads`, `likes`, `trendingScore`, `createdAt`, `lastModified` | Criterio de orden |
| `direction` | `-1` | Orden descendente |
| `limit` | `100` | Cantidad de resultados |
| `search` | `wiki` | Búsqueda por texto en el nombre |
| `author` | `openai` | Solo datasets de un autor u organización |
| `filter` | `language:es`, `modality:image`, `license:mit` | Filtra por etiqueta |
| `full` | `true` | Incluye más detalles (p. ej. `cardData`) |

## Campos de la respuesta

Ejemplo resumido de un elemento:

```json
{
  "id": "m-a-p/FineFineWeb",
  "author": "m-a-p",
  "downloads": 4352929,
  "likes": 195,
  "gated": false,
  "private": false,
  "createdAt": "2024-12-14T12:46:33.000Z",
  "lastModified": "2024-12-19T11:34:03.000Z",
  "tags": [
    "task_categories:text-classification",
    "task_categories:text-generation",
    "language:en",
    "license:apache-2.0",
    "size_categories:1B<n<10B",
    "modality:tabular",
    "modality:text",
    "region:us"
  ]
}
```

| Campo | Significado |
|---|---|
| `id` | Identificador `autor/nombre` |
| `author` | Usuario u organización que lo publicó |
| `downloads` | Descargas de los **últimos 30 días** (no es el total histórico) |
| `likes` | "Me gusta" de los usuarios en el Hub |
| `tags` | Etiquetas con el formato `categoría:valor` |
| `createdAt` / `lastModified` | Fecha de creación y de la última actualización |
| `gated` | Si hay que aceptar términos para descargarlo |
| `private` | Siempre `false` en el listado público |

### Etiquetas que usa el panel

| Prefijo | Ejemplo | Uso en el panel |
|---|---|---|
| `modality:` | `text`, `image`, `audio` | Color de los gráficos, filtro de la barra lateral |
| `task_categories:` | `text-generation` | Gráfico de tareas |
| `language:` | `en`, `es` | Gráfico de idiomas |
| `license:` | `mit`, `apache-2.0` | Métrica y gráfico de licencias |

Las etiquetas salen del README (la "dataset card") que escribe el propio autor, y algunas las agrega el Hub automáticamente. Por eso muchos datasets aparecen como **"Sin etiqueta"**: el autor no la completó.

## Advertencias (para contar en la charla)

1. **Descargar no es lo mismo que entrenar.** Buena parte de las descargas viene de pruebas automáticas y pipelines de CI. Ejemplo: `huggingface/documentation-images`, que solo guarda las imágenes de la documentación, aparece entre los primeros.
2. **Los datos cambian.** El ranking es de "últimos 30 días" y puede ser distinto el día de la presentación.
3. **Hay límite de peticiones.** La API es abierta, pero no acepta llamadas sin límite. Por eso el panel usa `@st.cache_data(ttl=3600)`: consulta como máximo una vez por hora.

## Para explorar (pega en el navegador)

- Los que tienen más "me gusta":
  https://huggingface.co/api/datasets?sort=likes&direction=-1&limit=5
- Tendencia ahora:
  https://huggingface.co/api/datasets?sort=trendingScore&direction=-1&limit=5
- Los más descargados en español:
  https://huggingface.co/api/datasets?filter=language:es&sort=downloads&direction=-1&limit=5
- Detalles de un dataset:
  https://huggingface.co/api/datasets/m-a-p/FineFineWeb

## Otros endpoints

| Endpoint | Devuelve |
|---|---|
| `/api/models` | Modelos (mismos parámetros) |
| `/api/spaces` | Apps de demostración |
| `/api/datasets/{autor}/{nombre}` | Detalles de un solo dataset |

También existe la biblioteca oficial `huggingface_hub` (`pip install huggingface_hub`):

```python
from huggingface_hub import HfApi

for d in HfApi().list_datasets(sort="downloads", direction=-1, limit=5):
    print(d.id, d.downloads)
```

En la charla, usar `requests` directamente es más didáctico porque muestra que **es solo una URL que devuelve JSON**.

## Documentación oficial

- API del Hub: https://huggingface.co/docs/hub/api
- Dataset cards (de donde salen las etiquetas): https://huggingface.co/docs/hub/datasets-cards
