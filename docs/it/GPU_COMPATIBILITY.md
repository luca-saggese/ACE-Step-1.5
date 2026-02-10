# Guida alla compatibilità GPU

ACE-Step 1.5 si adatta automaticamente alla VRAM disponibile sulla tua GPU, regolando i limiti di generazione e la disponibilità dei modelli LM. Il sistema rileva la memoria GPU all'avvio e configura le impostazioni ottimali.

## Configurazione per tier GPU

| VRAM | Tier | Modalità LM | Durata max | Batch max | Allocazione memoria LM |
|------|------|---------|--------------|----------------|---------------------|
| ≤4GB | Tier 1 | Non disponibile | 3 min | 1 | - |
| 4-6GB | Tier 2 | Non disponibile | 6 min | 1 | - |
| 6-8GB | Tier 3 | 0.6B (opzionale) | Con LM: 4 min / Senza: 6 min | Con LM: 1 / Senza: 2 | 3GB |
| 8-12GB | Tier 4 | 0.6B (opzionale) | Con LM: 4 min / Senza: 6 min | Con LM: 2 / Senza: 4 | 3GB |
| 12-16GB | Tier 5 | 0.6B / 1.7B | Con LM: 4 min / Senza: 6 min | Con LM: 2 / Senza: 4 | 0.6B: 3GB, 1.7B: 8GB |
| 16-24GB | Tier 6 | 0.6B / 1.7B / 4B | 8 min | Con LM: 4 / Senza: 8 | 0.6B: 3GB, 1.7B: 8GB, 4B: 12GB |
| ≥24GB | Illimitato | Tutti i modelli | 10 min | 8 | Senza limiti |

## Note

- **Impostazioni predefinite** configurate automaticamente in base alla memoria GPU rilevata
- **Modalità LM** si riferisce al Language Model usato per Chain-of-Thought e audio understanding
- **Flash Attention**, **CPU Offload**, **Compile** e **Quantization** sono attivi di default per prestazioni ottimali
- Se richiedi una durata o un batch oltre i limiti della GPU, verrà mostrato un avviso e i valori verranno limitati
- **Constrained Decoding**: quando l'LM è inizializzato, anche la generazione della durata dell'LM è vincolata al limite massimo del tier GPU, evitando OOM durante la generazione CoT
- Per GPU con ≤6GB di VRAM, l'inizializzazione LM è disabilitata di default per preservare memoria per il modello DiT
- Puoi sovrascrivere manualmente le impostazioni con argomenti CLI o tramite la Gradio UI

> **Contributi della community benvenuti**: le configurazioni dei tier GPU sopra si basano sui nostri test su hardware comuni. Se noti che le prestazioni reali del tuo dispositivo differiscono (es. può gestire durate più lunghe o batch più grandi), ti invitiamo a fare test più approfonditi e aprire una PR per ottimizzare queste configurazioni in `acestep/gpu_config.py`. Il tuo contributo migliora l'esperienza per tutti!

## Suggerimenti per ottimizzare la memoria

1. **VRAM bassa (<8GB)**: usa la modalità solo DiT senza inizializzare l'LM per la durata massima
2. **VRAM media (8-16GB)**: usa il modello LM 0.6B per il miglior equilibrio qualità/memoria
3. **VRAM alta (>16GB)**: abilita modelli LM più grandi (1.7B/4B) per migliore qualità e audio understanding

## Modalità debug: simulare diverse configurazioni GPU

Per test e sviluppo, puoi simulare diverse dimensioni di memoria GPU usando la variabile d'ambiente `MAX_CUDA_VRAM`:

```bash
# Simula una GPU 4GB (Tier 1)
MAX_CUDA_VRAM=4 uv run acestep

# Simula una GPU 8GB (Tier 4)
MAX_CUDA_VRAM=8 uv run acestep

# Simula una GPU 12GB (Tier 5)
MAX_CUDA_VRAM=12 uv run acestep

# Simula una GPU 16GB (Tier 6)
MAX_CUDA_VRAM=16 uv run acestep
```

Utile per:
- Testare configurazioni dei tier GPU su hardware di fascia alta
- Verificare che avvisi e limiti funzionino correttamente per ogni tier
- Sviluppare e testare nuovi parametri di configurazione GPU prima di inviare una PR
