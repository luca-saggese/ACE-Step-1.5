# ACE-Step 1.5 — Guida per Musicisti

## Che cos'è?

ACE-Step è un'IA per creare musica che gira sul tuo computer. Descrivi la musica che vuoi — lo stile, gli strumenti, l'atmosfera, i testi — e genera una canzone completa in pochi secondi. Non un loop, non un beat — una canzone completa con voce, strumenti e struttura.

A differenza di servizi cloud come Suno o Udio, ACE-Step viene eseguito in locale. Possiedi il software, possiedi l'output e puoi usarlo offline senza abbonamenti, limiti di velocità o vincoli sui Termini di Servizio.

È open-source e gratuito.

---

## Come funziona realmente?

ACE-Step ha due “menti” che lavorano insieme, come un cantautore e un ingegnere di studio:

```
    ┌─────────────────────────────────────────────────────────┐
    │                    YOU (the musician)                   │
    │                                                         │
    │   "I want an upbeat pop song with electric guitars,     │
    │    catchy chorus, female vocals, 120 BPM"               │
    └──────────────────────┬──────────────────────────────────┘
                           │
                    Your description
                           │
                           ▼
    ┌─────────────────────────────────────────────────────────┐
    │              BRAIN 1: The Songwriter (LM)               │
    │                                                         │
    │   Reads your description and thinks about it.           │
    │   Fills in the gaps you didn't specify:                 │
    │     - What key fits this mood? → G Major                │
    │     - What tempo feels right? → 122 BPM                 │
    │     - How should the song be structured?                │
    │     - Where should energy peak?                         │
    │                                                         │
    │   Creates a detailed blueprint of the song.             │
    │                                                         │
    │   (Optional — you can skip this brain for speed,        │
    │    or if you already know exactly what you want.)       │
    └──────────────────────┬──────────────────────────────────┘
                           │
                      Blueprint
                           │
                           ▼
    ┌─────────────────────────────────────────────────────────┐
    │           BRAIN 2: The Studio Engineer (DiT)            │
    │                                                         │
    │   Takes the blueprint and builds the actual audio.      │
    │   Starts with pure noise (like static on a TV)          │
    │   and gradually shapes it into music — step by step.    │
    │                                                         │
    │   Each step removes a layer of noise and adds           │
    │   detail: instruments come into focus, vocals           │
    │   emerge, drums tighten up, mix clears.                 │
    │                                                         │
    │   After 8 steps (fast mode) or 50 steps (quality        │
    │   mode), you have a finished song.                      │
    └──────────────────────┬──────────────────────────────────┘
                           │
                     Finished audio
                           │
                           ▼
    ┌─────────────────────────────────────────────────────────┐
    │                    YOUR SONG  ♪ ♫                       │
    │           (WAV or MP3, ready to play)                   │
    └─────────────────────────────────────────────────────────┘
```

**L'idea chiave:** il Brain 1 (il Cantautore) è opzionale. Puoi fornire direttamente il blueprint al Brain 2 (l'Ingegnere di Studio) se preferisci il controllo totale, oppure lasciare che il Brain 1 si occupi della pianificazione. La scelta è tua ogni volta.

---

## Cosa può fare?

ACE-Step offre sei modalità creative. Pensale come diversi strumenti in uno studio:

```
    ┌──────────────────────────────────────────────────────┐
    │                  YOUR CREATIVE TOOLKIT               │
    │                                                      │
    │  🎵 Text to Music    Describe it → Get a song        │
    │  🎨 Cover            Restyle an existing song        │
    │  🖌️ Repaint          Fix one section of a song       │
    │  🧱 Lego             Add layers to a backing track   │
    │  🔬 Extract          Pull out individual instruments │
    │  🎹 Complete         Add accompaniment to vocals     │
    └──────────────────────────────────────────────────────┘
```

### Text to Music — Partire da zero

La modalità più semplice. Scrivi una descrizione, ottieni una canzone.

**Tu scrivi:** "melancholic indie folk with acoustic guitar and breathy female vocals"
**Ottieni:** Una canzone completa che corrisponde a quella descrizione.

### Cover — Trasformare lo stile di una canzone

