# Add-on: Learning Styles (VARK)

Optionale Erweiterung für ClawTutor, die den Lerntyp des Kindes ermittelt und den Tutor-Stil entsprechend anpasst.

## Was ist das?

Basiert auf dem VARK-Modell:
- **V**isual — lernt durch Bilder, Diagramme, räumliche Darstellung
- **A**uditory — lernt durch Hören, Erklären, Diskussion
- **R**ead/Write — lernt durch Lesen, Listen, Notizen
- **K**inesthetic — lernt durch Anfassen, Ausprobieren, Bewegung

## Installation

1. Kopiere `PROFILE_TEMPLATE.md` in den Kind-Workspace als `LEARNING_PROFILE.md`
2. Füge den Inhalt von `tutor-patch.md` in die SOUL.md des Tutors ein
3. Optional: Nutze `ONBOARDING.md` für den Lerntyp-Test beim ersten Kontakt

## Dateien

| Datei | Zweck |
|-------|-------|
| `README.md` | Diese Anleitung |
| `ONBOARDING.md` | 4-Fragen-Test zur Lerntyp-Ermittlung |
| `PROFILE_TEMPLATE.md` | Vorlage für das Lernprofil |
| `tutor-patch.md` | Ergänzung für die Tutor-SOUL.md |

## Nutzung

### Mit Onboarding (empfohlen)
Beim ersten Kontakt führt der Tutor den kurzen Test durch und erstellt das Profil automatisch.

### Ohne Onboarding
Eltern/Lehrer können das Profil auch manuell ausfüllen, wenn sie den Lerntyp schon kennen.

### Deaktivieren
Einfach `LEARNING_PROFILE.md` löschen oder `lerntyp: unbekannt` setzen — der Tutor verhält sich dann neutral.

## Hinweis

Das VARK-Modell ist ein vereinfachtes Werkzeug. Kinder sind keine festen Typen — die meisten lernen multimodal. Der Tutor nutzt den Lerntyp als Startpunkt, nicht als Schublade.
