# Architektura i kontrakty

## Trzy warstwy

1. **Metodyka:** canonical `workflow/skills/mw-*/SKILL.md` oraz autonomy.md. W aplikacji oba
   katalogi discovery wskazują dowiązaniami na te same pliki.
2. **Runner:** planuje wykonanie kroków, sprawdza artefakty, uruchamia gates, zapisuje
   potwierdzenia, zarządza commitem i PR. Python standard library, bez usług centralnych.
3. **Adapter:** buduje argv i przekazuje jawny prompt przez stdin do świeżego procesu CLI.
   Wyjściowy JSONL jest logiem diagnostycznym, nie źródłem stanu przebiegu.

Nie zakładamy, że YAML `context: fork`, `$ARGUMENTS`, nazwa narzędzia do pytań lub procesów
w tle jest wspólna między silnikami. Niezależny review oznacza nowy proces z plikami jako
wejściem; reviewer nie dziedziczy historii planowania lub implementacji.

## Artefakty

| Artefakt | Autor / znaczenie |
|----------|-------------------|
| shape-notes, prd, tech-stack, roadmap, test-plan | Interaktywne projektowanie |
| changes/id/plan.md | Cele, decyzje, fazy, human checks, odchylenia |
| plan-review.md | READY / READY WITH NOTES / NEEDS CHANGES |
| mutation.md | Raport lub jawny powód pominięcia |
| review.md | APPROVE / APPROVE WITH FOLLOW-UPS / CHANGES REQUESTED |
| pr-body.md | Tytuł w pierwszej linii `# ` i opis PR |
| replies.md | Odpowiedź dla każdego autoryzowanego komentarza |
| .workflow/id/state.json | Lokalny cache potwierdzeń z hashami wejść i wyjść |
| .workflow/id/gates.json | Wyniki commands dla danego fingerprintu wejść |

Format planu i review znajduje się w odpowiednich skills. Markdown ma ścisłe linie
`Verdict:` i `- Decision: open`; zmiana ich formatu powoduje odrzucenie kroku.
Fazy muszą mieć kolejne numery i być ukończone w kolejności. Implementacja zaznacza dokładnie
jedną fazę; runner weryfikuje różnicę i wykonuje commit z `Refs #n`.

## Aktualność dowodów

Fingerprint aplikacji obejmuje nazwy, zawartość i tryby plików w Git oraz nieignorowane
nowe pliki, poza `context/` i runtime `.workflow/`. Dodatkowo potwierdzenia obejmują plan,
PRD, tech stack, test plan, lessons i konfigurację. Hash artefaktu wykrywa jego podmianę.
Zmiana opisu PR nie unieważnia review kodu. Zmiana checkboxów Progress nie unieważnia
zaakceptowanego projektu, ale nowe decyzje i pozostała treść planu wymagają nowego review.

Runner uruchamia final gates po poprawkach i nowy code review, zamiast uznawać samą triage
findings za zgodę reviewera. Wykonanie powtórnego review może zapisać identyczny raport;
liczy się jego zapis w nowej sesji i aktualny fingerprint, nie wymuszona zmiana treści.

## Git i publikacja

Agent dostaje instrukcję „nie modyfikuj historii Git”. Runner kontroluje branch i HEAD po
sesji oraz commituje konkretne zmienione ścieżki. To kontrola po wykonaniu, nie zapora
przeciw celowo nieposłusznemu agentowi. Właściwą granicą są uprawnienia CLI i środowisko.

Runner wymaga czystego drzewa również dla plików nieśledzonych. Po błędzie zachowuje diff.
Nie ma automatycznego stasha, resetu, force push ani WIP z masowym stage. Commity projektu
można weryfikować dodatkowo normalnymi hookami Git (runner ich nie omija).

Publikacja wymaga `--publish`, robi zwykły push i idempotentnie tworzy/aktualizuje otwarty
PR dla branch. Ustawia draft, gdy dowody są nieaktualne lub run jest niekompletny.
Scalanie należy do człowieka. Adresowanie komentarzy wymaga osobnej jawnej komendy i
filtruje autorów przed przekazaniem danych modelowi.
