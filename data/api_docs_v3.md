# DataPulse Core API Documentation
Versione: 3.1.2
Endpoint Base: `https://api.datapulse.it/v3/`

## Autenticazione
Tutte le chiamate API richiedono un Bearer Token nel'header `Authorization`. I token scadono ogni 24 ore.

## Endpoint: GET /customers
Restituisce la lista dei clienti caricati nel sistema.
### Parametri di Query
- `limit`: Numero di risultati (default: 50, max: 200).
- `offset`: Paginazione dei risultati.

## Codici di Errore
- `401 Unauthorized`: Token mancante o scaduto.
- `403 Forbidden`: Permessi insufficienti per la risorsa richiesta.
- `429 Too Many Requests`: Limite di rate limit superato (1000 req/min).
