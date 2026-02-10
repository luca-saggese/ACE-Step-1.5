# Guida utente della demo Gradio di ACE-Step

**Lingua / 语言 / 言語 / Lingua:** [English](../en/GRADIO_GUIDE.md) | [中文](../zh/GRADIO_GUIDE.md) | [日本語](../ja/GRADIO_GUIDE.md) | [Italiano](GRADIO_GUIDE.md)

---

Questa guida fornisce una documentazione completa per usare l'interfaccia web Gradio di ACE-Step per la generazione musicale, incluse tutte le funzionalità e impostazioni.

## Indice

- [Per iniziare](#per-iniziare)
- [Configurazione del servizio](#configurazione-del-servizio)
- [Modalità di generazione](#modalità-di-generazione)
- [Tipi di task](#tipi-di-task)
- [Parametri di input](#parametri-di-input)
- [Impostazioni avanzate](#impostazioni-avanzate)
- [Sezione risultati](#sezione-risultati)
- [Addestramento LoRA](#addestramento-lora)
- [Suggerimenti e buone pratiche](#suggerimenti-e-buone-pratiche)

---

## Per iniziare

### Avvio della demo

```bash
# Avvio base
python app.py

# Con pre-inizializzazione
python app.py --config acestep-v15-turbo --init-llm

# Con porta specifica
python app.py --port 7860
```

### Panoramica dell'interfaccia

L'interfaccia Gradio è composta da diverse sezioni principali:

1. **Configurazione del servizio** - Caricamento e inizializzazione modelli
2. **Input richiesti** - Tipo di task, upload audio e modalità di generazione
3. **Caption e lyrics** - Input testuali per la generazione
4. **Parametri opzionali** - Metadati come BPM, tonalità, durata
5. **Impostazioni avanzate** - Controllo fine della generazione
6. **Risultati** - Riproduzione audio generato e gestione

---

## Configurazione del servizio

### Selezione modello

| Impostazione | Descrizione |
|---------|-------------|
| **Checkpoint File** | Seleziona un checkpoint del modello addestrato (se disponibile) |
| **Main Model Path** | Scegli la config del modello DiT (es. `acestep-v15-turbo`, `acestep-v15-turbo-shift3`) |
| **Device** | Dispositivo di elaborazione: `auto` (consigliato), `cuda` o `cpu` |

### Configurazione LM 5Hz

| Impostazione | Descrizione |
|---------|-------------|
| **5Hz LM Model Path** | Seleziona il language model (es. `acestep-5Hz-lm-0.6B`, `acestep-5Hz-lm-1.7B`) |
| **5Hz LM Backend** | `vllm` (più veloce, consigliato) o `pt` (PyTorch, più compatibile) |
| **Initialize 5Hz LM** | Spunta per caricare l'LM durante l'inizializzazione (necessario per thinking mode) |

### Opzioni di performance

| Impostazione | Descrizione |
|---------|-------------|
| **Use Flash Attention** | Abilita per inferenza più veloce (richiede pacchetto flash_attn) |
| **Offload to CPU** | Offload dei modelli su CPU quando inattivi per risparmiare VRAM |
| **Offload DiT to CPU** | Offload specifico del modello DiT su CPU |

### Adattatore LoRA

| Impostazione | Descrizione |
|---------|-------------|
| **LoRA Path** | Percorso della directory dell'adattatore LoRA addestrato |
| **Load LoRA** | Carica l'adattatore LoRA specificato |
| **Unload** | Rimuove il LoRA attualmente caricato |
| **Use LoRA** | Abilita/disabilita il LoRA caricato per l'inferenza |

> **⚠️ Nota:** gli adattatori LoRA non possono essere caricati su modelli quantizzati a causa di un problema di compatibilità tra PEFT e TorchAO. Se devi usare LoRA, imposta **INT8 Quantization** su **None** prima di caricare l'adattatore.

### Inizializzazione

Fai clic su **Initialize Service** per caricare i modelli. Il box di stato mostrerà avanzamento e conferma.

---

## Modalità di generazione

### Modalità semplice

La modalità semplice è pensata per generazione rapida basata su linguaggio naturale.

**Come usarla:**
1. Seleziona "Simple" nel radio button della modalità di generazione
2. Inserisci una descrizione in linguaggio naturale nel campo "Song Description"
3. (Opzionale) Spunta "Instrumental" se non vuoi voci
4. (Opzionale) Seleziona una lingua vocale preferita
5. Clicca **Create Sample** per generare caption, lyrics e metadati
6. Rivedi il contenuto generato nelle sezioni espanse
7. Clicca **Generate Music** per creare l'audio

**Esempi di descrizione:**
- "a soft Bengali love song for a quiet evening"
- "upbeat electronic dance music with heavy bass drops"
- "melancholic indie folk with acoustic guitar"
- "jazz trio playing in a smoky bar"

**Campione casuale:** clicca il pulsante 🎲 per caricare una descrizione di esempio casuale.

### Modalità personalizzata

La modalità personalizzata offre controllo completo su tutti i parametri di generazione.

**Come usarla:**
1. Seleziona "Custom" nel radio button della modalità di generazione
2. Compila manualmente i campi Caption e Lyrics
3. Imposta i metadati opzionali (BPM, tonalità, durata, ecc.)
4. (Opzionale) Clicca **Format** per migliorare il tuo input con l'LM
5. Configura le impostazioni avanzate come necessario
6. Clicca **Generate Music** per creare l'audio

---

## Tipi di task

### text2music (Default)

Genera musica da descrizioni testuali e/o lyrics.

**Use case:** creare nuova musica da zero basandosi su prompt.

**Input richiesti:** Caption o Lyrics (almeno uno)

### cover

Trasforma audio esistente mantenendo la struttura ma cambiando stile.

**Use case:** creare versioni cover in stili diversi.

**Input richiesti:**
- Audio sorgente (upload nella sezione Audio Uploads)
- Caption che descrive lo stile target

**Parametro chiave:** `Audio Cover Strength` (0.0-1.0)
- Valori alti mantengono più struttura originale
- Valori bassi permettono più libertà creativa

### repaint

Rigenera un segmento temporale specifico dell'audio.

**Use case:** correggere o modificare sezioni specifiche della musica generata.

**Input richiesti:**
- Audio sorgente
- Inizio repainting (secondi)
- Fine repainting (secondi, -1 per fine file)
- Caption che descrive il contenuto desiderato

### lego (Solo modello base)

Genera una traccia strumentale specifica nel contesto di audio esistente.

**Use case:** aggiungere layer strumentali a backing track.

**Input richiesti:**
- Audio sorgente
- Nome traccia (seleziona da dropdown)
- Caption che descrive le caratteristiche della traccia

**Tracce disponibili:** vocals, backing_vocals, drums, bass, guitar, keyboard, percussion, strings, synth, fx, brass, woodwinds

### extract (Solo modello base)

Estrae/isola una traccia strumentale specifica da audio mixato.

**Use case:** separazione stem, isolamento strumenti.

**Input richiesti:**
- Audio sorgente
- Nome traccia da estrarre

### complete (Solo modello base)

Completa tracce parziali con strumenti specificati.

**Use case:** auto-arrangiamento di composizioni incomplete.

**Input richiesti:**
- Audio sorgente
- Nomi tracce (selezione multipla)
- Caption che descrive lo stile desiderato

---

## Parametri di input

### Input richiesti

#### Tipo di task
Seleziona il task di generazione dal menu a tendina. Il campo istruzione si aggiorna automaticamente in base al task selezionato.

#### Upload audio

| Campo | Descrizione |
|-------|-------------|
| **Reference Audio** | Audio opzionale come riferimento di stile |
| **Source Audio** | Richiesto per task cover, repaint, lego, extract, complete |
| **Convert to Codes** | Estrae i codici semantici 5Hz dall'audio sorgente |

#### LM Codes Hints

Puoi incollare qui codici semantici audio pre-computati per guidare la generazione. Usa il pulsante **Transcribe** per analizzare i codici ed estrarre metadati.

### Caption musicale

La descrizione testuale della musica desiderata. Sii specifico su:
- Genere e stile
- Strumenti
- Mood e atmosfera
- Sensazione di tempo (se non specifichi BPM)

**Esempio:** "upbeat pop rock with electric guitars, driving drums, and catchy synth hooks"

Clicca 🎲 per caricare una caption di esempio casuale.

### Lyrics

Inserisci le lyrics con tag di struttura:

```
[Verse 1]
Walking down the street today
Thinking of the words you used to say

[Chorus]
I'm moving on, I'm staying strong
This is where I belong

[Verse 2]
...
```

**Checkbox Instrumental:** selezionalo per generare musica strumentale indipendentemente dal contenuto delle lyrics.

**Lingua vocale:** seleziona la lingua per le voci. Usa "unknown" per auto-rilevamento o per tracce strumentali.

**Pulsante Format:** clicca per migliorare caption e lyrics usando il LM 5Hz.

### Parametri opzionali

| Parametro | Default | Descrizione |
|-----------|---------|-------------|
| **BPM** | Auto | Tempo in battiti per minuto (30-300) |
| **Key Scale** | Auto | Tonalità musicale (es. "C Major", "Am", "F# minor") |
| **Time Signature** | Auto | Metrica: 2 (2/4), 3 (3/4), 4 (4/4), 6 (6/8) |
| **Audio Duration** | Auto/-1 | Durata target in secondi (10-600). -1 per automatico |
| **Batch Size** | 2 | Numero di varianti audio da generare (1-8) |

---

## Impostazioni avanzate

### Parametri DiT

| Parametro | Default | Descrizione |
|-----------|---------|-------------|
| **Inference Steps** | 8 | Step di denoising. Turbo: 1-20, Base: 1-200 |
| **Guidance Scale** | 7.0 | Forza CFG (solo modello base). Più alto = segue più il prompt |
| **Seed** | -1 | Seed casuale. Usa valori separati da virgola per batch |
| **Random Seed** | ✓ | Se selezionato, genera seed casuali |
| **Audio Format** | mp3 | Formato di output: mp3, flac |
| **Shift** | 3.0 | Fattore di shift timestep (1.0-5.0). Consigliato 3.0 per turbo |
| **Inference Method** | ode | ode (Euler, più veloce) o sde (stocastico) |
| **Custom Timesteps** | - | Sovrascrive i timesteps (es. "0.97,0.76,0.615,0.5,0.395,0.28,0.18,0.085,0") |

### Parametri solo modello base

| Parametro | Default | Descrizione |
|-----------|---------|-------------|
| **Use ADG** | ✗ | Abilita Adaptive Dual Guidance per migliore qualità |
| **CFG Interval Start** | 0.0 | Quando iniziare ad applicare CFG (0.0-1.0) |
| **CFG Interval End** | 1.0 | Quando interrompere l'applicazione CFG (0.0-1.0) |

### Parametri LM

| Parametro | Default | Descrizione |
|-----------|---------|-------------|
| **LM Temperature** | 0.85 | Temperatura campionamento (0.0-2.0). Più alto = più creativo |
| **LM CFG Scale** | 2.0 | Forza guidance LM (1.0-3.0) |
| **LM Top-K** | 0 | Campionamento Top-K. 0 disabilita |
| **LM Top-P** | 0.9 | Nucleus sampling (0.0-1.0) |
| **LM Negative Prompt** | "NO USER INPUT" | Prompt negativo per CFG |

### Opzioni CoT (Chain-of-Thought)

| Opzione | Default | Descrizione |
|--------|---------|-------------|
| **CoT Metas** | ✓ | Genera metadati via ragionamento LM |
| **CoT Language** | ✓ | Rileva lingua vocale via LM |
| **Constrained Decoding Debug** | ✗ | Abilita log di debug |

### Opzioni di generazione

| Opzione | Default | Descrizione |
|--------|---------|-------------|
| **LM Codes Strength** | 1.0 | Quanto i codici LM influenzano la generazione (0.0-1.0) |
| **Auto Score** | ✗ | Calcola automaticamente i punteggi qualità |
| **Auto LRC** | ✗ | Genera automaticamente timestamp lyrics |
| **LM Batch Chunk Size** | 8 | Numero massimo elementi per batch LM (VRAM) |

### Controlli principali di generazione

| Controllo | Descrizione |
|---------|-------------|
| **Think** | Abilita LM 5Hz per generazione codici e metadati |
| **ParallelThinking** | Abilita batch LM in parallelo |
| **CaptionRewrite** | Consenti all'LM di migliorare la caption |
| **AutoGen** | Avvia automaticamente il batch successivo al completamento |

---

## Sezione risultati

### Audio generato

Fino a 8 campioni audio vengono mostrati in base alla dimensione del batch. Ogni campione include:

- **Audio Player** - Riproduci, metti in pausa e scarica l'audio generato
- **Send To Src** - Invia questo audio all'input Source Audio per ulteriori elaborazioni
- **Save** - Salva audio e metadati in un file JSON
- **Score** - Calcola un punteggio di qualità basato sulla perplessità
- **LRC** - Genera timestamp delle lyrics (formato LRC)

### Accordion Dettagli

Clicca "Score & LRC & LM Codes" per espandere e vedere:
- **LM Codes** - I codici semantici 5Hz per questo campione
- **Quality Score** - Metrica di qualità basata sulla perplessità
- **Lyrics Timestamps** - Dati temporali in formato LRC

### Navigazione batch

| Controllo | Descrizione |
|---------|-------------|
| **◀ Previous** | Visualizza il batch precedente |
| **Batch Indicator** | Mostra la posizione corrente (es. "Batch 1 / 3") |
| **Next Batch Status** | Mostra l'avanzamento della generazione in background |
| **Next ▶** | Visualizza il batch successivo (attiva la generazione se AutoGen è attivo) |

### Ripristino parametri

Clicca **Apply These Settings to UI** per ripristinare tutti i parametri di generazione dal batch corrente ai campi di input. Utile per iterare su un buon risultato.

### Risultati batch

L'accordion "Batch Results & Generation Details" contiene:
- **All Generated Files** - Scarica tutti i file di tutti i batch
- **Generation Details** - Informazioni dettagliate sul processo di generazione

---

## Addestramento LoRA

La tab LoRA Training fornisce strumenti per creare adattatori LoRA personalizzati.

### Tab Dataset Builder

#### Step 1: Carica o scansiona

**Opzione A: Carica dataset esistente**
1. Inserisci il percorso di un dataset JSON salvato
2. Clicca **Load**

**Opzione B: Scansiona nuova directory**
1. Inserisci il percorso della cartella audio
2. Clicca **Scan** per trovare file audio (wav, mp3, flac, ogg, opus)

#### Step 2: Configura dataset

| Impostazione | Descrizione |
|---------|-------------|
| **Dataset Name** | Nome del dataset |
| **All Instrumental** | Spunta se tutte le tracce sono senza voci |
| **Custom Activation Tag** | Tag unico per attivare lo stile LoRA |
| **Tag Position** | Posizione del tag: Prepend, Append o Replace caption |

#### Step 3: Auto-label

Clicca **Auto-Label All** per generare metadati per tutti i file audio:
- Caption (descrizione musicale)
- BPM
- Key
- Time Signature

**Opzione Skip Metas** salta l'etichettatura LLM e usa valori N/A.

#### Step 4: Anteprima e modifica

Usa lo slider per selezionare campioni e modificare manualmente:
- Caption
- Lyrics
- BPM, Key, Time Signature
- Language
- Flag instrumental

Clicca **Save Changes** per aggiornare il campione.

#### Step 5: Salva dataset

Inserisci un percorso di salvataggio e clicca **Save Dataset** per esportare in JSON.

#### Step 6: Preprocess

Converti il dataset in tensori pre-computati per addestramento veloce:
1. (Opzionale) Carica un dataset JSON esistente
2. Imposta la directory di output dei tensori
3. Clicca **Preprocess**

Questo codifica l'audio in latenti VAE, il testo in embedding, ed esegue il condition encoder.

### Tab Train LoRA

#### Selezione dataset

Inserisci il percorso della directory dei tensori preprocessati e clicca **Load Dataset**.

#### Impostazioni LoRA

| Impostazione | Default | Descrizione |
|---------|---------|-------------|
| **LoRA Rank (r)** | 64 | Capacità LoRA. Più alto = più capacità, più memoria |
| **LoRA Alpha** | 128 | Fattore di scala (tipicamente 2x rank) |
| **LoRA Dropout** | 0.1 | Dropout per regolarizzazione |

#### Parametri di training

| Impostazione | Default | Descrizione |
|---------|---------|-------------|
| **Learning Rate** | 1e-4 | Learning rate per l'ottimizzazione |
| **Max Epochs** | 500 | Numero massimo di epoche |
| **Batch Size** | 1 | Dimensione batch di training |
| **Gradient Accumulation** | 1 | Batch effettivo = batch_size × accumulo |
| **Save Every N Epochs** | 200 | Frequenza di salvataggio checkpoint |
| **Shift** | 3.0 | Shift timestep per modello turbo |
| **Seed** | 42 | Seed casuale per riproducibilità |

#### Controlli di training

- **Start Training** - Avvia il training
- **Stop Training** - Interrompi il training
- **Training Progress** - Mostra epoca corrente e loss
- **Training Log** - Output dettagliato del training
- **Training Loss Plot** - Curva visiva della loss

#### Export LoRA

Dopo il training, esporta l'adattatore finale:
1. Inserisci il percorso di export
2. Clicca **Export LoRA**

#### Note sulle performance (Windows / poca VRAM)

Su Windows o sistemi con VRAM limitata, training e preprocessing possono bloccarsi o usare più memoria del previsto. Ecco alcune opzioni utili:

- **Persistent workers** – La reinizializzazione dei worker a fine epoca su Windows può causare lunghe pause; il comportamento predefinito è stato migliorato (vedi fix correlati) quindi i blocchi sono meno comuni.
- **Offload dei modelli inutilizzati** – Durante il preprocessing, l'offload dei modelli non necessari per lo step corrente (es. via **Offload to CPU** in Service Configuration) può ridurre molto l'uso VRAM e evitare picchi che rallentano o bloccano.
- **Tiled encode** – L'encoding a tile durante il preprocessing riduce il picco di VRAM e può ridurre drasticamente i tempi quando la VRAM è stretta.
- **Batch size** – Ridurre il batch size nel training riduce la memoria a costo di tempi più lunghi; l'accumulo di gradiente permette di mantenere il batch effettivo entro i limiti VRAM.

Queste opzioni sono particolarmente utili quando il preprocessing richiede molto tempo o si verificano OOM o lunghe pause tra le epoche.

---

## Suggerimenti e buone pratiche

### Per la migliore qualità

1. **Usa la modalità thinking** - Mantieni il checkbox "Think" attivo per generazione migliorata dall'LM
2. **Sii specifico nelle caption** - Includi genere, strumenti, mood e dettagli di stile
3. **Lascia all'LM i metadati** - Lascia BPM/Key/Duration vuoti per auto-rilevamento
4. **Usa la generazione batch** - Genera 2-4 varianti e scegli la migliore

### Per una generazione più veloce

1. **Usa il modello turbo** - Seleziona `acestep-v15-turbo` o `acestep-v15-turbo-shift3`
2. **Mantieni gli step a 8** - Il default è ottimale per turbo
3. **Riduci il batch size** - Batch più piccolo se vuoi risultati rapidi
4. **Disabilita AutoGen** - Controllo manuale dei batch

### Per risultati consistenti

1. **Imposta un seed specifico** - Deseleziona "Random Seed" e inserisci un seed
2. **Salva buoni risultati** - Usa "Save" per esportare i parametri
3. **Usa "Apply These Settings"** - Ripristina i parametri da un buon batch

### Per musica lunga

1. **Imposta durata esplicita** - Specifica la durata in secondi
2. **Usa repaint** - Correggi sezioni problematiche dopo la generazione iniziale
3. **Concatena generazioni** - Usa "Send To Src" per costruire su risultati precedenti

### Per coerenza di stile

1. **Allena un LoRA** - Crea un adattatore personalizzato per il tuo stile
2. **Usa audio di riferimento** - Carica un riferimento di stile in Audio Uploads
3. **Usa caption coerenti** - Mantieni un linguaggio descrittivo simile

### Risoluzione problemi

**Nessun audio generato:**
- Verifica che il modello sia inizializzato (messaggio verde)
- Assicurati che l'LM 5Hz sia inizializzato se usi thinking
- Controlla l'output di stato per messaggi di errore

**Qualità scarsa:**
- Aumenta gli step di inferenza (per modello base)
- Regola guidance scale
- Prova seed diversi
- Rendi la caption più specifica

**Memoria insufficiente:**
- Riduci il batch size
- Abilita CPU offloading
- Riduci LM batch chunk size

**LM non funziona:**
- Assicurati di aver selezionato "Initialize 5Hz LM" all'avvio
- Controlla che il percorso del modello LM sia valido
- Verifica che il backend vllm o PyTorch sia disponibile

---

## Scorciatoie da tastiera

L'interfaccia Gradio supporta scorciatoie web standard:
- **Tab** - Passa tra i campi input
- **Enter** - Invia input testuali
- **Space** - Attiva/disattiva checkbox

---

## Supporto lingua

L'interfaccia supporta più lingue UI:
- **Inglese** (en)
- **Cinese** (zh)
- **Giapponese** (ja)

Seleziona la lingua preferita nella sezione Configurazione del servizio.

---

Per maggiori informazioni, vedi:
- README principale: [`../../README.md`](../../README.md)
- Documentazione REST API: [`API.md`](API.md)
- API di inferenza Python: [`INFERENCE.md`](INFERENCE.md)
