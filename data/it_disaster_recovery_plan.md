# DataPulse S.p.A. - Piano di Disaster Recovery
Codice: DP-IT-DRP-001
Revisione: Marzo 2024
Confidenzialità: Alta

## Obiettivi di Recupero (RTO/RPO)
- **RTO (Recovery Time Objective)**: 4 ore per i sistemi critici.
- **RPO (Recovery Point Objective)**: 1 ora per i database transazionali.

## Squadra di Emergenza
- Coordinatore: Mario Rossi
- Responsabile Infrastruttura: Elena Verdi
- Comunicazione: Ufficio PR

## Procedura di Ripristino
1. Attivazione del sito di disaster recovery su AWS Region (Sud-Europa).
2. Ripristino degli snapshot dei database dall'ultimo backup immutabile.
3. Switch del traffico DNS tramite Route53.

## Test del Piano
Il piano deve essere testato ogni 6 mesi con una simulazione di "Blackout Totale".
