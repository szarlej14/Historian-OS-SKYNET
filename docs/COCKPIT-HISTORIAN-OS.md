# HISTORIAN OS SKYNET — KOKPIT AI

## Cel

Telefoniczny kokpit roboczy dla budowy, obsługi i archiwizacji Historian OS SKYNET.

## Warstwy

| Narzędzie | Rola | Główne zadanie |
|---|---|---|
| ChatGPT | ORCHESTRATOR | planowanie, analiza, koordynacja korpusu |
| GitHub | ARCHIVE / SOURCE | trwałe przechowywanie kodu, danych i historii zmian |
| Claude | SECOND OPINION | niezależna analiza i kontrola jakości |
| Gemini | GOOGLE LAYER | praca z ekosystemem Google i dodatkowa analiza |
| Meta AI | AUXILIARY AI | pomocnicze zadania i porównania |
| Termux | SYSTEM / CLI | skrypty, walidacja, automatyzacja i narzędzia lokalne |
| Obsidian | LOCAL KNOWLEDGE | lokalne notatki, mapowanie wiedzy i robocze opracowania |
| F-Droid | OPEN SOURCE | źródła narzędzi open-source |
| Asystent | DEVICE LAYER | funkcje systemowe Androida |

## Zasada pracy

1. ChatGPT koordynuje zadanie.
2. Dane docelowe trafiają do Historian OS w GitHubie.
3. Obsidian może służyć jako lokalna warstwa robocza.
4. Termux wykonuje lokalne skrypty i walidację.
5. Claude, Gemini i Meta AI mogą pełnić funkcję niezależnych warstw kontrolnych.
6. GitHub pozostaje źródłem trwałej wersji archiwum.

## Zasada bezpieczeństwa danych

Rozmowa nie jest traktowana jako trwały magazyn danych. Każdy istotny rekord, indeks, dokumentacja lub wynik pracy przeznaczony do zachowania powinien zostać zapisany w repozytorium.

## Priorytet dla Historian OS

MOTORSPORT → FORMUŁA 1 oraz pozostałe korpusy mają być przechowywane jako strukturalne rekordy z indeksami i relacjami krzyżowymi, a nie jako jeden monolityczny dokument.
