# Guida alla risoluzione dei problemi di rilevamento GPU

Questa guida aiuta a risolvere gli errori "Nessuna GPU rilevata, in esecuzione su CPU".

## Diagnostica rapida

Esegui lo strumento di diagnostica per identificare il problema:

```bash
python scripts/check_gpu.py
```

Questo controlla l'installazione di PyTorch, la disponibilità della GPU e la configurazione dell'ambiente.

## Problemi comuni e soluzioni

### Problema 1: GPU AMD non rilevata (ROCm)

**Sintomi:**
- Hai una GPU AMD (serie RX 6000/7000/9000)
- ROCm è installato
- Continui a ricevere "Nessuna GPU rilevata"

**Soluzione:**

#### Per GPU RDNA3 (serie RX 7000/9000):

È necessaria la variabile d'ambiente `HSA_OVERRIDE_GFX_VERSION`:

**Linux/macOS:**
```bash
export HSA_OVERRIDE_GFX_VERSION=11.0.0  # Per RX 7900 XT/XTX, RX 9070 XT
export HSA_OVERRIDE_GFX_VERSION=11.0.1  # Per RX 7800 XT, RX 7700 XT
export HSA_OVERRIDE_GFX_VERSION=11.0.2  # Per RX 7600
```

**Windows:**
```cmd
set HSA_OVERRIDE_GFX_VERSION=11.0.0
```

Oppure usa lo script di avvio fornito che lo imposta automaticamente:
```cmd
start_gradio_ui_rocm.bat
```

#### Per GPU RDNA2 (serie RX 6000):

```bash
export HSA_OVERRIDE_GFX_VERSION=10.3.0  # Linux/macOS
set HSA_OVERRIDE_GFX_VERSION=10.3.0     # Windows
```

#### Verifica l'installazione ROCm:

```bash
# Verifica se ROCm vede la tua GPU
rocm-smi

# Verifica la build ROCm di PyTorch
python -c "import torch; print(f'ROCm: {torch.version.hip}')"
```

### Problema 2: PyTorch solo CPU installato

**Sintomi:**
- La diagnostica mostra "Build type: CPU-only"

**Soluzione:**

Devi reinstallare PyTorch con supporto GPU.

#### Per GPU AMD:

**Windows (ROCm 7.2):**
Segui le istruzioni dettagliate in `requirements-rocm.txt`:

```cmd
# 1. Installa i componenti ROCm SDK (vedi requirements-rocm.txt per gli URL completi)
pip install --no-cache-dir [ROCm SDK wheels...]

# 2. Installa PyTorch per ROCm
pip install --no-cache-dir [PyTorch ROCm wheel...]

# 3. Installa le dipendenze
pip install -r requirements-rocm.txt
```

**Linux (ROCm 6.0+):**
```bash
pip install torch --index-url https://download.pytorch.org/whl/rocm6.0
pip install -r requirements-rocm-linux.txt
```

#### Per GPU NVIDIA:

```bash
# Per CUDA 12.1 (controlla il sito PyTorch per la versione più recente)
pip install torch --index-url https://download.pytorch.org/whl/cu121
# Oppure per CUDA 12.4+:
# pip install torch --index-url https://download.pytorch.org/whl/cu124
```

> **Nota:** consulta https://pytorch.org/get-started/locally/ per l'ultima versione CUDA supportata da PyTorch.

### Problema 3: GPU NVIDIA non rilevata (CUDA)

**Sintomi:**
- Hai una GPU NVIDIA
- CUDA è installato
- Continui a ricevere "Nessuna GPU rilevata"

**Soluzione:**

1. **Controlla i driver NVIDIA:**
   ```bash
   nvidia-smi
   ```
   
   Se fallisce, installa/aggiorna i driver NVIDIA da: https://www.nvidia.com/download/index.aspx

