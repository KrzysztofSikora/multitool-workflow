# Operacje i ograniczenia

## Aktualizacja instalacji

Toolkit jest kopiowany do `.workflow-kit`, a źródłowy commit zapisuje się w VERSION.
Nie pobiera aktualizacji automatycznie. Aktualizacja wymaga czystego drzewa i osobnego
review diffu: porównaj nową wersję toolkitu, przenieś świadomie zmienione pliki oraz zachowaj
własny config.toml. Instalator nie nadpisuje istniejącego zestawu.

Pierwsza wersja nie posiada polecenia automatycznej aktualizacji ani migracji stanu.
Po zmianie kontraktów zachowaj stare logi, przejrzyj artefakty i wykonaj ponowną weryfikację.

## Przenoszenie istniejącej aplikacji

Nie instaluj na ślepo w aktywnym projekcie z drugim runnerem. Najpierw zakończ przebiegi,
wybierz jeden właściciel commita i publikacji, przejrzyj AGENTS.md/CLAUDE.md i kolizje skills.
Canonical skills mają prefiks mw-, ale stare hooki mogą nadal reagować na tool calls.
Wyłączenie lub aktualizację starej konfiguracji wykonuj jako osobną świadomą zmianę.

Ten toolkit nie przenosi automatycznie ograniczeń MeshCore Guardian. Dla aplikacji Android
zapisz reguły emulatora i zakazu fizycznych telefonów w AGENTS.md oraz przygotuj preflight,
który przy braku możliwości sprawdzenia urządzeń kończy się błędem. Sam prefiks emulator-
nie dowodzi nazwy AVD. Gates muszą również weryfikować docelowe urządzenie.

## Błąd sesji lub gate

1. Odczytaj lokalny komunikat runnera i wskazany log; nie publikuj logów bez przeglądu.
2. Sprawdź branch, `git status` i diff. Runner nie usuwa niedokończonych zmian.
3. Napraw przyczynę. Commituj tylko świadomie wybrane pliki. Nie obchodź uprawnień.
4. Wznów tym samym lub innym silnikiem. Jeśli `.workflow/stuck` istnieje, po rozwiązaniu
   problemu usuń świadomie ten marker (jest lokalny i ignorowany przez Git).
5. Przy konflikcie/rozbieżnej historii address-pr zatrzymuje się na `--ff-only`.

Nie ma automatycznych retry na błędy CLI ani bezterminowych pętli. Limity dotyczą iteracji
review i liczby faz, a timeouts sesji i gates są konfigurowalne. Koszt sesji nie jest
sumowany, ponieważ CLI mają różne formaty i mechanizmy rozliczeń; kontroluj limity konta.

## Zaufanie i dostęp

Commands gates/preflight są wykonywane poza sandboxem modelu przez lokalny runner i mają
uprawnienia procesu użytkownika. Nie uruchamiaj go nad nieprzejrzaną konfiguracją z obcego PR.
Hooki narzędzi i project trust pozostają konfiguracją wybranego CLI. Runner ich nie akceptuje
ani nie przepisuje automatycznie. Najpierw przygotuj wymagany dostęp, następnie uruchom run.

Kod sprawdza wynik sesji i Git po wykonaniu; nie zapobiega każdej szkodliwej operacji w trakcie.
Dla pracy z niezaufanymi treściami używaj odpowiednio ograniczonego środowiska. W szczególności
instrukcje „nie czytaj sekretów” nie zastępują izolacji sekretów od workspace.

## Zakres pierwszej wersji

- Wspólny runner i 14 canonical skills, adaptery Codex/Claude.
- Jedna aktywna operacja na repozytorium; także worktrees są serializowane.
- Lokalna praca domyślnie, GitHub PR i komentarze po `--publish`.
- Brak GitLab, fork PR, automatycznego merge, usług scheduler/background monitor.
- Brak automatycznego tworzenia issues, migracji starego workflow i aktualizacji instalacji.
- Testy bez modeli sprawdzają runner, a nie jakość decyzji modelu lub rzeczywiste logowanie.
- Pilotaż realnych CLI i publikacji wykonaj na małej zmianie w testowym repo aplikacji.

Timeout sesji/gate kończy grupę procesów wraz z dziećmi powłoki. Komentarze są rozpoznawane
po ID; jeśli chcesz zmienić decyzję już obsłużoną, dodaj nowy komentarz zamiast edytować stary.
Rozbieżność snapshotu przy oczekującej odpowiedzi zatrzymuje run i wymaga przeglądu stanu.
