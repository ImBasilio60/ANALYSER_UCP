# UCP Analyzer

Script Python pour analyser les profils UCP (Universal Commerce Protocol).

## Installation

```bash
pip install requests
```

## Utilisation

### Avec le site par défaut
```bash
python ucp_analyzer.py
```

### Avec un site spécifique
```bash
python ucp_analyzer.py https://example.com
```

## Configuration

Modifiez la variable `TARGET_SITE` dans le script pour changer le site par défaut.

## Résultat

Le script retourne un JSON avec :
- Statut de l'analyse
- Données UCP brutes
- Capacités détectées (Checkout, Identity Linking, Order)
- Versions et endpoints accessibles

## Exemple de sortie

```json
{
  "Statut": "Succès",
  "Code HTTP": "HTTP 200",
  "Capacités UCP": {
    "Shopping Checkout": {
      "Présence": "Présent",
      "Version": "2026-01-23",
      "Endpoint": "Accessible"
    }
  }
}
```