2. **Controlla la compatibilità della versione CUDA:**
   
   La versione CUDA della build PyTorch deve essere compatibile con i driver.
   
   Controlla la versione CUDA di PyTorch:
   ```bash
   python -c "import torch; print(f'CUDA: {torch.version.cuda}')"
   ```
   
   Controlla la versione CUDA dei driver:
   ```bash
   nvidia-smi  # Cerca "CUDA Version: X.X"
   ```

3. **Reinstalla PyTorch se necessario:**
   ```bash
   pip uninstall torch torchvision torchaudio
   # Controlla https://pytorch.org/get-started/locally/ per l'ultima versione CUDA
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```

### Problema 4: Problemi di accesso GPU in WSL2

**Sintomi:**
- Stai eseguendo in WSL2 (Windows Subsystem for Linux)
- GPU non rilevata

**Soluzione:**

Per GPU NVIDIA in WSL2, serve CUDA su WSL2:
1. Installa i driver NVIDIA su Windows (non in WSL2)
2. Installa il toolkit CUDA in WSL2
3. Segui: https://docs.nvidia.com/cuda/wsl-user-guide/index.html

Per GPU AMD, il supporto ROCm in WSL2 è limitato. Valuta:
- Eseguire su Linux nativo
- Usare Windows con `start_gradio_ui_rocm.bat`

## Configurazione specifica per GPU

### RX 9070 XT (RDNA3)

```bash
# Linux/macOS
export HSA_OVERRIDE_GFX_VERSION=11.0.0
export MIOPEN_FIND_MODE=FAST

# Windows (oppure usa start_gradio_ui_rocm.bat)
set HSA_OVERRIDE_GFX_VERSION=11.0.0
set MIOPEN_FIND_MODE=FAST
```

### RX 7900 XT/XTX (RDNA3)

Come per RX 9070 XT sopra.

### RX 6900 XT (RDNA2)

```bash
# Linux/macOS
export HSA_OVERRIDE_GFX_VERSION=10.3.0

# Windows
set HSA_OVERRIDE_GFX_VERSION=10.3.0
```

## Risorse aggiuntive

- **Setup ROCm Linux:** vedi `docs/en/ACE-Step1.5-Rocm-Manual-Linux.md`
- **Setup ROCm Windows:** vedi `requirements-rocm.txt`
- **Tier GPU:** vedi `docs/en/GPU_COMPATIBILITY.md`
- **Installazione generale:** vedi `README.md`

## Problemi persistenti?

Se nessuna delle soluzioni funziona:

1. Esegui la diagnostica e salva l'output:
   ```bash
   python scripts/check_gpu.py > gpu_diagnostic.txt
   ```

2. Apri un issue su GitHub con:
   - Output diagnostico
   - Modello GPU
   - OS (Windows/Linux/macOS)
   - Versione ROCm/CUDA installata

## Riferimento variabili d'ambiente

### ROCm (GPU AMD)

| Variabile | Scopo | Esempio |
|----------|---------|---------|
| `HSA_OVERRIDE_GFX_VERSION` | Override architettura GPU | `11.0.0` (RDNA3), `10.3.0` (RDNA2) |
| `MIOPEN_FIND_MODE` | Modalità selezione kernel MIOpen | `FAST` (consigliato) |
| `TORCH_COMPILE_BACKEND` | Backend di compilazione PyTorch | `eager` (ROCm Windows) |
| `ACESTEP_LM_BACKEND` | Backend del language model | `pt` (consigliato per ROCm) |

### CUDA (GPU NVIDIA)

| Variabile | Scopo | Esempio |
|----------|---------|---------|
| `CUDA_VISIBLE_DEVICES` | Seleziona quale GPU usare | `0` (prima GPU) |

### Specifiche ACE-Step

| Variabile | Scopo | Esempio |
|----------|---------|---------|
| `MAX_CUDA_VRAM` | Override VRAM rilevata (test) | `8` (simula GPU 8GB) |
