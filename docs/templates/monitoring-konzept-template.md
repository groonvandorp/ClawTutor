# Monitoring-Konzept

**Projekt:** [Projektname]  
**Version:** 1.0  
**Datum:** [TT.MM.JJJJ]  
**Autor:** [Name]  
**Status:** Entwurf | Review | Freigegeben

---

## 1. Einleitung

### 1.1 Zweck
Dieses Dokument definiert das Monitoring-Konzept für [System/Service] und beschreibt, wie die Überwachung der Sicherheit, Verfügbarkeit und Compliance gewährleistet wird.

### 1.2 Scope
| In Scope | Out of Scope |
|----------|--------------|
| [System A] | [Legacy-System X] |
| [Cloud-Service B] | [Endgeräte] |

### 1.3 Referenzen
- DHL CIS 2025 (05.23.CIS, 05.27.CIS, 07.3.CIS)
- ISO/IEC 27001:2022
- [Firmenspezifische Policies]

---

## 2. Rollen & Verantwortlichkeiten

| Rolle | Verantwortung | Kontakt |
|-------|---------------|---------|
| **Security Architect** | Konzept-Design, Review | [Name] |
| **SOC / Security Operations** | 24/7 Monitoring, Incident Response | [Team] |
| **System Owner** | Bereitstellung Log-Quellen, Eskalation | [Name] |
| **Cloud Provider** | Infrastruktur-Monitoring (gem. SLA) | [Provider] |
| **CISO** | Freigabe, Reporting an Management | [Name] |

---

## 3. Monitoring-Architektur

### 3.1 Übersicht

```
┌─────────────────────────────────────────────────────────────┐
│                        Log-Quellen                          │
├──────────┬──────────┬──────────┬──────────┬────────────────┤
│ Server   │ Firewall │ Cloud    │ Applik.  │ Identity Mgmt  │
└────┬─────┴────┬─────┴────┬─────┴────┬─────┴───────┬────────┘
     │          │          │          │             │
     └──────────┴──────────┴──────────┴─────────────┘
                           │
                    ┌──────▼──────┐
                    │  Log Shipper │  (Filebeat, Fluentd, etc.)
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │    SIEM      │  (Splunk, Elastic, Sentinel)
                    └──────┬──────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────▼─────┐   ┌──────▼──────┐   ┌─────▼─────┐
    │ Dashboards │   │   Alerting   │   │ Reporting │
    └───────────┘   └──────────────┘   └───────────┘
```

### 3.2 Eingesetzte Tools

| Funktion | Tool | Verantwortlich |
|----------|------|----------------|
| SIEM | [z.B. Splunk, Microsoft Sentinel] | SOC |
| Log Collection | [z.B. Filebeat, Fluentd] | Ops |
| Alerting | [z.B. PagerDuty, OpsGenie] | SOC |
| Dashboards | [z.B. Grafana, Kibana] | Security |
| Vulnerability Scanning | [z.B. Qualys, Nessus] | Security |

---

## 4. Monitoring-Bereiche

### 4.1 Security Monitoring

| Event-Typ | Quelle | Erkennung | Beispiel |
|-----------|--------|-----------|----------|
| Brute-Force | IAM, Firewall | >5 fehlgeschl. Logins/Min | Account-Lockout |
| Privilege Escalation | AD, IAM | Rollenzuweisung Admin | Alert + Ticket |
| Malware | Endpoint, AV | Signatur-Match | Isolation + Alert |
| Data Exfiltration | DLP, Proxy | Ungewöhnl. Upload-Volumen | Alert + Block |
| Anomalous Behavior | UEBA | Abweichung vom Baseline | Alert zur Prüfung |

### 4.2 Availability Monitoring

| Komponente | Metrik | Schwellwert | Aktion |
|------------|--------|-------------|--------|
| Webserver | Response Time | > 2s | Alert |
| Datenbank | CPU | > 80% | Alert + Scale |
| API | Error Rate | > 1% | Alert |
| Storage | Kapazität | > 85% | Alert + Cleanup |

### 4.3 Compliance Monitoring

| Anforderung | Monitoring | Nachweis |
|-------------|------------|----------|
| Zugriff auf Confidential-Daten | Log aller Zugriffe | Quartalsreport |
| Admin-Aktivitäten | Privileged Access Logging | Audit Trail |
| Datenaufbewahrung | Retention Policy Check | Automatisiert |

---

## 5. Log-Management

### 5.1 Log-Quellen

| Quelle | Log-Typ | Format | Transport |
|--------|---------|--------|-----------|
| Linux Server | syslog, auth.log | Syslog | Filebeat → SIEM |
| Windows Server | Security Event Log | EVTX | Winlogbeat → SIEM |
| Firewall | Traffic, Threat | CEF | Syslog → SIEM |
| Cloud (AWS/Azure) | CloudTrail/Activity | JSON | Native → SIEM |
| Applikation | App-Logs | JSON | Fluentd → SIEM |

### 5.2 Retention (Aufbewahrung)

| Datenklasse | Hot Storage | Warm Storage | Cold/Archive | Gesamt |
|-------------|-------------|--------------|--------------|--------|
| Security Logs | 30 Tage | 90 Tage | 12 Monate | 15 Monate |
| Access Logs | 30 Tage | 60 Tage | 6 Monate | 9 Monate |
| Debug Logs | 7 Tage | — | — | 7 Tage |

### 5.3 Log-Integrität

- [ ] Logs werden verschlüsselt transportiert (TLS)
- [ ] Logs werden im SIEM vor Manipulation geschützt (Write-Once)
- [ ] Checksummen für kritische Logs
- [ ] Zugriffsrechte auf Logs eingeschränkt (Need-to-Know)

