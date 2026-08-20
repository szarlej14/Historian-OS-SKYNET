# Obsidian ↔ GitHub — Historian OS SKYNET

## Docelowe połączenie

- Vault: Historian OS SKYNET
- GitHub repository: `szarlej14/Historian-OS-SKYNET`
- Branch: `main`
- Synchronizator Android: GitSync Portal
- Transport: GitHub REST API (bez systemowego Git)

## Ustawienia GitSync Portal

1. GitHub token: fine-grained PAT ograniczony do tego repozytorium.
2. Repository: `szarlej14/Historian-OS-SKYNET`
3. Branch: `main`
4. Device detection: ON
5. Sync on startup: ON
6. Sync after save: ON
7. Periodic sync: OFF na etapie pierwszej konfiguracji; włączyć dopiero po udanym teście.

## Bezpieczeństwo pierwszej synchronizacji

Przed pierwszym `two-way sync` należy wykonać `Test connection`. Nie umieszczać tokena w plikach repozytorium ani w tej dokumentacji.

Pierwsza synchronizacja ma zachować istniejące pliki po obu stronach; przy konflikcie należy sprawdzić kopię konfliktową zamiast bezwarunkowo nadpisywać dane.

## Kolejny etap

Po uruchomieniu synchronizacji można dołączyć Templater i Dataview/Bases do warstwy roboczej Obsidiana. Najpierw stabilizujemy synchronizację repozytorium.
