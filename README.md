# UCP Profile Analyzer

Application web pour analyser les profils publics UCP et vérifier leurs capacités avec détection d'extensions et vérification réelle des endpoints.

## 🚀 Démarrage

### 1. Installation des dépendances
```bash
pip install flask requests
```

### 2. Lancement de l'application
```bash
python app.py
```

L'application démarre sur `http://localhost:5002`

## 📖 Utilisation

### Étape 1: Accéder à l'interface
Ouvrez votre navigateur et allez sur `http://localhost:5002`

### Étape 2: Entrer l'URL du profil UCP
Dans le champ "URL du profil UCP", entrez l'URL complète du profil que vous voulez analyser.

**Exemples:**
- `https://api.example.com/ucp/profile/user123`
- `https://api.ucp-service.com/v1/users/456/profile`
- `api.monucp.com/profile/abc123` (HTTPS sera ajouté automatiquement)

### Étape 3: Cliquer sur "Analyser"
Cliquez sur le bouton **"Analyser"** pour lancer l'analyse.

### Étape 4: Consulter les résultats
L'application affiche les résultats en français avec :

#### 📊 Informations générales
- **Statut**: Succès/Erreur
- **Code HTTP**: Status de la réponse
- **Type de contenu**: Format de la réponse
- **Taille de la réponse**: Taille en octets
- **Données JSON**: Le profil JSON complet

#### 🔍 Analyse des capacités UCP
Un tableau détaillé montre pour chaque capacité :

| Capacité | Présence | Version | Endpoint |
|----------|----------|---------|----------|

**Types de présence:**
- 🟢 **Présent** - Capacité directement déclarée dans le JSON
- 🟢 **Présent (via extension)** - Capacité inférée via le champ `extends`
- 🔴 **Absent (selon le JSON public, peut être géré côté serveur)** - Non déclaré mais可能 géré côté serveur

**Types d'endpoint:**
- 🟢 **Accessible** - Endpoint répond HTTP 200
- 🔴 **Non accessible** - Endpoint ne répond pas ou erreur

## 🎯 Capacités vérifiées

L'application vérifie automatiquement ces 3 capacités UCP :

1. **dev.ucp.shopping.checkout** - Capacité de paiement
2. **dev.ucp.common.identity_linking** - Liaison d'identité  
3. **dev.ucp.shopping.order** - Gestion des commandes

## 🔧 Fonctionnalités avancées

### 📋 Détection d'extensions
L'application détecte automatiquement quand une capacité en étend une autre :

**Exemple de JSON:**
```json
{
  "capabilities": {
    "dev.ucp.shopping.checkout": {"version": "2.1.0"},
    "dev.ucp.shopping.advanced_checkout": {
      "version": "3.0.0",
      "extends": "dev.ucp.shopping.checkout"
    }
  }
}
```

**Résultat:** Shopping Checkout s'affiche comme "Présent (via extension)"

### 🌐 Vérification réelle des endpoints
L'application utilise les endpoints réels déclarés dans la section `services`:

**Exemple de JSON:**
```json
{
  "services": [
    {
      "capability": "dev.ucp.shopping.checkout",
      "endpoint": "https://api.example.com/checkout/health"
    }
  ]
}
```

L'application fait une requête HTTP GET réelle à cet endpoint et retourne:
- **Accessible** si HTTP 200
- **Non accessible** sinon

### 🧬 Héritage de version
Quand une capacité est présente via extension, la version est héritée de la capacité qui l'étend si elle n'a pas sa propre version.

### 📝 Messages clarifiés
Pour les capacités absentes du JSON public, le message précise:
> "Absent (selon le JSON public, peut être géré côté serveur)"

Cela indique que l'absence dans le JSON public ne signifie pas nécessairement que le site ne peut pas gérer cette capacité.

## 🏗️ Formats JSON supportés

L'application peut analyser les profils UCP dans différentes structures :

### Structure des capacités
- `capabilities` au niveau racine
- `ucp.capabilities` imbriqué
- `data.capabilities` imbriqué
- Capacités directement au niveau racine

### Structure des services
- `services` au niveau racine
- `ucp.services` imbriqué
- `data.services` imbriqué

## 📋 Exemple complet

**JSON d'entrée:**
```json
{
  "capabilities": {
    "dev.ucp.shopping.checkout": {"version": "2.1.0"},
    "dev.ucp.shopping.advanced_checkout": {
      "version": "3.0.0",
      "extends": "dev.ucp.shopping.checkout"
    },
    "dev.ucp.common.identity_linking": {"version": "1.5.2"}
  },
  "services": [
    {
      "capability": "dev.ucp.shopping.checkout",
      "endpoint": "https://api.example.com/checkout/health"
    },
    {
      "capability": "dev.ucp.common.identity_linking",
      "endpoint": "https://identity.example.com/status"
    }
  ]
}
```

**Résultat affiché:**
| Capacité | Présence | Version | Endpoint |
|----------|----------|---------|----------|
| Shopping Checkout | Présent | 2.1.0 | Accessible |
| Common Identity Linking | Présent | 1.5.2 | Non accessible |
| Shopping Order | Absent (selon le JSON public, peut être géré côté serveur) | N/A | Non accessible |

## ⚠️ Messages d'erreur

En cas de problème, l'application affiche des messages clairs en français :

- **"Impossible d'accéder au profil UCP - Délai d'attente dépassé"**
- **"Impossible d'accéder au profil UCP - Erreur de connexion"**
- **"Impossible d'accéder au profil UCP - Profil UCP non trouvé (404)"**
- **"Impossible d'accéder au profil UCP - La réponse n'est pas un JSON valide"**

## 📱 Interface responsive

L'interface s'adapte automatiquement aux mobiles et tablettes pour une utilisation optimale sur tous les appareils.

## 🛠️ Dépannage

### Problèmes courants
1. **"Non accessible" pour les endpoints**: Normal si les endpoints de test n'existent pas
2. **Timeout**: Vérifiez la connexion et l'URL (timeout de 5 secondes)
3. **JSON invalide**: Assurez-vous que l'URL retourne du JSON valide

### Logs de développement
En mode debug, les erreurs détaillées s'affichent dans la console.

### Tests unitaires
Pour tester les fonctionnalités:
```bash
python test_complete_integration.py
python test_extensions.py
python test_absent_message.py
```

## 🎨 Personnalisation

### Ajouter de nouvelles capacités
Modifiez la liste `capabilities_to_check` dans `app.py`:
```python
capabilities_to_check = [
    'dev.ucp.shopping.checkout',
    'dev.ucp.common.identity_linking', 
    'dev.ucp.shopping.order',
    'dev.ucp.votre.nouvelle.capacite'  # Ajoutez ici
]
```

### Modifier le port
Changez le port dans la dernière ligne de `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=VOTRE_PORT)
```

---

**Développé avec Flask, Python 3.13+**
**Toutes les fonctionnalités en français**
