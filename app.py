from flask import Flask, render_template, request
import requests
import json
from urllib.parse import urlparse

app = Flask(__name__)

def check_ucp_capabilities(json_data):
    """Vérifie les capacités UCP spécifiques dans les données JSON"""
    capabilities_to_check = [
        'dev.ucp.shopping.checkout',
        'dev.ucp.common.identity_linking',
        'dev.ucp.shopping.order'
    ]
    
    results = {}
    
    # Chercher les capacités dans différentes structures possibles
    capabilities_data = None
    services_data = None
    
    # Vérifier si les capacités sont directement dans les données
    if isinstance(json_data, dict):
        # Structure 1: capabilities comme clé directe
        if 'capabilities' in json_data:
            capabilities_data = json_data['capabilities']
        # Structure 2: ucp.capabilities
        elif 'ucp' in json_data and isinstance(json_data['ucp'], dict) and 'capabilities' in json_data['ucp']:
            capabilities_data = json_data['ucp']['capabilities']
        # Structure 3: data.capabilities
        elif 'data' in json_data and isinstance(json_data['data'], dict) and 'capabilities' in json_data['data']:
            capabilities_data = json_data['data']['capabilities']
        # Structure 4: les capacités sont directement au niveau racine
        else:
            capabilities_data = json_data
        
        # Chercher les services avec endpoints
        if 'services' in json_data:
            services_data = json_data['services']
        elif 'ucp' in json_data and isinstance(json_data['ucp'], dict) and 'services' in json_data['ucp']:
            services_data = json_data['ucp']['services']
        elif 'data' in json_data and isinstance(json_data['data'], dict) and 'services' in json_data['data']:
            services_data = json_data['data']['services']
    
    if capabilities_data and isinstance(capabilities_data, dict):
        # Analyser les extensions d'abord
        extension_map = build_extension_map(capabilities_data)
        
        for capability in capabilities_to_check:
            capability_result = {'Présence': 'Absent (selon le JSON public, peut être géré côté serveur)', 'Version': 'N/A', 'Endpoint': 'Non accessible', 'Extension': False}
            
            # Vérifier si la capacité est directement présente
            if capability in capabilities_data:
                capability_info = capabilities_data[capability]
                capability_result['Présence'] = 'Présent'
                
                # Extraire la version
                if isinstance(capability_info, dict):
                    if 'version' in capability_info:
                        capability_result['Version'] = str(capability_info['version'])
                    elif 'v' in capability_info:
                        capability_result['Version'] = str(capability_info['v'])
                    elif '__version' in capability_info:
                        capability_result['Version'] = str(capability_info['__version'])
                    else:
                        capability_result['Version'] = 'Non spécifiée'
                elif isinstance(capability_info, str):
                    capability_result['Version'] = capability_info
                else:
                    capability_result['Version'] = 'Inconnue'
            
            # Vérifier si la capacité est étendue par d'autres capacités
            elif capability in extension_map:
                # La capacité est présente via extension
                capability_result['Présence'] = 'Présent (via extension)'
                capability_result['Extension'] = True
                
                # Hériter la version de la capacité de base
                extending_capabilities = extension_map[capability]
                for ext_cap in extending_capabilities:
                    ext_info = capabilities_data.get(ext_cap, {})
                    if isinstance(ext_info, dict):
                        # Utiliser la version de la capacité qui étend si elle n'a pas sa propre version
                        if 'version' in ext_info:
                            capability_result['Version'] = str(ext_info['version'])
                            break
                        elif 'v' in ext_info:
                            capability_result['Version'] = str(ext_info['v'])
                            break
                        elif '__version' in ext_info:
                            capability_result['Version'] = str(ext_info['__version'])
                            break
                
                # Si aucune version trouvée, chercher dans la capacité de base si elle existe
                if capability_result['Version'] == 'N/A':
                    # Chercher une version par défaut ou utiliser Non spécifiée
                    capability_result['Version'] = 'Non spécifiée'
            
            # Vérifier l'accessibilité de l'endpoint réel depuis services
            endpoint_status = check_service_endpoint(capability, services_data)
            capability_result['Endpoint'] = endpoint_status
            
            # Nettoyer le nom de la capacité pour l'affichage
            display_name = capability.replace('dev.ucp.', '').replace('.', ' ').title()
            results[display_name] = capability_result
    
    return results

