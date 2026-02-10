# Guida all'installazione di ACE-Step 1.5

**Lingua / 语言 / 言語 / Lingua:** [English](../en/INSTALL.md) | [中文](../zh/INSTALL.md) | [日本語](../ja/INSTALL.md) | [Italiano](INSTALL.md)

---

## Indice

- [Requisiti](#requisiti)
- [Avvio rapido (tutte le piattaforme)](#avvio-rapido-tutte-le-piattaforme)
- [Pacchetto portatile Windows](#-pacchetto-portatile-windows)
- [GPU AMD / ROCm](#gpu-amd--rocm)
- [GPU Intel](#gpu-intel)
- [Modalità solo CPU](#modalità-solo-cpu)
- [Note Linux](#note-linux)
- [Variabili d'ambiente (.env)](#variabili-dambiente-env)
- [Opzioni da riga di comando](#opzioni-da-riga-di-comando)
- [Download modelli](#-download-modelli)
- [Quale modello scegliere?](#-quale-modello-scegliere)
- [Sviluppo](#sviluppo)

---

## Requisiti

| Elemento | Requisito |
|------|-------------|
| Python | 3.11+ (release stabile, non pre-release) |
| GPU | Consigliata CUDA; supportati anche MPS / ROCm / Intel XPU / CPU |
| VRAM | ≥4GB per modalità solo DiT; ≥6GB per LLM+DiT |
| Disco | ~10GB per i modelli principali |

---

## Avvio rapido (tutte le piattaforme)

### 1. Installa uv (Package Manager)

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clona e installa

```bash
git clone https://github.com/ACE-Step/ACE-Step-1.5.git
cd ACE-Step-1.5
uv sync
```

### 3. Avvia

**Gradio Web UI (consigliato):**

```bash
uv run acestep
```

**Server REST API:**

```bash
uv run acestep-api
```

**Usando Python direttamente** (Conda / venv / system Python):

```bash
# Attiva prima l'ambiente, poi:
python acestep/acestep_v15_pipeline.py          # Gradio UI
python acestep/api_server.py                     # REST API
```

> I modelli vengono scaricati automaticamente al primo avvio. Apri http://localhost:7860 (Gradio) oppure http://localhost:8001 (API).

---

## 🪟 Pacchetto portatile Windows

Per utenti Windows, forniamo un pacchetto portatile con dipendenze pre-installate:

1. Scarica ed estrai: [ACE-Step-1.5.7z](https://files.acemusic.ai/acemusic/win/ACE-Step-1.5.7z)
2. Il pacchetto include `python_embeded` con tutte le dipendenze pre-installate
3. **Requisiti:** CUDA 12.8

### Script di avvio rapido

| Script | Descrizione |
|--------|-------------|
| `start_gradio_ui.bat` | Avvia Gradio Web UI |
| `start_api_server.bat` | Avvia server REST API |

Entrambi gli script supportano rilevamento ambiente, installazione automatica di `uv`, sorgente download configurabile, controllo aggiornamenti Git opzionale e modelli/parametri personalizzabili.

### Configurazione

**`start_gradio_ui.bat`:**

```batch
REM Lingua UI (en, zh, he, ja)
set LANGUAGE=zh

REM Sorgente download (auto, huggingface, modelscope)
set DOWNLOAD_SOURCE=--download-source modelscope

REM Controllo aggiornamenti Git (true/false)
set CHECK_UPDATE=true

REM Configurazione modelli
set CONFIG_PATH=--config_path acestep-v15-turbo
set LM_MODEL_PATH=--lm_model_path acestep-5Hz-lm-1.7B
```

**`start_api_server.bat`:**

```batch
REM Inizializzazione LLM via variabile d'ambiente
REM set ACESTEP_INIT_LLM=true   # Forza abilitazione LLM
REM set ACESTEP_INIT_LLM=false  # Forza disabilitazione LLM (modalità solo DiT)
```

### Aggiornamento e manutenzione

| Script | Scopo |
|--------|---------|
| `check_update.bat` | Controlla e aggiorna da GitHub |
| `merge_config.bat` | Unisce le configurazioni salvate dopo l'aggiornamento |
| `install_uv.bat` | Installa il package manager uv |
| `quick_test.bat` | Testa la configurazione ambiente |
| `test_git_update.bat` | Testa la funzionalità di update Git |

**Workflow di aggiornamento:**

```bash
check_update.bat          # 1. Controlla aggiornamenti (richiede PortableGit/)
merge_config.bat          # 2. Unisci le impostazioni se ci sono conflitti
```

### Supporto Portable Git

Posiziona una cartella `PortableGit/` nel pacchetto per abilitare gli auto-aggiornamenti:

```batch
set CHECK_UPDATE=true     # in start_gradio_ui.bat o start_api_server.bat
```

Funzionalità: timeout 10s, rilevamento conflitti intelligente e backup, rollback automatico in caso di fallimento, struttura directory preservata nei backup.

### Priorità rilevamento ambiente

1. `python_embeded\python.exe` (se esiste)
2. `uv run acestep` (se uv è installato)
3. Installazione automatica di uv via winget o PowerShell

---

## GPU AMD / ROCm

> ⚠️ `uv run acestep` installa wheel PyTorch CUDA e potrebbe sovrascrivere un setup ROCm esistente.

### Workflow consigliato

```bash
# 1. Crea e attiva un ambiente virtuale
python -m venv .venv
source .venv/bin/activate

# 2. Installa PyTorch compatibile ROCm
pip install torch --index-url https://download.pytorch.org/whl/rocm6.0

# 3. Installa ACE-Step
pip install -e .

# 4. Avvia il servizio
python -m acestep.acestep_v15_pipeline --port 7680
```

Su Windows, usa `.venv\Scripts\activate` e gli stessi passaggi.

### Risoluzione problemi di rilevamento GPU

Se vedi "Nessuna GPU rilevata, in esecuzione su CPU" con GPU AMD:

1. Esegui lo strumento diagnostico: `python scripts/check_gpu.py`
2. Per GPU RDNA3, imposta `HSA_OVERRIDE_GFX_VERSION`:

| GPU | Valore |
|-----|-------|
| RX 7900 XT/XTX, RX 9070 XT | `export HSA_OVERRIDE_GFX_VERSION=11.0.0` |
| RX 7800 XT, RX 7700 XT | `export HSA_OVERRIDE_GFX_VERSION=11.0.1` |
| RX 7600 | `export HSA_OVERRIDE_GFX_VERSION=11.0.2` |

3. Su Windows, usa `start_gradio_ui_rocm.bat` che imposta automaticamente le variabili richieste.
4. Verifica l'installazione ROCm: `rocm-smi` dovrebbe elencare la tua GPU.

### Linux (cachy-os / RDNA4)

Vedi [ACE-Step1.5-Rocm-Manual-Linux.md](ACE-Step1.5-Rocm-Manual-Linux.md) per un manuale ROCm dettagliato testato con RDNA4 su cachy-os.

---

## GPU Intel

| Elemento | Dettaglio |
|------|--------|
| Dispositivo testato | Laptop Windows con grafica integrata Ultra 9 285H |
| Offload | Disabilitato di default |
| Compile & Quantization | Abilitati di default |
| Inferenza LLM | Supportata (testata con `acestep-5Hz-lm-0.6B`) |
| Accelerazione nanovllm | NON supportata su GPU Intel |
| Ambiente di test | PyTorch 2.8.0 da [Intel Extension for PyTorch](https://pytorch-extension.intel.com/?request=platform) |

> Nota: la velocità di inferenza LLM può diminuire quando si genera audio oltre 2 minuti. Le GPU discrete Intel sono attese ma non ancora testate.

---

## Modalità solo CPU

ACE-Step può girare su CPU per **sola inferenza**, ma le prestazioni saranno molto inferiori.

- L'addestramento (incluso LoRA) su CPU **non è consigliato**.
- Per sistemi con poca VRAM, è supportata la modalità solo DiT (LLM disabilitato).

Se non hai una GPU, considera:
- Usare provider cloud GPU
- Eseguire workflow di sola inferenza
- Usare modalità solo DiT con `ACESTEP_INIT_LLM=false`

---

## Note Linux

### Problema Python 3.11 Pre-Release

Alcune distribuzioni Linux (incluso Ubuntu) includono Python 3.11.0rc1, una build **pre-release**. Questo può causare segmentation fault con il backend vLLM.

**Raccomandazione:** usa una release stabile di Python (≥ 3.11.12). Su Ubuntu, installa tramite PPA deadsnakes.

Se non puoi aggiornare Python, usa il backend PyTorch:

```bash
uv run acestep --backend pt
```

---

## Variabili d'ambiente (.env)

```bash
cp .env.example .env   # Copia e modifica
```

### Variabili chiave

| Variabile | Valori | Descrizione |
|----------|--------|-------------|
| `ACESTEP_INIT_LLM` | `auto` / `true` / `false` | Modalità inizializzazione LLM |
| `ACESTEP_CONFIG_PATH` | nome modello | Percorso modello DiT |
| `ACESTEP_LM_MODEL_PATH` | nome modello | Percorso modello LM |
| `ACESTEP_DOWNLOAD_SOURCE` | `auto` / `huggingface` / `modelscope` | Sorgente download |
| `ACESTEP_API_KEY` | string | Chiave API per autenticazione |

### Inizializzazione LLM (`ACESTEP_INIT_LLM`)

Flusso: `Rilevamento GPU → Override ACESTEP_INIT_LLM → Caricamento modelli`

| Valore | Comportamento |
|-------|----------|
| `auto` (o vuoto) | Usa il risultato del rilevamento GPU (consigliato) |
| `true` / `1` / `yes` | Forza abilita LLM dopo rilevamento GPU (può causare OOM) |
| `false` / `0` / `no` | Forza disabilita per modalità solo DiT |

**Esempio `.env` per scenari diversi:**

```bash
# Modalità auto (consigliata)
ACESTEP_INIT_LLM=auto

# Forza abilita su GPU con poca VRAM
ACESTEP_INIT_LLM=true
ACESTEP_LM_MODEL_PATH=acestep-5Hz-lm-0.6B

# Forza disabilita LLM per generazione più veloce
ACESTEP_INIT_LLM=false
```

---

## Opzioni da riga di comando

### Gradio UI (`acestep`)

| Opzione | Default | Descrizione |
|--------|---------|-------------|
| `--port` | 7860 | Porta server |
| `--server-name` | 127.0.0.1 | Indirizzo server (usa `0.0.0.0` per accesso rete) |
| `--share` | false | Crea link pubblico Gradio |
| `--language` | en | Lingua UI: `en`, `zh`, `he`, `ja` |
| `--init_service` | false | Auto-inizializza modelli all'avvio |
| `--init_llm` | auto | Init LLM: `true` / `false` / omesso per auto |
| `--config_path` | auto | Modello DiT (es. `acestep-v15-turbo`) |
| `--lm_model_path` | auto | Modello LM (es. `acestep-5Hz-lm-1.7B`) |
| `--offload_to_cpu` | auto | CPU offload (auto se VRAM < 16GB) |
| `--download-source` | auto | Sorgente modelli: `auto` / `huggingface` / `modelscope` |
| `--enable-api` | false | Abilita REST API insieme alla Gradio UI |
| `--api-key` | none | Chiave API per autenticazione |
| `--auth-username` | none | Username autenticazione Gradio |
| `--auth-password` | none | Password autenticazione Gradio |

**Esempi:**

```bash
# Accesso pubblico con UI cinese
uv run acestep --server-name 0.0.0.0 --share --language zh

# Pre-inizializza modelli all'avvio
uv run acestep --init_service true --config_path acestep-v15-turbo

# Abilita endpoint API con autenticazione
uv run acestep --enable-api --api-key sk-your-secret-key --port 8001

# Usa ModelScope come sorgente download
uv run acestep --download-source modelscope
```

---

## 📥 Download modelli

I modelli vengono scaricati automaticamente da [HuggingFace](https://huggingface.co/ACE-Step/Ace-Step1.5) o [ModelScope](https://modelscope.cn/organization/ACE-Step) al primo avvio.

### Download da CLI

```bash
uv run acestep-download                              # Scarica modello principale
uv run acestep-download --all                         # Scarica tutti i modelli
uv run acestep-download --download-source modelscope  # Da ModelScope
uv run acestep-download --model acestep-v15-sft       # Modello specifico
uv run acestep-download --list                        # Lista di tutti i modelli disponibili
```

Oppure con Python direttamente:

```bash
python -m acestep.model_downloader                    # Scarica modello principale
python -m acestep.model_downloader --all              # Scarica tutti i modelli
```

### Download manuale (huggingface-cli)

```bash
# Modello principale (vae, Qwen3-Embedding-0.6B, acestep-v15-turbo, acestep-5Hz-lm-1.7B)
huggingface-cli download ACE-Step/Ace-Step1.5 --local-dir ./checkpoints

# Modelli opzionali
huggingface-cli download ACE-Step/acestep-5Hz-lm-0.6B --local-dir ./checkpoints/acestep-5Hz-lm-0.6B
huggingface-cli download ACE-Step/acestep-5Hz-lm-4B --local-dir ./checkpoints/acestep-5Hz-lm-4B
```

### Modelli disponibili

| Modello | Descrizione | HuggingFace |
|-------|-------------|-------------|
| **Ace-Step1.5** (Principale) | Core: vae, Qwen3-Embedding-0.6B, acestep-v15-turbo, acestep-5Hz-lm-1.7B | [Link](https://huggingface.co/ACE-Step/Ace-Step1.5) |
| acestep-5Hz-lm-0.6B | LM leggero (0.6B parametri) | [Link](https://huggingface.co/ACE-Step/acestep-5Hz-lm-0.6B) |
| acestep-5Hz-lm-4B | LM grande (4B parametri) | [Link](https://huggingface.co/ACE-Step/acestep-5Hz-lm-4B) |
| acestep-v15-base | Modello DiT base | [Link](https://huggingface.co/ACE-Step/acestep-v15-base) |
| acestep-v15-sft | Modello DiT SFT | [Link](https://huggingface.co/ACE-Step/acestep-v15-sft) |
| acestep-v15-turbo-shift1 | DiT turbo con shift1 | [Link](https://huggingface.co/ACE-Step/acestep-v15-turbo-shift1) |
| acestep-v15-turbo-shift3 | DiT turbo con shift3 | [Link](https://huggingface.co/ACE-Step/acestep-v15-turbo-shift3) |
| acestep-v15-turbo-continuous | DiT turbo con shift continuo (1-5) | [Link](https://huggingface.co/ACE-Step/acestep-v15-turbo-continuous) |

---

## 💡 Quale modello scegliere?

ACE-Step si adatta automaticamente alla VRAM della GPU:

| VRAM GPU | Modello LM consigliato | Note |
|---------------|---------------------|-------|
| **≤6GB** | Nessuno (solo DiT) | LM disabilitato per risparmiare memoria |
| **6-12GB** | `acestep-5Hz-lm-0.6B` | Leggero, buon equilibrio |
| **12-16GB** | `acestep-5Hz-lm-1.7B` | Qualità migliore |
| **≥16GB** | `acestep-5Hz-lm-4B` | Migliore qualità e audio understanding |

> 📖 Per dettagli sulla compatibilità GPU (limiti durata, batch, ottimizzazione memoria), vedi [Guida alla compatibilità GPU](GPU_COMPATIBILITY.md).

---

## Sviluppo

```bash
# Aggiungi dipendenze
uv add package-name
uv add --dev package-name

# Aggiorna tutte le dipendenze
uv sync --upgrade
```
