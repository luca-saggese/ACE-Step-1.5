# Studio UI sperimentale

ACE-Step include un'interfaccia Studio UI opzionale e sperimentale basata su HTML, pensata per chi desidera un'interfaccia più strutturata, simile a una DAW.

Questa UI:

- È solo frontend
- Dialoga con la stessa REST API (`/release_task`, `/query_result`)
- Non modifica il comportamento del modello

## Come usarla

1. Avvia il server API di ACE-Step (ad es. `uv run acestep --enable-api --port 8001` oppure il tuo comando abituale).
2. Apri `ui/studio.html` nel browser (doppio clic o `file:///percorso/ACE-Step-1.5/ui/studio.html`).
3. Imposta l'URL base dell'API se necessario (predefinito: `http://localhost:8001`).
4. Inserisci prompt e opzioni, poi fai clic su **Generate**. La UI interrogherà periodicamente i risultati e mostrerà l'audio quando è pronto.

## Ambito

- **Opzionale:** Il modo predefinito di usare ACE-Step rimane la Gradio Web UI.
- **Nessuna modifica backend:** Questa UI usa solo la REST API esistente.
- **Sperimentale:** Layout e funzionalità possono cambiare in base al feedback della community.