---

## 6. Alerting & Eskalation

### 6.1 Severity-Matrix

| Severity | Beschreibung | Reaktionszeit | Eskalation |
|----------|--------------|---------------|------------|
| **P1 - Critical** | Aktiver Angriff, Datenverlust, Ausfall Kernsystem | 15 Min | SOC → CISO → Management |
| **P2 - High** | Verdächtiger Incident, Teilausfall | 1 Stunde | SOC → Team Lead |
| **P3 - Medium** | Anomalie, Regelverstoß | 4 Stunden | SOC → Ticket |
| **P4 - Low** | Info, Optimierungsbedarf | Nächster BD | Ticket |

### 6.2 Eskalationspfad

```
         ┌─────────────────┐
         │   Alert fired   │
         └────────┬────────┘
                  │
         ┌────────▼────────┐
         │   SOC Analyst   │ ◄── 24/7
         └────────┬────────┘
                  │ P1/P2 nicht gelöst in SLA
         ┌────────▼────────┐
         │   SOC Lead      │
         └────────┬────────┘
                  │ Eskalation
         ┌────────▼────────┐
         │   CISO / ISIRT  │
         └────────┬────────┘
                  │ Major Incident
         ┌────────▼────────┐
         │  Crisis Mgmt    │
         └─────────────────┘
```

### 6.3 Benachrichtigungskanäle

| Severity | Kanal | Empfänger |
|----------|-------|-----------|
| P1 | Telefon + SMS + E-Mail | On-Call, CISO |
| P2 | SMS + E-Mail | On-Call, Team Lead |
| P3 | E-Mail + Ticket | SOC, System Owner |
| P4 | Ticket | System Owner |

---

## 7. Incident Response Integration

Bei Security Incidents gilt:

1. **Detection** → Alert aus SIEM
2. **Triage** → SOC bewertet, klassifiziert
3. **Containment** → Isolation, Block (wenn automatisiert: Playbook)
4. **Eradication** → Root Cause beheben
5. **Recovery** → System wiederherstellen
6. **Lessons Learned** → Post-Incident Review

Verweis auf: [Incident Response Plan]

---

## 8. Cloud Provider Monitoring (Shared Responsibility)

### 8.1 Verantwortlichkeitsmatrix

| Aspekt | Provider | DHL/Kunde |
|--------|----------|-----------|
| Physische Sicherheit DC | ✓ | — |
| Hypervisor-Sicherheit | ✓ | — |
| Netzwerk-Infrastruktur | ✓ | — |
| OS-Patching (IaaS) | — | ✓ |
| Applikations-Logs | — | ✓ |
| IAM-Konfiguration | — | ✓ |
| Security Alerts (native) | ✓ | Konsumieren |

### 8.2 Provider-Anforderungen (gem. CIS 05.23.CIS.7)

- [ ] 24/7 Monitoring durch Provider
- [ ] Regelmäßige Monitoring-Reports an Kunden
- [ ] Erkennung externer UND interner Angriffe
- [ ] Sofortige Meldung von Incidents an Kunden

### 8.3 Datenexport

| Datentyp | Export-Methode | Frequenz |
|----------|----------------|----------|
| CloudTrail/Activity Logs | API → SIEM | Real-time |
| Security Alerts | Webhook | Real-time |
| Compliance Reports | Portal Download | Monatlich |

---

## 9. Reporting

### 9.1 Regelmäßige Reports

| Report | Frequenz | Empfänger | Inhalt |
|--------|----------|-----------|--------|
| SOC Daily Brief | Täglich | SOC Team | Incidents, offene Tickets |
| Security Weekly | Wöchentlich | IT Security, Ops | Trends, Top Alerts |
| Management Report | Monatlich | CISO, Management | KPIs, Risiken, Empfehlungen |
| Compliance Report | Quartalsweise | Audit, Compliance | Control-Erfüllung |

### 9.2 KPIs

| KPI | Beschreibung | Ziel |
|-----|--------------|------|
| **MTTD** | Mean Time to Detect | < 1h |
| **MTTR** | Mean Time to Respond | < 4h (P1/P2) |
| **False Positive Rate** | Fehlalarme / Gesamt | < 20% |
| **Alert Coverage** | Überwachte Assets / Gesamt | > 95% |
| **Log Ingestion Rate** | Events/Sekunde | [Baseline] |

---

## 10. Review & Wartung

### 10.1 Review-Zyklus

| Aktivität | Frequenz | Verantwortlich |
|-----------|----------|----------------|
| Alert-Rule Tuning | Monatlich | SOC |
| Konzept-Review | Jährlich (mind. alle 2 Jahre) | Security Architect |
| Tool-Evaluation | Jährlich | Security + Ops |
| Playbook-Test | Halbjährlich | SOC |

### 10.2 Änderungshistorie

| Version | Datum | Autor | Änderung |
|---------|-------|-------|----------|
| 1.0 | [Datum] | [Name] | Initiale Version |
| | | | |

---

## Anhang

### A. Glossar

| Begriff | Definition |
|---------|------------|
| SIEM | Security Information and Event Management |
| SOC | Security Operations Center |
| MTTD | Mean Time to Detect |
| MTTR | Mean Time to Respond |
| ISIRT | Information Security Incident Response Team |

### B. Kontakte

| Rolle | Name | Telefon | E-Mail |
|-------|------|---------|--------|
| SOC 24/7 | | | |
| CISO | | | |
| Cloud Provider Support | | | |

### C. Verwandte Dokumente

- Incident Response Plan
- Business Continuity Plan
- Cloud Security Concept
- Data Classification Policy