Fornisci una canzone esistente e indica lo stile desiderato. Mantiene la struttura (forma melodica, ritmo, forma della canzone) ma cambia tutto il resto.

**Tu fornisci:** Una ballata country
**Tu scrivi:** "heavy metal rock with distorted guitars and screaming vocals"
**Ottieni:** La stessa canzone reimmaginata come heavy metal

### Repaint — Sistemare solo una parte

Hai generato una canzone che ti piace, ma l'intro è debole? Repaint ti permette di rigenerare solo quella sezione mantenendo il resto intatto.

**Tu fornisci:** Una canzone dove i secondi 0-10 vanno migliorati
**Tu scrivi:** "dramatic orchestral build-up"
**Ottieni:** La stessa canzone, ma con una nuova intro

### Lego — Impilare layer di strumenti

Hai un loop di batteria? Aggiungi il basso. Hai una traccia di chitarra? Aggiungi archi sopra. Lego ti permette di costruire la canzone un layer alla volta.

### Extract — Separare un mix

L'opposto di Lego. Fornisci un mix completo e chiedi di isolare solo le voci, o solo la batteria, o solo la chitarra.

### Complete — Aggiungere accompagnamento

Hai una registrazione vocale senza altri strumenti? Complete genera gli strumenti di accompagnamento per abbinarla.

---

## Cosa serve per farlo girare?

### La risposta breve

Un computer con una buona scheda grafica (GPU). Più potente è la GPU, più velocemente e per più tempo potrai generare canzoni.

### Guida hardware

```
    YOUR GPU MEMORY          WHAT YOU CAN DO
    ─────────────────────────────────────────────────────

    4 GB  (entry level)      Songs up to 3 minutes
    ▓░░░░░░░░░░░░░░░░░░░    1 song at a time
                             Basic mode only (no Songwriter brain)

    8 GB  (mainstream)       Songs up to 6 minutes
    ▓▓▓▓░░░░░░░░░░░░░░░░    1-2 songs at a time
                             Optional lightweight Songwriter brain

    12 GB (sweet spot)       Songs up to 6 minutes
    ▓▓▓▓▓▓░░░░░░░░░░░░░░    2-4 songs at a time
                             Full Songwriter brain available

    16 GB (enthusiast)       Songs up to 8 minutes
    ▓▓▓▓▓▓▓▓░░░░░░░░░░░░    2-4 songs at a time
                             Larger, smarter Songwriter brain

    24 GB+ (high end)        Songs up to 10 minutes
    ▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░    Up to 8 songs at a time
                             All features unlocked
```

**GPU comuni e dove si collocano:**

| GPU | Memory | Tier |
|-----|--------|------|
| GTX 1050 Ti | 4 GB | Entry |
| RTX 3060 / 4060 | 8 GB | Mainstream |
| RTX 3070 / 4070 | 8-12 GB | Sweet spot |
| RTX 3080 / 4080 | 12-16 GB | Enthusiast |
| RTX 4090 | 24 GB | High end |
| Apple M1/M2/M3 (Mac) | Shared memory | Supported, varies |

**Spazio su disco:** Circa 100 GB liberi. I modelli AI sono file grandi (circa 60 GB totali) che scaricano automaticamente la prima volta che esegui il software.

**Sistema operativo:** Windows, Mac o Linux funzionano tutti.

---

## Avviare

### Su Windows (percorso più semplice)

1. Scarica il pacchetto portabile dal sito ACE-Step (un singolo file .7z)
2. Estrallo (clic destro → Estrai con 7-Zip o WinRAR)
3. Doppio clic su **start_gradio_ui.bat** nella cartella estratta
4. Si apre una finestra del browser — quello è il tuo studio
5. Al primo avvio i modelli si scaricano automaticamente (30 min - 2 ore a seconda della velocità di rete)

Tutto qui. Nessuna programmazione richiesta.

### Su Mac o Linux

Dovrai digitare qualche comando nel terminale, ma è semplice:

```
Step 1:  Install the "uv" package manager (a one-time setup)
Step 2:  Download ACE-Step from GitHub
Step 3:  Run "uv sync" to install everything
Step 4:  Run "uv run acestep" to launch
Step 5:  Open your browser to http://localhost:7860
```

