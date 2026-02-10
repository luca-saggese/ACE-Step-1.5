# Guida CLI di ACE-Step 1.5

Questa guida spiega come usare `cli.py`, il wizard interattivo e la CLI basata su configurazione per l'inferenza di ACE-Step.

La CLI è **solo wizard/config**: oppure esegui il wizard per creare una config, oppure carichi una config `.toml` e generi.

---

## Avvio rapido

Generazione via wizard (interattivo):

```bash
python cli.py
```

Generazione da una config salvata:

```bash
python cli.py --config config.toml
```

Crea o modifica una config senza generare:

```bash
python cli.py --configure
python cli.py --configure --config config.toml
```

---

## Flag CLI

- `-c` / `--config` — Percorso del file di configurazione `.toml` da caricare.
- `--configure` — Esegue il wizard per salvare la configurazione senza generare.
- `--log-level` — Livello di logging per i moduli interni. Uno tra `TRACE`, `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. Default: `INFO`.

---

## Flusso del wizard

1. Scegli uno dei 6 task.
2. Seleziona un modello DiT (tra i modelli locali disponibili, o auto-download).
3. Seleziona un modello LM (tra i modelli locali disponibili, o auto-download).
4. Fornisci input specifici del task (audio sorgente, tracce, ecc.).
5. Per `text2music`: scegli tra Modalità Semplice (auto-generazione di caption/lyrics via LM) o input manuale.
6. Fornisci caption / descrizione.
7. Scegli la modalità lyrics (strumentale / auto-generazione / file / incolla).
8. Imposta il numero di output.
9. (Opzionale) Configura parametri avanzati (metadati, impostazioni DiT, LM, output).
10. Rivedi il riepilogo e conferma la generazione.
11. Salva la configurazione in un file `.toml`.

Se salti i parametri avanzati, il wizard compila **tutti i parametri opzionali** con i valori di default di `GenerationParams` e `GenerationConfig`.

---

## Modalità Configure (`--configure`)

`--configure` esegue il wizard **senza generazione** e salva sempre una config.

Comportamento:
- Se `--config` è fornito, il file viene caricato e usato come valori iniziali del wizard.
- Dopo il wizard, scegli un nome file da salvare (sovrascrittura o nuovo).
- Il programma termina senza generare.

---

## File di configurazione (`.toml`)

Il wizard salva un file `.toml` che contiene tutti i parametri. Queste chiavi mappano direttamente ai campi usati in `cli.py`.

Quando carichi una config con `--config`, tutte le chiavi vengono applicate alle impostazioni runtime.

---

## Modifica del prompt (`instruction.txt`)

Quando `thinking=True` e una config è caricata via `--config`, la CLI cerca un file `instruction.txt` nella root del progetto. Se presente, il suo contenuto viene usato come prompt formattato pre-caricato per la generazione LM degli audio-token, saltando la fase di editing interattivo.

Quando si esegue senza config (modalità wizard), la CLI scrive il prompt formattato del LM in `instruction.txt` e si mette in pausa così puoi modificarlo prima che proceda la generazione degli audio-token.

Questo consente di rifinire il prompt esatto (caption, lyrics, metadati) che il LM vede prima di generare i codici audio.