def build_extension_map(capabilities_data):
    """Construit une carte des extensions pour savoir quelles capacités en étendent d'autres"""
    extension_map = {}
    
    for cap_name, cap_info in capabilities_data.items():
        if isinstance(cap_info, dict) and 'extends' in cap_info:
            extended_capability = cap_info['extends']
            if extended_capability not in extension_map:
                extension_map[extended_capability] = []
            extension_map[extended_capability].append(cap_name)
    
    return extension_map

def check_service_endpoint(capability_name, services_data):
    """Vérifie si l'endpoint d'un service UCP répond avec HTTP 200"""
    if not services_data or not isinstance(services_data, list):
        return 'Non accessible'
    
    # Chercher le service correspondant à la capacité
    for service in services_data:
        if not isinstance(service, dict):
            continue
            
        # Vérifier si ce service correspond à la capacité
        service_capability = service.get('capability') or service.get('name') or service.get('id')
        if service_capability == capability_name:
            # Extraire l'endpoint
            endpoint = service.get('endpoint')
            if not endpoint:
                continue
            
            # Faire une requête HTTP GET
            try:
                response = requests.get(endpoint, timeout=5, allow_redirects=True)
                if response.status_code == 200:
                    return 'Accessible'
                else:
                    return 'Non accessible'
            except requests.exceptions.RequestException:
                return 'Non accessible'
    
    return 'Non accessible'

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    url = ''
    
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        if url:
            try:
                # Add protocol if missing
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                
                # Fetch UCP public profile JSON
                headers = {'Accept': 'application/json'}
                response = requests.get(url, headers=headers, timeout=10)
                
                # Handle specific HTTP errors
                if response.status_code == 404:
                    raise requests.exceptions.HTTPError("Profil UCP non trouvé (404)")
                elif response.status_code == 403:
                    raise requests.exceptions.HTTPError("Accès interdit au profil UCP (403)")
                elif response.status_code >= 500:
                    raise requests.exceptions.HTTPError(f"Erreur serveur UCP ({response.status_code})")
                
                response.raise_for_status()
                
                # Parse JSON response
                try:
                    json_data = response.json()
                except json.JSONDecodeError:
                    raise ValueError("La réponse n'est pas au format JSON valide")
                
                # Check UCP capabilities
                capabilities = check_ucp_capabilities(json_data)
                
                # Format results with French labels
                result = {
                    'Statut': 'Succès',
                    'Code HTTP': f"HTTP {response.status_code}",
                    'Type de contenu': response.headers.get('Content-Type', 'Non spécifié'),
                    'Taille de la réponse': f"{len(response.content)} octets",
                    'Données JSON': json_data,
                    'URL': url
                }
                
                # Add capabilities to results
                if capabilities:
                    result['Capacités UCP'] = capabilities
                
            except requests.exceptions.Timeout:
                result = {
                    'Statut': 'Erreur',
                    'Code HTTP': 'Timeout',
                    'Erreur': 'Impossible d\'accéder au profil UCP - Délai d\'attente dépassé',
                    'URL': url
                }
            except requests.exceptions.ConnectionError:
                result = {
                    'Statut': 'Erreur',
                    'Code HTTP': 'Connexion',
                    'Erreur': 'Impossible d\'accéder au profil UCP - Erreur de connexion',
                    'URL': url
                }
            except requests.exceptions.HTTPError as e:
                result = {
                    'Statut': 'Erreur',
                    'Code HTTP': 'HTTP',
                    'Erreur': f'Impossible d\'accéder au profil UCP - {str(e)}',
                    'URL': url
                }
            except json.JSONDecodeError:
                result = {
                    'Statut': 'Erreur',
                    'Code HTTP': 'JSON',
                    'Erreur': 'Impossible d\'accéder au profil UCP - La réponse n\'est pas un JSON valide',
                    'URL': url
                }
            except ValueError as e:
                result = {
                    'Statut': 'Erreur',
                    'Code HTTP': 'Format',
                    'Erreur': f'Impossible d\'accéder au profil UCP - {str(e)}',
                    'URL': url
                }
            except Exception as e:
                result = {
                    'Statut': 'Erreur',
                    'Code HTTP': 'Inconnue',
                    'Erreur': f'Impossible d\'accéder au profil UCP - Erreur inattendue: {str(e)}',
                    'URL': url
                }
    
    return render_template('index.html', result=result, url=url)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
