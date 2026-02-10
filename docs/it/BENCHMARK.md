# Guida ai benchmark e al profiling di ACE-Step 1.5

**Lingua / 语言:** [English](../en/BENCHMARK.md) | [中文](../zh/BENCHMARK.md)

---

## Indice

- [Panoramica](#panoramica)
- [Avvio rapido](#avvio-rapido)
- [Modalità di profiling](#modalità-di-profiling)
- [Riferimento CLI](#riferimento-cli)
- [Esempi](#esempi)
- [Comprendere l'output](#comprendere-loutput)
- [Suggerimenti e buone pratiche](#suggerimenti-e-buone-pratiche)

---

## Panoramica

`profile_inference.py` è uno strumento completo di profiling e benchmarking per l'inferenza di ACE-Step 1.5. Misura il tempo totale end-to-end, il tempo di pianificazione LLM, il tempo di diffusione DiT, il tempo di decodifica VAE e altro ancora, su diversi dispositivi, backend e configurazioni.

### Modalità supportate

| Modalità | Descrizione |
|------|-------------|
| `profile` | Profilo di una singola generazione con dettaglio dei tempi |
| `benchmark` | Esegue una matrice di configurazioni (durata × batch × thinking × step) e produce una tabella riassuntiva |
| `understand` | Profilo della API `understand_music()` (audio → estrazione metadati) |
| `create_sample` | Profilo della API `create_sample()` (ispirazione / modalità semplice) |
| `format_sample` | Profilo della API `format_sample()` (caption + lyrics → metadati strutturati) |

### Dispositivi e backend supportati

| Dispositivo | Flag | Note |
|--------|------|-------|
| CUDA (NVIDIA) | `--device cuda` | Consigliato. Rilevato automaticamente per default |
| MPS (Apple Silicon) | `--device mps` | macOS con Apple Silicon |
| CPU | `--device cpu` | Lento, solo per test |
| Auto | `--device auto` | Seleziona automaticamente il migliore (default) |

| Backend LLM | Flag | Note |
|-------------|------|-------|
| vLLM | `--lm-backend vllm` | Più veloce su CUDA, consigliato per NVIDIA |
| PyTorch | `--lm-backend pt` | Fallback universale, funziona ovunque |
| MLX | `--lm-backend mlx` | Ottimizzato per Apple Silicon |
| Auto | `--lm-backend auto` | Seleziona il backend migliore per il dispositivo (default) |

---

## Avvio rapido

```bash
# Profilo base (text2music, impostazioni predefinite)
python profile_inference.py

# Profilo con thinking LLM abilitato
python profile_inference.py --thinking

# Esegui la matrice di benchmark
python profile_inference.py --mode benchmark

# Profilo su Apple Silicon
python profile_inference.py --device mps --lm-backend mlx

# Profilo con analisi a livello di funzione tramite cProfile
python profile_inference.py --detailed
```

---

## Modalità di profiling

### 1. `profile` — Profilo di una singola esecuzione

Esegue una singola generazione con dettaglio dei tempi. Include warmup opzionale e cProfile.

```bash
python profile_inference.py --mode profile
```

**Cosa misura:**
- Tempo totale (end-to-end)
- Tempo di pianificazione LLM (generazione token, decoding vincolato, overhead CFG)
- Tempo di diffusione DiT (per step e totale)
- Tempo di decodifica VAE
- Tempo di salvataggio audio

**Opzioni per questa modalità:**

| Flag | Descrizione |
|------|-------------|
| `--no-warmup` | Salta il warmup (include overhead di compilazione nelle misure) |
| `--detailed` | Abilita l'analisi a livello di funzione con `cProfile` |
| `--llm-debug` | Debug LLM approfondito (conteggio token, throughput) |
| `--thinking` | Abilita il ragionamento Chain-of-Thought dell'LLM |
| `--duration <sec>` | Sovrascrive la durata audio |
| `--batch-size <n>` | Sovrascrive la dimensione del batch |
| `--inference-steps <n>` | Sovrascrive gli step di diffusione |

### 2. `benchmark` — Matrice di configurazioni

Esegue una matrice di configurazioni e produce una tabella riassuntiva. Si adatta automaticamente ai limiti di memoria GPU.

```bash
python profile_inference.py --mode benchmark
```

**Matrice predefinita:**
- Durate: 30s, 60s, 120s, 240s (limitato dalla memoria GPU)
- Batch: 1, 2, 4 (limitato dalla memoria GPU)
- Thinking: True, False
- Step di inferenza: 8, 16

**Esempio di output:**

```
Duration   Batch   Think   Steps   Wall(s)    LM(s)      DiT(s)     VAE(s)     Status
--------------------------------------------------------------------------------------------------------------------------
30         1       False   8       3.21       0.45       1.89       0.52       OK
30         1       True    8       5.67       2.91       1.89       0.52       OK
60         2       False   16      12.34      0.48       9.12       1.85       OK
...
```

**Salva i risultati in JSON:**

```bash
python profile_inference.py --mode benchmark --benchmark-output results.json
```

### 3. `understand` — Profiling di audio understanding

Profilo della API `understand_music()` che estrae metadati (BPM, tonalità, metrica, caption) dai codici audio.

```bash
python profile_inference.py --mode understand
python profile_inference.py --mode understand --audio-codes "your_audio_codes_string"
```

### 4. `create_sample` — Profiling modalità ispirazione

Profilo della API `create_sample()` che genera un blueprint completo di canzone da una semplice query testuale.

```bash
python profile_inference.py --mode create_sample
python profile_inference.py --mode create_sample --sample-query "a soft Bengali love song"
python profile_inference.py --mode create_sample --instrumental
```

### 5. `format_sample` — Profiling formattazione metadati

Profilo della API `format_sample()` che converte caption + lyrics in metadati strutturati.

```bash
python profile_inference.py --mode format_sample
```

---

## Riferimento CLI

### Dispositivo e backend

| Flag | Default | Descrizione |
|------|---------|-------------|
| `--device` | `auto` | Dispositivo: `auto` / `cuda` / `mps` / `cpu` |
| `--lm-backend` | `auto` | Backend LLM: `auto` / `vllm` / `pt` / `mlx` |

### Percorsi modello

| Flag | Default | Descrizione |
|------|---------|-------------|
| `--config-path` | `acestep-v15-turbo` | Config DiT |
| `--lm-model` | `acestep-5Hz-lm-1.7B` | Percorso modello LLM |

### Opzioni hardware

| Flag | Default | Descrizione |
|------|---------|-------------|
| `--offload-to-cpu` | off | Scarica i modelli sulla CPU quando non in uso |
| `--offload-dit-to-cpu` | off | Scarica il DiT sulla CPU quando non in uso |
| `--quantization` | none | Quantizzazione: `int8_weight_only` / `fp8_weight_only` / `w8a8_dynamic` |

### Parametri di generazione

| Flag | Default | Descrizione |
|------|---------|-------------|
| `--duration` | dall'esempio | Durata audio in secondi |
| `--batch-size` | dall'esempio | Dimensione batch |
| `--inference-steps` | dall'esempio | Step di inferenza della diffusione |
| `--seed` | dall'esempio | Seed casuale |
| `--guidance-scale` | 7.0 | Scala di guidance CFG per il DiT |

### Parametri LLM / CoT

| Flag | Default | Descrizione |
|------|---------|-------------|
| `--thinking` | off | Abilita il ragionamento Chain-of-Thought dell'LLM |
| `--use-cot-metas` | off | LLM genera metadati musicali via CoT |
| `--use-cot-caption` | off | LLM riscrive/formatta la caption via CoT |
| `--use-cot-language` | off | LLM rileva la lingua vocale via CoT |
| `--use-constrained-decoding` | on | Decoding vincolato basato su FSM |
| `--no-constrained-decoding` | — | Disabilita il decoding vincolato |
| `--lm-temperature` | 0.85 | Temperatura di campionamento LLM |
| `--lm-cfg-scale` | 2.0 | Scala CFG LLM |

### Opzioni di profiling

| Flag | Default | Descrizione |
|------|---------|-------------|
| `--mode` | `profile` | Modalità: `profile` / `benchmark` / `understand` / `create_sample` / `format_sample` |
| `--no-warmup` | off | Salta il warmup |
| `--detailed` | off | Abilita l'analisi a livello di funzione con `cProfile` |
| `--llm-debug` | off | Debug LLM approfondito (conteggio token, throughput) |
| `--benchmark-output` | none | Salva i risultati del benchmark in un file JSON |

### Opzioni di input

| Flag | Default | Descrizione |
|------|---------|-------------|
| `--example` | `example_05.json` | Esempio JSON da `examples/text2music/` |
| `--task-type` | `text2music` | Task: `text2music` / `cover` / `repaint` / `lego` / `extract` / `complete` |
| `--reference-audio` | none | Percorso audio di riferimento (per cover/style transfer) |
| `--src-audio` | none | Percorso audio sorgente (per audio-to-audio) |
| `--sample-query` | none | Query per la modalità `create_sample` |
| `--instrumental` | off | Genera musica strumentale (per `create_sample`) |
| `--audio-codes` | none | Stringa di codici audio (per modalità `understand`) |

---

## Esempi

### Confronto dispositivi

```bash
# GPU NVIDIA
python profile_inference.py --device cuda --lm-backend vllm

# Apple Silicon
python profile_inference.py --device mps --lm-backend mlx

# Baseline CPU
python profile_inference.py --device cpu --lm-backend pt
```

### Confronto modelli LLM

```bash
# Leggero (0.6B)
python profile_inference.py --lm-model acestep-5Hz-lm-0.6B

# Default (1.7B)
python profile_inference.py --lm-model acestep-5Hz-lm-1.7B

# Grande (4B)
python profile_inference.py --lm-model acestep-5Hz-lm-4B
```

### Thinking vs senza thinking

```bash
# Senza thinking (più veloce)
python profile_inference.py --mode benchmark

# Con thinking (qualità migliore, più lento)
python profile_inference.py --thinking --use-cot-metas --use-cot-caption
```

### Profiling con poca VRAM

```bash
# Offload + quantizzazione
python profile_inference.py --offload-to-cpu --quantization int8_weight_only --lm-model acestep-5Hz-lm-0.6B
```

### Suite completa di benchmark

```bash
# Esegui l'intera matrice e salva i risultati
python profile_inference.py --mode benchmark --benchmark-output benchmark_results.json

# Poi ispeziona il JSON
cat benchmark_results.json | python -m json.tool
```

### Profiling a livello di funzione

```bash
# Abilita cProfile per analisi dettagliata a livello di funzione
python profile_inference.py --detailed --llm-debug
```

---

## Comprendere l'output

### Dettaglio costi temporali

Il profiler stampa una scomposizione dettagliata di dove viene speso il tempo:

```
TIME COSTS BREAKDOWN
====================================================================================================
  Component                          Time (s)       % of Total
  ─────────────────────────────────────────────────────────────
  LLM Planning (total)               2.91           45.2%
    ├─ Token generation              2.45           38.1%
    ├─ Constrained decoding          0.31            4.8%
    └─ CFG overhead                  0.15            2.3%
  DiT Diffusion (total)              1.89           29.4%
    ├─ Per-step average              0.24            —
    └─ Steps                         8               —
  VAE Decode                         0.52            8.1%
  Audio Save                         0.12            1.9%
  Other / Overhead                   0.99           15.4%
  ─────────────────────────────────────────────────────────────
  Wall Time (total)                  6.43          100.0%
```

### Metriche chiave

| Metrica | Descrizione |
|--------|-------------|
| **Wall Time** | Tempo end-to-end dall'inizio alla fine |
| **LM Total Time** | Tempo speso nella pianificazione LLM (generazione token + parsing) |
| **DiT Total Time** | Tempo speso nella diffusione (tutti gli step) |
| **VAE Decode Time** | Tempo per decodificare i latenti in forma d'onda audio |
| **Tokens/sec** | Throughput di generazione token LLM (con `--llm-debug`) |

---

## Suggerimenti e buone pratiche

1. **Includi sempre il warmup** (predefinito) — La prima esecuzione include overhead di compilazione JIT e allocazione memoria. Il warmup assicura misure di performance a regime.

2. **Usa `--benchmark-output`** per salvare i risultati in JSON e analizzarli o confrontarli in seguito.

3. **Confronta thinking off vs on** — La modalità thinking aumenta significativamente il tempo LLM ma può migliorare la qualità.

4. **Testa con durate rappresentative** — Durate brevi (30s) sono dominate dal tempo LLM; durate lunghe (240s+) dal tempo DiT.

5. **Adattamento automatico della memoria GPU** — La modalità benchmark limita automaticamente durate e batch in base alla GPU.

6. **Usa `--detailed` con parsimonia** — `cProfile` aggiunge overhead; usalo solo per investigare colli di bottiglia a livello di funzione.