Il README del progetto su GitHub spiega ogni passo con comandi copy-paste.

---

## L'interfaccia: cosa vedrai

Quando ACE-Step si apre nel browser, troverai un'interfaccia con tre aree principali:

```
    ┌─────────────────────────────────────────────────────────────┐
    │  ACE-Step 1.5                                               │
    ├─────────────┬───────────────────┬───────────────────────────┤
    │  Generate   │  LoRA Training    │  Dataset Explorer         │
    ├─────────────┴───────────────────┴───────────────────────────┤
    │                                                             │
    │  The Generate tab is where you'll spend 95% of your time.   │
    │                                                             │
    │  LoRA Training is for teaching the AI your personal style.  │
    │                                                             │
    │  Dataset Explorer is for browsing example prompts.          │
    │                                                             │
    └─────────────────────────────────────────────────────────────┘
```

### La scheda Generate

Questo è il tuo spazio principale. Ha due modalità:

**Simple Mode** — Per risultati rapidi
- Scrivi una descrizione naturale come "a soft love song for a quiet evening"
- Clicca "Create Sample" e l'AI completa i dettagli
- Clicca "Generate Music" — fatto

**Custom Mode** — Per controllo preciso
- Scrivi la descrizione esatta (caption)
- Scrivi i testi con tag di struttura
- Imposta tempo, tonalità e durata
- Regola impostazioni avanzate se vuoi

La maggior parte delle persone inizia con Simple Mode, poi passa a Custom Mode quando capisce le risposte del sistema.

---

## Scrivere i prompt: come parlare con l'AI

La competenza più importante con ACE-Step è imparare a descrivere ciò che vuoi. Comunichi tramite due input principali:

### La Caption — la tua visione generale

La caption è un breve paragrafo che descrive l'intera canzone. Pensalo come la risposta a: "Se entrassi in uno studio con session musicians, come descriveresti ciò che vuoi?"

