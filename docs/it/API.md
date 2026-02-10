# Documentazione del client API di ACE-Step

**Lingua / 语言 / 言語 / Lingua:** [English](../en/API.md) | [中文](../zh/API.md) | [日本語](../ja/API.md) | [Italiano](API.md)

---

Questo servizio fornisce una API di generazione musicale asincrona basata su HTTP.

**Workflow di base**:
1. Chiama `POST /release_task` per inviare un task e ottenere un `task_id`.
2. Chiama `POST /query_result` per interrogare in batch lo stato finché `status` è `1` (successo) o `2` (fallito).
3. Scarica i file audio tramite gli URL `GET /v1/audio?path=...` restituiti nel risultato.

---

## Indice

- [Autenticazione](#1-autenticazione)
- [Formato di risposta](#2-formato-di-risposta)
- [Descrizione dello stato del task](#3-descrizione-dello-stato-del-task)
- [Creare un task di generazione](#4-creare-un-task-di-generazione)
- [Query batch dei risultati](#5-query-batch-dei-risultati)
- [Formattare l'input](#6-formattare-linput)
- [Ottenere un campione casuale](#7-ottenere-un-campione-casuale)
- [Elencare i modelli disponibili](#8-elencare-i-modelli-disponibili)
- [Statistiche del server](#9-statistiche-del-server)
- [Scaricare file audio](#10-scaricare-file-audio)
- [Health check](#11-health-check)
- [Variabili d'ambiente](#12-variabili-dambiente)

---

## 1. Autenticazione

L'API supporta l'autenticazione opzionale tramite chiave API. Quando abilitata, nelle richieste deve essere fornita una chiave valida.

### Metodi di autenticazione

Sono supportati due metodi:

**Metodo A: `ai_token` nel body della richiesta**

```json
{
  "ai_token": "your-api-key",
  "prompt": "upbeat pop song",
  ...
}
```

**Metodo B: header Authorization**

```bash
curl -X POST http://localhost:8001/release_task \
  -H 'Authorization: Bearer your-api-key' \
  -H 'Content-Type: application/json' \
  -d '{"prompt": "upbeat pop song"}'
```

### Configurare la chiave API

Imposta tramite variabile d'ambiente o argomento della riga di comando:

```bash
# Variabile d'ambiente
export ACESTEP_API_KEY=your-secret-key

# Oppure argomento da riga di comando
python -m acestep.api_server --api-key your-secret-key
```

---

## 2. Formato di risposta

Tutte le risposte API usano un formato wrapper unificato:

```json
{
  "data": { ... },
  "code": 200,
  "error": null,
  "timestamp": 1700000000000,
  "extra": null
}
```

| Campo | Tipo | Descrizione |
| :--- | :--- | :--- |
| `data` | any | Dati effettivi della risposta |
| `code` | int | Codice di stato (200=successo) |
| `error` | string | Messaggio di errore (null in caso di successo) |
| `timestamp` | int | Timestamp della risposta (millisecondi) |
| `extra` | any | Informazioni extra (di solito null) |

---

## 3. Descrizione dello stato del task

Lo stato del task (`status`) è rappresentato da interi:

| Codice | Nome | Descrizione |
| :--- | :--- | :--- |
| `0` | queued/running | Il task è in coda o in esecuzione |
| `1` | succeeded | Generazione riuscita, risultato pronto |
| `2` | failed | Generazione fallita |

---

## 4. Creare un task di generazione

### 4.1 Definizione API

- **URL**: `/release_task`
- **Metodo**: `POST`
- **Content-Type**: `application/json`, `multipart/form-data` o `application/x-www-form-urlencoded`

### 4.2 Parametri della richiesta

#### Convenzione di naming dei parametri

L'API supporta sia **snake_case** sia **camelCase** per la maggior parte dei parametri. Per esempio:
- `audio_duration` / `duration` / `audioDuration`
- `key_scale` / `keyscale` / `keyScale`
- `time_signature` / `timesignature` / `timeSignature`
- `sample_query` / `sampleQuery` / `description` / `desc`
- `use_format` / `useFormat` / `format`

Inoltre, i metadati possono essere passati in un oggetto annidato (`metas`, `metadata` o `user_metadata`).

#### Metodo A: richiesta JSON (application/json)

Adatto per passare solo parametri testuali o per riferirsi a file audio già presenti sul server.

**Parametri di base**:

| Nome parametro | Tipo | Default | Descrizione |
| :--- | :--- | :--- | :--- |
| `prompt` | string | `""` | Prompt di descrizione musicale (alias: `caption`) |
| `lyrics` | string | `""` | Testo delle liriche |
| `thinking` | bool | `false` | Se usare il LM 5Hz per generare audio codes (comportamento lm-dit) |
| `vocal_language` | string | `"en"` | Lingua delle liriche (en, zh, ja, ecc.) |
| `audio_format` | string | `"mp3"` | Formato in uscita (mp3, wav, flac) |

**Parametri modalità campione/descrizione**:

| Nome parametro | Tipo | Default | Descrizione |
| :--- | :--- | :--- | :--- |
| `sample_mode` | bool | `false` | Abilita modalità di generazione campione casuale (auto-genera caption/lyrics/metas via LM) |
| `sample_query` | string | `""` | Descrizione in linguaggio naturale per generare il campione (es. "a soft Bengali love song"). Alias: `description`, `desc` |
| `use_format` | bool | `false` | Usa LM per migliorare/formattare caption e lyrics fornite. Alias: `format` |

**Supporto multi-modello**:

| Nome parametro | Tipo | Default | Descrizione |
| :--- | :--- | :--- | :--- |
| `model` | string | null | Seleziona il modello DiT (es. `"acestep-v15-turbo"`, `"acestep-v15-turbo-shift3"`). Usa `/v1/models` per l'elenco. Se non specificato, usa il modello di default. |

**Semantica di `thinking` (Importante)**:

- `thinking=false`:
  - Il server **NON** usa il LM 5Hz per generare `audio_code_string`.
  - Il DiT gira in modalità **text2music** e **ignora** qualsiasi `audio_code_string` fornita.
- `thinking=true`:
  - Il server usa il LM 5Hz per generare `audio_code_string` (comportamento lm-dit).
  - Il DiT gira con codici generati dal LM per migliorare la qualità musicale.

**Completamento automatico metadati (condizionale)**:

Quando `use_cot_caption=true` o `use_cot_language=true` oppure mancano campi di metadati, il server può usare il LM 5Hz per completare i campi mancanti in base a `caption`/`lyrics`:

- `bpm`
- `key_scale`
- `time_signature`
- `audio_duration`

I valori forniti dall'utente hanno sempre la precedenza; il LM compila solo i campi vuoti/mancanti.

**Parametri attributi musicali**:

| Nome parametro | Tipo | Default | Descrizione |
| :--- | :--- | :--- | :--- |
| `bpm` | int | null | Specifica il tempo (BPM), range 30-300 |
| `key_scale` | string | `""` | Tonalità/scala (es. "C Major", "Am"). Alias: `keyscale`, `keyScale` |
| `time_signature` | string | `""` | Metrica (2, 3, 4, 6 per 2/4, 3/4, 4/4, 6/8). Alias: `timesignature`, `timeSignature` |
| `audio_duration` | float | null | Durata generazione (secondi), range 10-600. Alias: `duration`, `target_duration` |

**Codici audio (opzionali)**:

| Nome parametro | Tipo | Default | Descrizione |
| :--- | :--- | :--- | :--- |
| `audio_code_string` | string o string[] | `""` | Token semantici audio (5Hz) per `llm_dit`. Alias: `audioCodeString` |

**Parametri di controllo generazione**:

| Nome parametro | Tipo | Default | Descrizione |
| :--- | :--- | :--- | :--- |
| `inference_steps` | int | `8` | Numero di step di inferenza. Modello turbo: 1-20 (consigliato 8). Modello base: 1-200 (consigliato 32-64). |
| `guidance_scale` | float | `7.0` | Coefficiente di guidance del prompt. Efficace solo per il modello base. |
| `use_random_seed` | bool | `true` | Se usare un seed casuale |
| `seed` | int | `-1` | Specifica il seed (quando use_random_seed=false) |
| `batch_size` | int | `2` | Numero di generazioni in batch (max 8) |

**Parametri DiT avanzati**:

| Nome parametro | Tipo | Default | Descrizione |
| :--- | :--- | :--- | :--- |
| `shift` | float | `3.0` | Fattore di shift dei timestep (range 1.0-5.0). Efficace solo per modelli base, non turbo. |
| `infer_method` | string | `"ode"` | Metodo di inferenza di diffusione: `"ode"` (Euler, più veloce) o `"sde"` (stocastico). |
| `timesteps` | string | null | Timestep personalizzati come valori separati da virgole (es. `"0.97,0.76,0.615,0.5,0.395,0.28,0.18,0.085,0"`). Sovrascrive `inference_steps` e `shift`. |
| `use_adg` | bool | `false` | Usa Adaptive Dual Guidance (solo modello base) |
| `cfg_interval_start` | float | `0.0` | Rapporto di inizio applicazione CFG (0.0-1.0) |
| `cfg_interval_end` | float | `1.0` | Rapporto di fine applicazione CFG (0.0-1.0) |

**Parametri LM 5Hz (opzionali, lato server)**:

Questi parametri controllano il campionamento LM 5Hz, usato per il completamento metadati e (quando `thinking=true`) per la generazione di codici.

| Nome parametro | Tipo | Default | Descrizione |
| :--- | :--- | :--- | :--- |
| `lm_model_path` | string | null | Nome directory checkpoint LM 5Hz (es. `acestep-5Hz-lm-0.6B`) |
| `lm_backend` | string | `"vllm"` | `vllm` o `pt` |
| `lm_temperature` | float | `0.85` | Temperatura di campionamento |
| `lm_cfg_scale` | float | `2.5` | Scala CFG (>1 abilita CFG) |
| `lm_negative_prompt` | string | `"NO USER INPUT"` | Prompt negativo usato da CFG |
| `lm_top_k` | int | null | Top-k (0/null disabilita) |
| `lm_top_p` | float | `0.9` | Top-p (>=1 verrà considerato disabilitato) |
| `lm_repetition_penalty` | float | `1.0` | Penalità di ripetizione |

**Parametri CoT LM (Chain-of-Thought)**:

| Nome parametro | Tipo | Default | Descrizione |
| :--- | :--- | :--- | :--- |
| `use_cot_caption` | bool | `true` | Consenti al LM di riscrivere/migliorare la caption via CoT. Alias: `cot_caption`, `cot-caption` |
| `use_cot_language` | bool | `true` | Consenti al LM di rilevare la lingua vocale via CoT. Alias: `cot_language`, `cot-language` |
| `constrained_decoding` | bool | `true` | Abilita decoding vincolato basato su FSM per output strutturato. Alias: `constrainedDecoding`, `constrained` |
| `constrained_decoding_debug` | bool | `false` | Abilita log di debug per il decoding vincolato |
| `allow_lm_batch` | bool | `true` | Consenti batch LM per efficienza |

**Parametri audio di modifica/riferimento** (richiede percorso assoluto sul server):

| Nome parametro | Tipo | Default | Descrizione |
| :--- | :--- | :--- | :--- |
| `reference_audio_path` | string | null | Percorso audio di riferimento (Style Transfer) |
| `src_audio_path` | string | null | Percorso audio sorgente (Repainting/Cover) |
| `task_type` | string | `"text2music"` | Tipo di task: `text2music`, `cover`, `repaint`, `lego`, `extract`, `complete` |
| `instruction` | string | auto | Istruzione di editing (auto-generata in base a task_type se non fornita) |
| `repainting_start` | float | `0.0` | Inizio repainting (secondi) |
| `repainting_end` | float | null | Fine repainting (secondi), -1 per fine audio |
| `audio_cover_strength` | float | `1.0` | Intensità cover (0.0-1.0). Valori bassi (0.2) per style transfer. |

#### Metodo B: Upload file (multipart/form-data)

Usa questo metodo quando devi caricare file audio locali come riferimento o sorgente.

Oltre a supportare tutti i campi sopra come form fields, sono supportati anche i seguenti campi file:

- `reference_audio` o `ref_audio`: (File) carica file audio di riferimento
- `src_audio` o `ctx_audio`: (File) carica file audio sorgente

> **Nota**: Dopo il caricamento, i parametri `_path` corrispondenti saranno ignorati automaticamente e il sistema userà il percorso temporaneo del file caricato.

### 4.3 Esempio di risposta

```json
{
  "data": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "queued",
    "queue_position": 1
  },
  "code": 200,
  "error": null,
  "timestamp": 1700000000000,
  "extra": null
}
```

### 4.4 Esempi d'uso (cURL)

**Metodo JSON di base**:

```bash
curl -X POST http://localhost:8001/release_task \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "upbeat pop song",
    "lyrics": "Hello world",
    "inference_steps": 8
  }'
```

**Con thinking=true (LM genera codici + completa i metadati mancanti)**:

```bash
curl -X POST http://localhost:8001/release_task \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "upbeat pop song",
    "lyrics": "Hello world",
    "thinking": true,
    "lm_temperature": 0.85,
    "lm_cfg_scale": 2.5
  }'
```

**Generazione guidata da descrizione (sample_query)**:

```bash
curl -X POST http://localhost:8001/release_task \
  -H 'Content-Type: application/json' \
  -d '{
    "sample_query": "a soft Bengali love song for a quiet evening",
    "thinking": true
  }'
```

**Con miglioramento formato (use_format=true)**:

```bash
curl -X POST http://localhost:8001/release_task \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "pop rock",
    "lyrics": "[Verse 1]\nWalking down the street...",
    "use_format": true,
    "thinking": true
  }'
```

**Seleziona un modello specifico**:

```bash
curl -X POST http://localhost:8001/release_task \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "electronic dance music",
    "model": "acestep-v15-turbo",
    "thinking": true
  }'
```

**Con timesteps personalizzati**:

```bash
curl -X POST http://localhost:8001/release_task \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "jazz piano trio",
    "timesteps": "0.97,0.76,0.615,0.5,0.395,0.28,0.18,0.085,0",
    "thinking": true
  }'
```

**Metodo upload file**:

```bash
curl -X POST http://localhost:8001/release_task \
  -F "prompt=remix this song" \
  -F "src_audio=@/path/to/local/song.mp3" \
  -F "task_type=repaint"
```

---

## 5. Query batch dei risultati

### 5.1 Definizione API

- **URL**: `/query_result`
- **Metodo**: `POST`
- **Content-Type**: `application/json` o `application/x-www-form-urlencoded`

### 5.2 Parametri della richiesta

| Nome parametro | Tipo | Descrizione |
| :--- | :--- | :--- |
| `task_id_list` | string (array JSON) o array | Lista di ID task da interrogare |

### 5.3 Esempio di risposta

```json
{
  "data": [
    {
      "task_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": 1,
      "result": "[{\"file\": \"/v1/audio?path=...\", \"wave\": \"\", \"status\": 1, \"create_time\": 1700000000, \"env\": \"development\", \"prompt\": \"upbeat pop song\", \"lyrics\": \"Hello world\", \"metas\": {\"bpm\": 120, \"duration\": 30, \"genres\": \"\", \"keyscale\": \"C Major\", \"timesignature\": \"4\"}, \"generation_info\": \"...\", \"seed_value\": \"12345,67890\", \"lm_model\": \"acestep-5Hz-lm-0.6B\", \"dit_model\": \"acestep-v15-turbo\"}]"
    }
  ],
  "code": 200,
  "error": null,
  "timestamp": 1700000000000,
  "extra": null
}
```

**Descrizione campi del risultato** (result è una stringa JSON, dopo parsing contiene):

| Campo | Tipo | Descrizione |
| :--- | :--- | :--- |
| `file` | string | URL del file audio (usare con endpoint `/v1/audio`) |
| `wave` | string | Dati della forma d'onda (di solito vuoto) |
| `status` | int | Codice di stato (0=in corso, 1=successo, 2=fallito) |
| `create_time` | int | Tempo di creazione (timestamp Unix) |
| `env` | string | Identificatore ambiente |
| `prompt` | string | Prompt usato |
| `lyrics` | string | Lyrics usate |
| `metas` | object | Metadati (bpm, duration, genres, keyscale, timesignature) |
| `generation_info` | string | Riepilogo info di generazione |
| `seed_value` | string | Valori di seed usati (separati da virgola) |
| `lm_model` | string | Nome del modello LM usato |
| `dit_model` | string | Nome del modello DiT usato |

### 5.4 Esempio d'uso

```bash
curl -X POST http://localhost:8001/query_result \
  -H 'Content-Type: application/json' \
  -d '{
    "task_id_list": ["550e8400-e29b-41d4-a716-446655440000"]
  }'
```

---

## 6. Formattare l'input

### 6.1 Definizione API

- **URL**: `/format_input`
- **Metodo**: `POST`

Questo endpoint usa il LLM per migliorare e formattare caption e lyrics fornite dall'utente.

### 6.2 Parametri della richiesta

| Nome parametro | Tipo | Default | Descrizione |
| :--- | :--- | :--- | :--- |
| `prompt` | string | `""` | Prompt di descrizione musicale |
| `lyrics` | string | `""` | Testo delle liriche |
| `temperature` | float | `0.85` | Temperatura di campionamento LM |
| `param_obj` | string (JSON) | `"{}"` | Oggetto JSON contenente metadati (duration, bpm, key, time_signature, language) |

### 6.3 Esempio di risposta

```json
{
  "data": {
    "caption": "Enhanced music description",
    "lyrics": "Formatted lyrics...",
    "bpm": 120,
    "key_scale": "C Major",
    "time_signature": "4",
    "duration": 180,
    "vocal_language": "en"
  },
  "code": 200,
  "error": null,
  "timestamp": 1700000000000,
  "extra": null
}
```

### 6.4 Esempio d'uso

```bash
curl -X POST http://localhost:8001/format_input \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "pop rock",
    "lyrics": "Walking down the street",
    "param_obj": "{\"duration\": 180, \"language\": \"en\"}"
  }'
```

---

## 7. Ottenere un campione casuale

### 7.1 Definizione API

- **URL**: `/create_random_sample`
- **Metodo**: `POST`

Questo endpoint restituisce parametri di campione casuali da dati di esempio pre-caricati per il riempimento dei form.

### 7.2 Parametri della richiesta

| Nome parametro | Tipo | Default | Descrizione |
| :--- | :--- | :--- | :--- |
| `sample_type` | string | `"simple_mode"` | Tipo campione: `"simple_mode"` o `"custom_mode"` |

### 7.3 Esempio di risposta

```json
{
  "data": {
    "caption": "Upbeat pop song with guitar accompaniment",
    "lyrics": "[Verse 1]\nSunshine on my face...",
    "bpm": 120,
    "key_scale": "G Major",
    "time_signature": "4",
    "duration": 180,
    "vocal_language": "en"
  },
  "code": 200,
  "error": null,
  "timestamp": 1700000000000,
  "extra": null
}
```

### 7.4 Esempio d'uso

```bash
curl -X POST http://localhost:8001/create_random_sample \
  -H 'Content-Type: application/json' \
  -d '{"sample_type": "simple_mode"}'
```

---

## 8. Elencare i modelli disponibili

### 8.1 Definizione API

- **URL**: `/v1/models`
- **Metodo**: `GET`

Restituisce l'elenco dei modelli DiT disponibili caricati sul server.

### 8.2 Esempio di risposta

```json
{
  "data": {
    "models": [
      {
        "name": "acestep-v15-turbo",
        "is_default": true
      },
      {
        "name": "acestep-v15-turbo-shift3",
        "is_default": false
      }
    ],
    "default_model": "acestep-v15-turbo"
  },
  "code": 200,
  "error": null,
  "timestamp": 1700000000000,
  "extra": null
}
```

### 8.3 Esempio d'uso

```bash
curl http://localhost:8001/v1/models
```

---

## 9. Statistiche del server

### 9.1 Definizione API

- **URL**: `/v1/stats`
- **Metodo**: `GET`

Restituisce statistiche di runtime del server.

### 9.2 Esempio di risposta

```json
{
  "data": {
    "jobs": {
      "total": 100,
      "queued": 5,
      "running": 1,
      "succeeded": 90,
      "failed": 4
    },
    "queue_size": 5,
    "queue_maxsize": 200,
    "avg_job_seconds": 8.5
  },
  "code": 200,
  "error": null,
  "timestamp": 1700000000000,
  "extra": null
}
```

### 9.3 Esempio d'uso

```bash
curl http://localhost:8001/v1/stats
```

---

## 10. Scaricare file audio

### 10.1 Definizione API

- **URL**: `/v1/audio`
- **Metodo**: `GET`

Scarica i file audio generati tramite percorso.

### 10.2 Parametri della richiesta

| Nome parametro | Tipo | Descrizione |
| :--- | :--- | :--- |
| `path` | string | Percorso del file audio (URL-encoded) |

### 10.3 Esempio d'uso

```bash
# Scarica usando l'URL dal risultato del task
curl "http://localhost:8001/v1/audio?path=%2Ftmp%2Fapi_audio%2Fabc123.mp3" -o output.mp3
```

---

## 11. Health check

### 11.1 Definizione API

- **URL**: `/health`
- **Metodo**: `GET`

Restituisce lo stato di salute del servizio.

### 11.2 Esempio di risposta

```json
{
  "data": {
    "status": "ok",
    "service": "ACE-Step API",
    "version": "1.0"
  },
  "code": 200,
  "error": null,
  "timestamp": 1700000000000,
  "extra": null
}
```

---

## 12. Variabili d'ambiente

Il server API può essere configurato usando variabili d'ambiente:

### Configurazione server

| Variabile | Default | Descrizione |
| :--- | :--- | :--- |
| `ACESTEP_API_HOST` | `127.0.0.1` | Host di binding del server |
| `ACESTEP_API_PORT` | `8001` | Porta di binding del server |
| `ACESTEP_API_KEY` | (vuoto) | Chiave API (vuoto disabilita auth) |
| `ACESTEP_API_WORKERS` | `1` | Numero di thread worker API |

### Configurazione modelli

| Variabile | Default | Descrizione |
| :--- | :--- | :--- |
| `ACESTEP_CONFIG_PATH` | `acestep-v15-turbo` | Percorso modello DiT principale |
| `ACESTEP_CONFIG_PATH2` | (vuoto) | Percorso modello DiT secondario (opzionale) |
| `ACESTEP_CONFIG_PATH3` | (vuoto) | Percorso modello DiT terziario (opzionale) |
| `ACESTEP_DEVICE` | `auto` | Dispositivo per il caricamento dei modelli |
| `ACESTEP_USE_FLASH_ATTENTION` | `true` | Abilita flash attention |
| `ACESTEP_OFFLOAD_TO_CPU` | `false` | Offload dei modelli su CPU quando inattivi |
| `ACESTEP_OFFLOAD_DIT_TO_CPU` | `false` | Offload del DiT su CPU |

### Configurazione LM

| Variabile | Default | Descrizione |
| :--- | :--- | :--- |
| `ACESTEP_INIT_LLM` | auto | Se inizializzare il LM all'avvio (auto decide in base alla GPU) |
| `ACESTEP_LM_MODEL_PATH` | `acestep-5Hz-lm-0.6B` | Modello LM 5Hz predefinito |
| `ACESTEP_LM_BACKEND` | `vllm` | Backend LM (vllm o pt) |
| `ACESTEP_LM_DEVICE` | (come ACESTEP_DEVICE) | Dispositivo per il LM |
| `ACESTEP_LM_OFFLOAD_TO_CPU` | `false` | Offload LM su CPU |

### Configurazione coda

| Variabile | Default | Descrizione |
| :--- | :--- | :--- |
| `ACESTEP_QUEUE_MAXSIZE` | `200` | Dimensione massima della coda |
| `ACESTEP_QUEUE_WORKERS` | `1` | Numero di worker della coda |
| `ACESTEP_AVG_JOB_SECONDS` | `5.0` | Stima iniziale durata media job |
| `ACESTEP_AVG_WINDOW` | `50` | Finestra per la media durata job |

### Configurazione cache

| Variabile | Default | Descrizione |
| :--- | :--- | :--- |
| `ACESTEP_TMPDIR` | `.cache/acestep/tmp` | Directory file temporanei |
| `TRITON_CACHE_DIR` | `.cache/acestep/triton` | Directory cache Triton |
| `TORCHINDUCTOR_CACHE_DIR` | `.cache/acestep/torchinductor` | Directory cache TorchInductor |

---

## Gestione errori

**Codici di stato HTTP**:

- `200`: Successo
- `400`: Richiesta non valida (JSON errato, campi mancanti)
- `401`: Non autorizzato (chiave API mancante o non valida)
- `404`: Risorsa non trovata
- `415`: Content-Type non supportato
- `429`: Server occupato (coda piena)
- `500`: Errore interno del server

**Formato risposta errore**:

```json
{
  "detail": "Messaggio di errore che descrive il problema"
}
```

---

## Best practice

1. **Usa `thinking=true`** per ottenere i migliori risultati con generazione arricchita dal LM.

2. **Usa `sample_query`/`description`** per generare velocemente da descrizioni in linguaggio naturale.

3. **Usa `use_format=true`** quando hai caption/lyrics ma vuoi che il LM le migliori.

4. **Interroga i task in batch** usando l'endpoint `/query_result` per più task alla volta.

5. **Controlla `/v1/stats`** per capire il carico del server e la durata media dei job.

6. **Usa il supporto multi-modello** impostando `ACESTEP_CONFIG_PATH2` e `ACESTEP_CONFIG_PATH3`, poi seleziona con il parametro `model`.

7. **Per produzione**, imposta `ACESTEP_API_KEY` per abilitare l'autenticazione e proteggere la tua API.

8. **Per ambienti con poca VRAM**, abilita `ACESTEP_OFFLOAD_TO_CPU=true` per supportare generazioni più lunghe.
