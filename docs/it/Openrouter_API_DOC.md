# Documentazione API OpenRouter di ACE-Step

> API compatibile con OpenAI Chat Completions per la generazione musicale AI

**Base URL:** `http://{host}:{port}` (default `http://127.0.0.1:8002`)

---

## Indice

- [Autenticazione](#autenticazione)
- [Endpoint](#endpoint)
  - [POST /v1/chat/completions - Genera musica](#1-genera-musica)
  - [GET /v1/models - Lista modelli](#2-lista-modelli)
  - [GET /health - Health check](#3-health-check)
- [Modalità di input](#modalità-di-input)
- [Input audio](#input-audio)
- [Risposte in streaming](#risposte-in-streaming)
- [Esempi](#esempi)
- [Codici di errore](#codici-di-errore)

---

## Autenticazione

Se il server è configurato con una chiave API (tramite variabile d'ambiente `OPENROUTER_API_KEY` o flag CLI `--api-key`), tutte le richieste devono includere questo header:

```
Authorization: Bearer <your-api-key>
```

Non è richiesta autenticazione quando non è configurata alcuna chiave.

---

## Endpoint

### 1. Genera musica

**POST** `/v1/chat/completions`

Genera musica da messaggi chat e restituisce audio insieme a metadati generati dall'LM.

#### Parametri della richiesta

| Campo | Tipo | Richiesto | Default | Descrizione |
|---|---|---|---|---|
| `model` | string | No | auto | ID modello (ottenibile da `/v1/models`) |
| `messages` | array | **Sì** | - | Lista messaggi chat. Vedi [Modalità di input](#modalità-di-input) |
| `stream` | boolean | No | `false` | Abilita risposta streaming. Vedi [Risposte in streaming](#risposte-in-streaming) |
| `audio_config` | object | No | `null` | Configurazione generazione audio. Vedi sotto |
| `temperature` | float | No | `0.85` | Temperatura di campionamento LM |
| `top_p` | float | No | `0.9` | Parametro nucleus sampling LM |
| `seed` | int \| string | No | `null` | Seed casuale. Quando `batch_size > 1`, usa valori separati da virgola, es. `"42,123,456"` |
| `lyrics` | string | No | `""` | Lyrics passate direttamente (priorità su lyrics parsate dai messaggi). Quando impostato, il testo dei messaggi diventa il prompt |
| `sample_mode` | boolean | No | `false` | Abilita modalità sample LLM. Il testo dei messaggi diventa sample_query per auto-generare prompt/lyrics |
| `thinking` | boolean | No | `false` | Abilita thinking mode LLM per ragionamento più profondo |
| `use_format` | boolean | No | `false` | Quando l'utente fornisce prompt/lyrics, li migliora via formattazione LLM |
| `use_cot_caption` | boolean | No | `true` | Riscrive/migliora la descrizione musicale via Chain-of-Thought |
| `use_cot_language` | boolean | No | `true` | Auto-rileva la lingua vocale via Chain-of-Thought |
| `guidance_scale` | float | No | `7.0` | Scala di guidance classifier-free |
| `batch_size` | int | No | `1` | Numero di campioni audio da generare |
| `task_type` | string | No | `"text2music"` | Tipo task. Vedi [Input audio](#input-audio) |
| `repainting_start` | float | No | `0.0` | Inizio regione repaint (secondi) |
| `repainting_end` | float | No | `null` | Fine regione repaint (secondi) |
| `audio_cover_strength` | float | No | `1.0` | Intensità cover (0.0~1.0) |

#### Oggetto audio_config

| Campo | Tipo | Default | Descrizione |
|---|---|---|---|
| `duration` | float | `null` | Durata audio in secondi. Se omessa, determinata automaticamente dal LM |
| `bpm` | integer | `null` | Battiti al minuto. Se omesso, determinato automaticamente dal LM |
| `vocal_language` | string | `"en"` | Codice lingua vocale (es. `"zh"`, `"en"`, `"ja"`) |
| `instrumental` | boolean | `null` | Se generare solo strumentale (senza voci). Se omesso, determinato automaticamente dalle lyrics |
| `format` | string | `"mp3"` | Formato audio in uscita |
| `key_scale` | string | `null` | Tonalità musicale (es. `"C major"`) |
| `time_signature` | string | `null` | Metrica (es. `"4/4"`) |

> **Il significato del testo nei messaggi dipende dalla modalità:**
> - Se `lyrics` è impostato → testo messaggi = prompt (descrizione musicale)
> - Se `sample_mode: true` → testo messaggi = sample_query (LM genera tutto)
> - Nessuno impostato → auto-detect: tag → modalità tag, testo tipo lyrics → modalità lyrics, altrimenti → modalità sample

#### Formato messages

Supporta testo semplice e formato multimodale (testo + audio):

**Testo semplice:**

```json
{
  "messages": [
    {"role": "user", "content": "Your input content"}
  ]
}
```

**Multimodale (con input audio):**

```json
{
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "Cover this song"},
        {
          "type": "input_audio",
          "input_audio": {
            "data": "<base64 audio data>",
            "format": "mp3"
          }
        }
      ]
    }
  ]
}
```

---

#### Risposta non streaming (`stream: false`)

```json
{
  "id": "chatcmpl-a1b2c3d4e5f6g7h8",
  "object": "chat.completion",
  "created": 1706688000,
  "model": "acestep/acestep-v15-turbo",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "## Metadata\n**Caption:** Upbeat pop song...\n**BPM:** 120\n**Duration:** 30s\n**Key:** C major\n\n## Lyrics\n[Verse 1]\nHello world...",
        "audio": [
          {
            "type": "audio_url",
            "audio_url": {
              "url": "data:audio/mpeg;base64,SUQzBAAAAAAAI1RTU0UAAAA..."
            }
          }
        ]
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 100,
    "total_tokens": 110
  }
}
```

**Campi della risposta:**

| Campo | Descrizione |
|---|---|
| `choices[0].message.content` | Informazioni testuali generate dal LM, incluse Metadata (Caption/BPM/Duration/Key/Time Signature/Language) e Lyrics. Restituisce `"Music generated successfully."` se LM non è coinvolto |
| `choices[0].message.audio` | Array di dati audio. Ogni elemento contiene `type` (`"audio_url"`) e `audio_url.url` (Data URL Base64 nel formato `data:audio/mpeg;base64,...`) |
| `choices[0].finish_reason` | `"stop"` indica completamento normale |

**Decodifica audio:**

Il valore `audio_url.url` è un Data URL: `data:audio/mpeg;base64,<base64_data>`

Estrai la porzione base64 dopo la virgola e decodificala per ottenere il file MP3:

```python
import base64

url = response["choices"][0]["message"]["audio"][0]["audio_url"]["url"]
# Rimuovi il prefisso "data:audio/mpeg;base64,"
b64_data = url.split(",", 1)[1]
audio_bytes = base64.b64decode(b64_data)

with open("output.mp3", "wb") as f:
    f.write(audio_bytes)
```

```javascript
const url = response.choices[0].message.audio[0].audio_url.url;
const b64Data = url.split(",")[1];
const audioBytes = atob(b64Data);
// Oppure usa direttamente il Data URL in un elemento <audio>
const audio = new Audio(url);
audio.play();
```

---

### 2. Lista modelli

**GET** `/v1/models`

Restituisce le informazioni sui modelli disponibili.

#### Risposta

```json
{
  "object": "list",
  "data": [
    {
      "id": "acestep/acestep-v15-turbo",
      "name": "ACE-Step acestep-v15-turbo",
      "created": 1706688000,
      "input_modalities": ["text", "audio"],
      "output_modalities": ["audio", "text"],
      "context_length": 4096,
      "max_output_length": 300,
      "pricing": {"prompt": "0", "completion": "0", "request": "0"},
      "description": "AI music generation model"
    }
  ]
}
```

---

### 3. Health check

**GET** `/health`

#### Risposta

```json
{
  "status": "ok",
  "service": "ACE-Step OpenRouter API",
  "version": "1.0"
}
```

---

## Modalità di input

Il sistema seleziona automaticamente la modalità di input in base al contenuto dell'ultimo messaggio `user`. Puoi anche specificarla esplicitamente tramite i campi `lyrics` o `sample_mode`.

### Modalità 1: Modalità tag (consigliata)

Usa i tag `<prompt>` e `<lyrics>` per specificare in modo esplicito descrizione musicale e lyrics:

```json
{
  "messages": [
    {
      "role": "user",
      "content": "<prompt>A gentle acoustic ballad in C major, female vocal</prompt>\n<lyrics>[Verse 1]\nSunlight through the window\nA brand new day begins\n\n[Chorus]\nWe are the dreamers\nWe are the light</lyrics>"
    }
  ],
  "audio_config": {
    "duration": 30,
    "vocal_language": "en"
  }
}
```

- `<prompt>...</prompt>` — Descrizione stile/scena musicale (caption)
- `<lyrics>...</lyrics>` — Contenuto lyrics
- Entrambi i tag possono essere usati da soli
- Quando `use_format: true`, l'LLM migliora automaticamente prompt e lyrics

### Modalità 2: Linguaggio naturale (Sample Mode)

Descrivi la musica desiderata in linguaggio naturale. Il sistema usa l'LLM per generare automaticamente prompt e lyrics:

```json
{
  "messages": [
    {"role": "user", "content": "Generate an upbeat pop song about summer and travel"}
  ],
  "sample_mode": true,
  "audio_config": {
    "vocal_language": "en"
  }
}
```

Condizione di trigger: `sample_mode: true`, oppure il contenuto del messaggio non contiene tag e non assomiglia a lyrics.

### Modalità 3: Solo lyrics

Passa direttamente lyrics con marcatori di struttura. Il sistema le identifica automaticamente:

```json
{
  "messages": [
    {
      "role": "user",
      "content": "[Verse 1]\nWalking down the street\nFeeling the beat\n\n[Chorus]\nDance with me tonight\nUnder the moonlight"
    }
  ],
  "audio_config": {"duration": 30}
}
```

Condizione di trigger: il contenuto contiene `[Verse]`, `[Chorus]` o marcatori simili, oppure ha una struttura multi-linea.

### Modalità 4: Separazione lyrics + prompt

Usa il campo `lyrics` per passare le lyrics direttamente, e il testo dei messaggi diventa automaticamente il prompt:

```json
{
  "messages": [
    {"role": "user", "content": "Energetic EDM with heavy bass drops"}
  ],
  "lyrics": "[Verse 1]\nFeel the rhythm in your soul\nLet the music take control\n\n[Drop]\n(instrumental break)",
  "audio_config": {
    "bpm": 128,
    "duration": 60
  }
}
```

### Modalità strumentale

Imposta `audio_config.instrumental: true`:

```json
{
  "messages": [
    {"role": "user", "content": "<prompt>Epic orchestral cinematic score, dramatic and powerful</prompt>"}
  ],
  "audio_config": {
    "instrumental": true,
    "duration": 30
  }
}
```

---

## Input audio

I file audio possono essere passati tramite messaggi multimodali (base64) per cover, repaint e altri task.

### Tipi task_type

| task_type | Descrizione | Input audio richiesto |
|---|---|---|
| `text2music` | Testo → musica (default) | Opzionale (come riferimento) |
| `cover` | Cover/style transfer | Richiede src_audio |
| `repaint` | Repaint parziale | Richiede src_audio |
| `lego` | Audio splicing | Richiede src_audio |
| `extract` | Estrazione audio | Richiede src_audio |
| `complete` | Continuazione audio | Richiede src_audio |

### Regole di routing audio

Più blocchi `input_audio` vengono mappati a parametri diversi in ordine (simile all'upload multi-immagine):

| task_type | audio[0] | audio[1] |
|---|---|---|
| `text2music` | reference_audio (riferimento stile) | - |
| `cover/repaint/lego/extract/complete` | src_audio (audio da modificare) | reference_audio (riferimento stile opzionale) |

### Esempi di input audio

**Task cover:**

```json
{
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "<prompt>Jazz style cover with saxophone</prompt>"},
        {
          "type": "input_audio",
          "input_audio": {"data": "<base64 source audio>", "format": "mp3"}
        }
      ]
    }
  ],
  "task_type": "cover",
  "audio_cover_strength": 0.8,
  "audio_config": {"duration": 30}
}
```

**Task repaint:**

```json
{
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "<prompt>Replace with guitar solo</prompt>"},
        {
          "type": "input_audio",
          "input_audio": {"data": "<base64 source audio>", "format": "mp3"}
        }
      ]
    }
  ],
  "task_type": "repaint",
  "repainting_start": 10.0,
  "repainting_end": 20.0,
  "audio_config": {"duration": 30}
}
```

---

## Risposte in streaming

Imposta `"stream": true` per abilitare lo streaming SSE (Server-Sent Events).

### Formato evento

Ogni evento inizia con `data: `, seguito da JSON, termina con doppia newline `\n\n`:

```
data: {"id":"chatcmpl-xxx","object":"chat.completion.chunk","created":1706688000,"model":"acestep/acestep-v15-turbo","choices":[{"index":0,"delta":{...},"finish_reason":null}]}

```

### Sequenza eventi streaming

| Fase | Contenuto delta | Descrizione |
|---|---|---|
| 1. Inizializzazione | `{"role":"assistant","content":"Generating music"}` | Stabilisce la connessione |
| 2. Heartbeat | `{"content":"."}` | Inviato ogni 2 secondi durante la generazione per tenere viva la connessione |
| 3. Contenuto LM | `{"content":"## Metadata\n..."}` | Metadati e lyrics dopo il completamento |
| 4. Dati audio | `{"audio":[{"type":"audio_url","audio_url":{"url":"data:..."}}]}` | Dati audio base64 |
| 5. Fine | `finish_reason: "stop"` | Generazione completata |
| 6. Terminazione | `data: [DONE]` | Marker fine stream |

### Esempio risposta streaming

```
data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1706688000,"model":"acemusic/acestep-v1.5-turbo","choices":[{"index":0,"delta":{"role":"assistant","content":""},"finish_reason":null}]}

data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1706688000,"model":"acemusic/acestep-v1.5-turbo","choices":[{"index":0,"delta":{"content":"\n\n## Metadata\n**Caption:** Upbeat pop\n**BPM:** 120"},"finish_reason":null}]}

data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1706688000,"model":"acemusic/acestep-v1.5-turbo","choices":[{"index":0,"delta":{"content":"."},"finish_reason":null}]}

data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1706688000,"model":"acemusic/acestep-v1.5-turbo","choices":[{"index":0,"delta":{"audio":[{"type":"audio_url","audio_url":{"url":"data:audio/mpeg;base64,..."}}]},"finish_reason":null}]}

data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1706688000,"model":"acemusic/acestep-v1.5-turbo","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}

data: [DONE]

```

### Gestione streaming lato client

```python
import json
import httpx

with httpx.stream("POST", "http://127.0.0.1:8002/v1/chat/completions", json={
    "messages": [{"role": "user", "content": "Generate a cheerful guitar piece"}],
    "sample_mode": True,
    "stream": True,
    "audio_config": {"instrumental": True}
}) as response:
    content_parts = []
    audio_url = None

    for line in response.iter_lines():
        if not line or not line.startswith("data: "):
            continue
        if line == "data: [DONE]":
            break

        chunk = json.loads(line[6:])
        delta = chunk["choices"][0]["delta"]

        if "content" in delta and delta["content"]:
            content_parts.append(delta["content"])

        if "audio" in delta and delta["audio"]:
            audio_url = delta["audio"][0]["audio_url"]["url"]

        if chunk["choices"][0].get("finish_reason") == "stop":
            print("Generazione completata!")

    print("Content:", "".join(content_parts))
    if audio_url:
        import base64
        b64_data = audio_url.split(",", 1)[1]
        with open("output.mp3", "wb") as f:
            f.write(base64.b64decode(b64_data))
```

```javascript
const response = await fetch("http://127.0.0.1:8002/v1/chat/completions", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    messages: [{ role: "user", content: "Generate a cheerful guitar piece" }],
    sample_mode: true,
    stream: true,
    audio_config: { instrumental: true }
  })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();
let audioUrl = null;
let content = "";

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  const text = decoder.decode(value);
  for (const line of text.split("\n")) {
    if (!line.startsWith("data: ") || line === "data: [DONE]") continue;

    const chunk = JSON.parse(line.slice(6));
    const delta = chunk.choices[0].delta;

    if (delta.content) content += delta.content;
    if (delta.audio) audioUrl = delta.audio[0].audio_url.url;
  }
}

// audioUrl può essere usato direttamente come <audio src="...">
```

---

## Esempi

### Esempio 1: Generazione in linguaggio naturale (uso più semplice)

```bash
curl -X POST http://127.0.0.1:8002/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "A soft folk song about hometown and memories"}
    ],
    "sample_mode": true,
    "audio_config": {"vocal_language": "en"}
  }'
```

### Esempio 2: Modalità tag con parametri specifici

```bash
curl -X POST http://127.0.0.1:8002/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "<prompt>Energetic EDM track with heavy bass drops and synth leads</prompt><lyrics>[Verse 1]\nFeel the rhythm in your soul\nLet the music take control\n\n[Drop]\n(instrumental break)</lyrics>"
      }
    ],
    "audio_config": {
      "bpm": 128,
      "duration": 60,
      "vocal_language": "en"
    }
  }'
```

### Esempio 3: Strumentale con LM enhancement disabilitato

```bash
curl -X POST http://127.0.0.1:8002/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "<prompt>Peaceful piano solo, slow tempo, jazz harmony</prompt>"
      }
    ],
    "use_cot_caption": false,
    "audio_config": {
      "instrumental": true,
      "duration": 45
    }
  }'
```

### Esempio 4: Richiesta streaming

```bash
curl -X POST http://127.0.0.1:8002/v1/chat/completions \
  -H "Content-Type: application/json" \
  -N \
  -d '{
    "messages": [
      {"role": "user", "content": "Generate a happy birthday song"}
    ],
    "sample_mode": true,
    "stream": true
  }'
```

### Esempio 5: Generazione batch multi-seed

```bash
curl -X POST http://127.0.0.1:8002/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "<prompt>Lo-fi hip hop beat</prompt>"}
    ],
    "batch_size": 3,
    "seed": "42,123,456",
    "audio_config": {
      "instrumental": true,
      "duration": 30
    }
  }'
```

---

## Codici di errore

| HTTP Status | Descrizione |
|---|---|
| 400 | Formato richiesta non valido o input mancante/errato |
| 401 | Chiave API mancante o non valida |
| 429 | Servizio occupato, coda piena |
| 500 | Errore interno durante la generazione musicale |
| 503 | Modello non ancora inizializzato |
| 504 | Timeout generazione |

Formato risposta errore:

```json
{
  "detail": "Messaggio descrittivo dell'errore"
}
```

---

## Configurazione server (variabili d'ambiente)

Le seguenti variabili d'ambiente possono configurare il server (riferimento operativo):

| Variabile | Default | Descrizione |
|---|---|---|
| `OPENROUTER_API_KEY` | None | Chiave API autenticazione |
| `OPENROUTER_HOST` | `127.0.0.1` | Indirizzo di ascolto |
| `OPENROUTER_PORT` | `8002` | Porta di ascolto |
| `ACESTEP_CONFIG_PATH` | `acestep-v15-turbo` | Percorso configurazione modello DiT |
| `ACESTEP_DEVICE` | `auto` | Dispositivo di inferenza |
| `ACESTEP_LM_MODEL_PATH` | `acestep-5Hz-lm-0.6B` | Percorso modello LLM |
| `ACESTEP_LM_BACKEND` | `vllm` | Backend inferenza LLM |
| `ACESTEP_QUEUE_MAXSIZE` | `200` | Capienza massima coda task |
| `ACESTEP_GENERATION_TIMEOUT` | `600` | Timeout richiesta non streaming (secondi) |