**Vago (l'AI indovinerà molto):**
> "a sad song"

**Meglio (fornisce direzione reale all'AI):**
> "melancholic piano ballad with soft female vocals, gentle string accompaniment, slow tempo, intimate and heartbreaking atmosphere"

**Consigli per buone caption:**
- Nomina il genere: pop, rock, jazz, electronic, folk, hip-hop, lo-fi, synthwave
- Nomina gli strumenti: acoustic guitar, piano, synth pads, 808 drums, strings
- Nomina l'umore: melancholic, uplifting, energetic, dreamy, aggressive, intimate
- Nomina lo stile di produzione: lo-fi, polished, live recording, bedroom pop, orchestral

### I testi — lo script della tua canzone

I testi fanno doppio lavoro in ACE-Step. Non sono solo parole — dicono all'AI come la canzone dovrebbe essere strutturata nel tempo.

Usa tag tra parentesi quadre per marcare le sezioni:

```
[Intro]

[Verse 1]
Walking through the empty streets
Thinking of your gentle touch
Summer nights and softer dreams

[Chorus]
We rise together
Into the light
This is our moment tonight

[Verse 2]
Stars are falling from the sky
Your hand fits perfectly in mine

[Bridge]
If tomorrow never comes
At least we had this

[Chorus]
We rise together
Into the light
This is our moment tonight

[Outro]
```

**Cosa fanno i tag:**

```
    [Intro]          → Sets up atmosphere, usually instrumental
    [Verse]          → Main storytelling section, moderate energy
    [Pre-Chorus]     → Builds tension before the chorus
    [Chorus]         → Emotional peak, highest energy
    [Bridge]         → A shift — different melody, different feel
    [Instrumental]   → No vocals, just instruments
    [Outro]          → Winds down, often fades
```

**Suggerimenti per i testi:**
- Mantieni le righe intorno a 6-10 sillabe così l'AI può inserirle naturalmente
- Usa MAIUSCOLO per parole che vuoi enfatizzare o urlate
- Usa (parentesi) per cori in background o echi
- Aggiungi descrittori ai tag per guida extra: `[Chorus - anthemic]` o `[Verse - whispered]`

### Opzionale: Metadata

Puoi anche impostare parametri musicali specifici:

| Setting | What It Means | Typical Values |
|---------|---------------|----------------|
| **BPM** | Speed of the song | 60-80 (slow), 90-120 (medium), 130-180 (fast) |
| **Key** | Musical key | C Major (bright), A minor (melancholic), etc. |
| **Duration** | Song length in seconds | 60 (1 min), 180 (3 min), 300 (5 min) |
| **Language** | Vocal language | English, Spanish, Japanese, Chinese, 50+ others |

Se non imposti questi parametri, l'AI sceglierà valori sensati basati sulla caption e i testi.

---

## Lavorare con audio di riferimento

Una delle funzionalità più potenti di ACE-Step è usare audio esistente come guida per la generazione. Ci sono tre modi per farlo:

```
    ┌──────────────────────────────────────────────────────────┐
    │               THREE WAYS TO USE AUDIO INPUT              │
    │                                                          │
    │   1. REFERENCE AUDIO (style guide)                       │
    │      ┌──────────┐                                        │
    │      │ jazz.mp3 │──→ "Make something that SOUNDS         │
    │      └──────────┘     like this — same warmth, same      │
    │                       texture, same vibe"                │
    │                                                          │
    │   2. SOURCE AUDIO + COVER (restyle a song)               │
    │      ┌──────────┐                                        │
    │      │ song.mp3 │──→ "Keep the STRUCTURE of this song    │
    │      └──────────┘     but change the style completely"   │
    │                                                          │
    │   3. SOURCE AUDIO + REPAINT (fix a section)              │
    │      ┌──────────┐                                        │
    │      │ song.mp3 │──→ "Keep the whole song EXCEPT         │
    │      └──────────┘     regenerate seconds 10-20"          │
    │                                                          │
    └──────────────────────────────────────────────────────────┘
```

### Modalità Cover: il Trasformatore di Stile

Questa è la modalità per trasformare un genere in un altro. Il controllo chiave è **Audio Cover Strength** — uno slider da 0 a 100%:

```
    Audio Cover Strength

    0%                     50%                    100%
    ├──────────────────────┼──────────────────────┤
    │                      │                      │
    Ignores the         Balanced              Follows the
    original audio.     blend.                original closely.
    Pure text-based     Recognizable          Same structure,
    generation.         but transformed.      subtle changes only.


    For dramatic genre changes (country → metal):  use 30-50%
    For moderate changes (pop → jazz):             use 50-70%
    For subtle changes (rock → indie rock):        use 70-90%
```

**Esempio: Country → Heavy Metal**

1. Carica la tua canzone country come source audio
2. Seleziona il task "Cover"
3. Imposta Audio Cover Strength intorno al 40%
4. Scrivi una caption come: *"heavy metal rock with heavily distorted electric guitars, aggressive double bass drumming, powerful screaming vocals, fast tempo, high energy, intense dark atmosphere"*
5. Genera alcune varianti (batch size 2-4)
6. Scegli la tua preferita

---

## Workflow di generazione in batch

Un concetto fondamentale: **quasi mai dovresti generare una sola versione.** La generazione musicale con AI è casuale. Pensala come lanciare dadi — a volte ottieni esattamente ciò che volevi, a volte no. La soluzione è lanciare più volte e scegliere la migliore.

```
    THE RECOMMENDED WORKFLOW

    ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
```

    ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
    │  Write your  │────▶│  Generate a  │────▶│  Listen to   │
    │  description │     │  batch of 4  │     │  all four    │
    └──────────────┘     └──────────────┘     └─────┬────────┘
                                                    │
                                ┌───────────────────┼──────────┐
                                │                   │          │
                                ▼                   ▼          ▼
                          ┌──────────┐       ┌──────────┐  ┌──────────┐
                          │ Love it? │       │ Close    │  │ Not      │
                          │ Export!  │       │ but not  │  │ right?   │
                          └──────────┘       │ quite?   │  │ Tweak    │
                                             │ prompt & │  │ prompt   │
                                             │ retry    │  │ & retry  │
                                             └──────────┘

**AutoGen:** C'è anche una funzione "auto-generate" che prepara il batch successivo mentre ascolti quello corrente. Questo mantiene il flusso creativo senza interruzioni.

---

## Allenare il tuo stile (LoRA)

LoRA è un modo per insegnare ad ACE-Step il tuo sound personale. Se hai una raccolta di canzoni che rappresentano lo stile che vuoi che l'AI impari — le tue registrazioni, un genere specifico, un certo mood — puoi allenare un "style adapter" personalizzato.

### Cos'è una LoRA?

Pensala come un piccolo plugin che si appoggia sopra il modello base:

```
    ┌──────────────────────────────────────┐
    │         BASE AI MODEL                │
    │   (knows how to make all kinds       │
    │    of music in general)              │
    │                                      │
    │    ┌──────────────────────────┐      │
    │    │    YOUR LoRA ADAPTER     │      │
    │    │  (teaches it YOUR style) │      │
    │    │                          │      │
    │    │  Trained on 8-20 of      │      │
    │    │  your reference songs    │      │
    │    └──────────────────────────┘      │
    │                                      │
    └──────────────────────────────────────┘

    Without LoRA: generic but versatile
    With LoRA:    sounds more like YOUR music
```

### Come allenarne una

1. **Raccogli 8-20 canzoni** che rappresentano lo stile che vuoi
2. Vai alla scheda **LoRA Training** nell'interfaccia
3. Indica la cartella con i tuoi file audio
4. Clicca "Scan" — analizza ogni file automaticamente
5. Rivedi e modifica le etichette auto-generate se necessario
6. Clicca "Start Training" — richiede circa 1 ora su una buona GPU
7. Alla fine avrai un file adattatore LoRA che puoi caricare quando vuoi

### Usare la tua LoRA

1. Nella scheda Generate, trova la sezione "LoRA Adapter"
2. Inserisci il percorso alla tua LoRA allenata
3. Clicca "Load LoRA"
4. Regola lo slider **LoRA Scale**:

```
    LoRA Scale

    0%                     50%                    100%
    ├──────────────────────┼──────────────────────┤
    │                      │                      │
    No LoRA effect.     Half strength.         Full LoRA effect.
    Pure base model.    Blended style.         Maximum influence
                                               from your training.
```

5. Genera musica come al solito — l'output sarà ora influenzato dal tuo stile allenato

### Limitazione attuale: una LoRA alla volta

Al momento puoi usare solo una LoRA alla volta. Caricarne una nuova sostituisce la precedente. Non è possibile combinare più stili simultaneamente (es. "jazz LoRA al 60% + vocal LoRA al 40%"). Questo è un limite noto che potrebbe essere risolto in futuro.

---

## La domanda sulla velocità

Quanto tempo ci vuole per generare? Dipende dall'hardware e dalle impostazioni:

```
    GENERATION SPEED (approximate)

    GPU Tier          30-sec song    2-min song     5-min song
    ──────────────────────────────────────────────────────────
    Entry (4 GB)      10-15 sec      20-30 sec      N/A
    Mainstream (8 GB)  5-10 sec      10-18 sec      15-25 sec
    Sweet spot (12 GB) 3-8 sec        8-12 sec      10-15 sec
    High end (24 GB)   1-3 sec        3-7 sec        5-10 sec
```

**Fast Mode vs. Quality Mode:**
- **Turbo** (default): 8 processing steps, molto veloce, buona qualità
- **SFT/Base**: 50 processing steps, più lento, più dettaglio e sfumature

La maggior parte usa Turbo per lavoro quotidiano e SFT/Base per versioni finali.

---

## Lingue

ACE-Step può generare voci in oltre 50 lingue, incluse:

English, Spanish, French, German, Italian, Portuguese, Chinese (Mandarin & Cantonese), Japanese, Korean, Hindi, Bengali, Arabic, Turkish, Thai, Vietnamese, Swedish, Dutch, Polish, Hebrew, e molte altre.

Per usare una lingua diversa:
1. Seleziona la lingua vocale nell'interfaccia
2. Scrivi i testi in quella lingua
3. L'AI genera vocali con pronuncia e stile appropriati

Puoi anche mescolare lingue all'interno della stessa canzone.

---

## Consigli dall'esperienza

### Inizia semplice, poi affina
Non cercare di controllare tutto al primo tentativo. Parti con una caption breve e guarda cosa produce l'AI. Poi aggiungi dettagli dove il risultato ti sorprende.

### Genera in batch
Genera sempre 2-4 versioni insieme. Scegliere la migliore da più opzioni è più veloce e gratificante che cercare una singola versione perfetta.

### Correggi, non rifare
Se il 90% di una canzone è ottimo ma una sezione è sbagliata, usa **Repaint** per rigenerare solo quella parte. Non buttare via tutto.

### Sii specifico sugli strumenti
"rock song" dà troppa libertà all'AI. "rock song with crunchy rhythm guitar, punchy snare, and gravelly male vocals" gli dice esattamente cosa hai in testa.

### Usa i tag di struttura nei testi
Anche se non ti interessano ancora le parole, scrivere `[Intro] [Verse] [Chorus] [Verse] [Chorus] [Bridge] [Chorus] [Outro]` dà all'AI una roadmap per energia e dinamiche.

### Prova semi-differenti seed
Ogni generazione usa un numero casuale "seed". Se ti piacciono le impostazioni ma vuoi interpretazioni diverse, clicca genera di nuovo — ogni esecuzione usa un seed nuovo automaticamente. Puoi anche impostare un seed specifico per riprodurre un risultato che ti è piaciuto.

### Il Songwriter Brain è opzionale
Se sai già esattamente cosa vuoi (tempo, tonalità, struttura, strumenti), puoi disattivare la "Thinking Mode" per saltare il Brain 1. Questo rende la generazione più veloce e ti dà più controllo diretto.

---

## Cosa ACE-Step non è

Vale la pena chiarire cosa questo strumento non è:

- **Non è una DAW.** Non sostituisce Ableton, Logic o FL Studio. Genera audio grezzo che puoi importare nella tua DAW per editing ulteriori.
- **Non è perfetto ogni volta.** Aspettati di generare più versioni e scegliere la migliore. Pensalo come un collaboratore creativo, non una jukebox.
- **Non è un servizio cloud.** Gira sulla tua macchina. Se la tua GPU è modesta, i risultati saranno limitati. Non c'è un server che fa il lavoro per te.
- **Non è magia con un clic.** I migliori risultati arrivano imparando a descrivere ciò che vuoi. È una competenza che migliora con la pratica.

Quello che *è*: uno strumento potente, gratuito e open che mette la generazione musicale AI nelle tue mani — letteralmente sul tuo hardware — con controllo creativo completo e proprietà dell'output.

---

## Scheda di riferimento rapido

```
    ┌─────────────────────────────────────────────────────────┐
    │                    QUICK REFERENCE                      │
    │                                                         │
    │  GENERATE A SONG                                        │
    │    Caption:  Describe style, instruments, mood          │
    │    Lyrics:   [Verse] [Chorus] [Bridge] with words       │
    │    Click:    Generate Music                             │
    │                                                         │
    │  RESTYLE A SONG (Cover)                                 │
    │    Upload:   Source audio                               │
    │    Task:     Cover                                      │
    │    Caption:  Describe the NEW style                     │
    │    Strength: 30-50% for big changes, 70-90% for subtle  │
    │                                                         │
    │  FIX A SECTION (Repaint)                                │
    │    Upload:   Source audio                               │
    │    Task:     Repaint                                    │
    │    Time:     Set start and end (in seconds)             │
    │    Caption:  Describe what the fixed section should be  │
    │                                                         │
    │  APPLY CUSTOM STYLE (LoRA)                              │
    │    Load:     Your trained LoRA adapter file             │
    │    Scale:    0-100% (how much style influence)          │
    │    Then:     Generate as usual                          │
    │                                                         │
    │  KEYBOARD SHORTCUTS                                     │
    │    Batch size 2-4 recommended for every generation      │
    │    Use Turbo mode for speed, SFT/Base for quality       │
    │    Turn off Thinking Mode if you know exactly what      │
    │    you want                                             │
    └─────────────────────────────────────────────────────────┘
```
