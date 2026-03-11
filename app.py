from flask import Flask, render_template, request
import requests
import json
from urllib.parse import urlparse, urljoin

app = Flask(__name__)

def complete_ucp_url(base_url):
    """
    Complète automatiquement une URL de base vers l'URL UCP complète.
    Ex: https://site.com -> https://site.com/.well-known/ucp
    """
    # Normaliser l'URL de base
    if not base_url.startswith(('http://', 'https://')):
        base_url = 'https://' + base_url
    
    # Parser l'URL pour extraire les composants
    parsed = urlparse(base_url)
    
    # Construire l'URL complète UCP
    ucp_path = '/.well-known/ucp'
    complete_url = f"{parsed.scheme}://{parsed.netloc}{ucp_path}"
    
    return complete_url

def verify_ucp_url_exists(url):
    """
    Vérifie si l'URL UCP complète existe et répond correctement.
    Retourne un tuple (exists, response_data)
    """
    try:
        headers = {'Accept': 'application/json'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            try:
                json_data = response.json()
                return True, json_data
            except json.JSONDecodeError:
                return True, None  # URL existe mais pas de JSON
        else:
            return False, None
            
    except requests.exceptions.RequestException:
        return False, None

def infer_capability_presence(capability_name, capabilities_data, services_data):
    """Infère la présence d'une capacité basée sur d'autres endpoints déclarés"""
    
    # Indicateurs pour Identity Linking
    identity_indicators = [
        'identity', 'auth', 'login', 'signin', 'oauth', 'sso', 'profile',
        'user', 'account', 'customer', 'member'
    ]
    
    # Indicateurs pour Order
    order_indicators = [
        'order', 'cart', 'checkout', 'payment', 'purchase', 'billing',
        'transaction', 'invoice', 'receipt', 'shipping', 'delivery'
    ]
    
    # Vérifier les capacités déclarées pour des indicateurs
    for cap_name, cap_info in capabilities_data.items():
        cap_lower = cap_name.lower()
        
        if capability_name == 'dev.ucp.common.identity_linking':
            if any(indicator in cap_lower for indicator in identity_indicators):
                return True, 'Inféré depuis autres capacités'
                
        elif capability_name == 'dev.ucp.shopping.order':
            if any(indicator in cap_lower for indicator in order_indicators):
                return True, 'Inféré depuis autres capacités'
    
    # Vérifier les endpoints des services pour des indicateurs
    if services_data and isinstance(services_data, list):
        for service in services_data:
            if not isinstance(service, dict):
                continue
                
            endpoint = service.get('endpoint', '')
            service_name = service.get('capability', '') or service.get('name', '') or service.get('id', '')
            
            endpoint_lower = endpoint.lower()
            service_lower = service_name.lower()
            
            if capability_name == 'dev.ucp.common.identity_linking':
                if (any(indicator in endpoint_lower for indicator in identity_indicators) or
                    any(indicator in service_lower for indicator in identity_indicators)):
                    return True, 'Inféré depuis endpoints'
                    
            elif capability_name == 'dev.ucp.shopping.order':
                if (any(indicator in endpoint_lower for indicator in order_indicators) or
                    any(indicator in service_lower for indicator in order_indicators)):
                    return True, 'Inféré depuis endpoints'
    
    return False, None

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
            capability_result = {'Présence': 'Non déclaré dans ce profil (mais peut être disponible)', 'Version': 'N/A', 'Endpoint': 'Non accessible', 'Extension': False}
            
            # Vérifier si la capacité est directement présente
            if capability in capabilities_data:
                capability_info = capabilities_data[capability]
                capability_result['Présence'] = 'Présent'
                
                # Extraire la version exacte
                if isinstance(capability_info, dict):
                    if 'version' in capability_info:
                        capability_result['Version'] = str(capability_info['version'])
                    elif 'v' in capability_info:
                        capability_result['Version'] = str(capability_info['v'])
                    elif '__version' in capability_info:
                        capability_result['Version'] = str(capability_info['__version'])
                    elif 'version_number' in capability_info:
                        capability_result['Version'] = str(capability_info['version_number'])
                    elif 'release' in capability_info:
                        capability_result['Version'] = str(capability_info['release'])
                    elif 'build' in capability_info:
                        capability_result['Version'] = str(capability_info['build'])
                    else:
                        capability_result['Version'] = 'Non spécifiée'
                elif isinstance(capability_info, str):
                    capability_result['Version'] = capability_info
                else:
                    capability_result['Version'] = 'Non spécifiée'
            
            # Vérifier si la capacité est étendue par d'autres capacités
            elif capability in extension_map:
                # La capacité est présente via extension
                capability_result['Présence'] = 'Présent (via extension)'
                capability_result['Extension'] = True
                
                # Hériter la version exacte de la capacité qui étend
                extending_capabilities = extension_map[capability]
                for ext_cap in extending_capabilities:
                    ext_info = capabilities_data.get(ext_cap, {})
                    if isinstance(ext_info, dict):
                        # Chercher la version dans tous les champs possibles
                        if 'version' in ext_info:
                            capability_result['Version'] = str(ext_info['version'])
                            break
                        elif 'v' in ext_info:
                            capability_result['Version'] = str(ext_info['v'])
                            break
                        elif '__version' in ext_info:
                            capability_result['Version'] = str(ext_info['__version'])
                            break
                        elif 'version_number' in ext_info:
                            capability_result['Version'] = str(ext_info['version_number'])
                            break
                        elif 'release' in ext_info:
                            capability_result['Version'] = str(ext_info['release'])
                            break
                        elif 'build' in ext_info:
                            capability_result['Version'] = str(ext_info['build'])
                            break
                    elif isinstance(ext_info, str):
                        capability_result['Version'] = ext_info
                        break
                
                # Si aucune version trouvée dans l'extension, utiliser Non spécifiée
                if capability_result['Version'] == 'N/A':
                    capability_result['Version'] = 'Non spécifiée'
            
            # Vérifier l'inférence pour Identity Linking et Order
            elif capability in ['dev.ucp.common.identity_linking', 'dev.ucp.shopping.order']:
                # Essayer d'inférer la présence depuis d'autres endpoints
                inferred, inference_reason = infer_capability_presence(capability, capabilities_data, services_data)
                if inferred:
                    capability_result['Présence'] = f'Présent (inféré - {inference_reason})'
                    capability_result['Version'] = 'Non spécifiée'
                else:
                    # Garder le message par défaut pour les capacités absentes
                    pass
            
            # Vérifier l'accessibilité de l'endpoint réel depuis services
            endpoint_status = check_service_endpoint(capability, services_data)
            capability_result['Endpoint'] = endpoint_status
            
            # Pour Checkout, toujours vérifier aussi l'endpoint MCP
            if capability == 'dev.ucp.shopping.checkout':
                mcp_status = check_mcp_endpoint_for_checkout(services_data)
                capability_result['Endpoint MCP'] = mcp_status
            
            # Nettoyer le nom de la capacité pour l'affichage
            display_name = capability.replace('dev.ucp.', '').replace('.', ' ').title()
            results[display_name] = capability_result
        
        # Ajouter les capacités qui étendent d'autres capacités
        for ext_cap_name, ext_cap_info in capabilities_data.items():
            if isinstance(ext_cap_info, dict) and 'extends' in ext_cap_info:
                extended_capability = ext_cap_info['extends']
                
                # Vérifier si la capacité étendue est dans notre liste de vérification
                if extended_capability in capabilities_to_check:
                    # Créer un résultat pour la capacité qui étend
                    ext_result = {'Présence': 'Présent', 'Version': 'N/A', 'Endpoint': 'Non accessible', 'Extension': True, 'Extends': extended_capability}
                    
                    # Extraire la version de l'extension
                    if 'version' in ext_cap_info:
                        ext_result['Version'] = str(ext_cap_info['version'])
                    elif 'v' in ext_cap_info:
                        ext_result['Version'] = str(ext_cap_info['v'])
                    elif '__version' in ext_cap_info:
                        ext_result['Version'] = str(ext_cap_info['__version'])
                    elif 'version_number' in ext_cap_info:
                        ext_result['Version'] = str(ext_cap_info['version_number'])
                    elif 'release' in ext_cap_info:
                        ext_result['Version'] = str(ext_cap_info['release'])
                    elif 'build' in ext_cap_info:
                        ext_result['Version'] = str(ext_cap_info['build'])
                    else:
                        ext_result['Version'] = 'Non spécifiée'
                    
                    # Vérifier l'endpoint de l'extension
                    endpoint_status = check_service_endpoint(ext_cap_name, services_data)
                    ext_result['Endpoint'] = endpoint_status
                    
                    # Nettoyer le nom et ajouter l'information sur l'extension
                    ext_display_name = ext_cap_name.replace('dev.ucp.', '').replace('.', ' ').title()
                    base_name = extended_capability.replace('dev.ucp.', '').replace('.', ' ').title()
                    ext_display_name_with_via = f"{ext_display_name} (via {base_name})"
                    
                    results[ext_display_name_with_via] = ext_result
    
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

def check_mcp_endpoint_for_checkout(services_data):
    """Vérifie spécifiquement les endpoints MCP pour Checkout"""
    if not services_data or not isinstance(services_data, list):
        return 'Non testé'
    
    # Chercher tous les services pour Checkout
    checkout_endpoints = []
    for service in services_data:
        if not isinstance(service, dict):
            continue
            
        # Vérifier si ce service correspond à Checkout
        service_capability = service.get('capability') or service.get('name') or service.get('id')
        if service_capability == 'dev.ucp.shopping.checkout':
            endpoint = service.get('endpoint')
            if endpoint:
                checkout_endpoints.append(endpoint)
    
    if not checkout_endpoints:
        return 'Non testé'
    
    # Tester chaque endpoint MCP
    for endpoint in checkout_endpoints:
        try:
            response = requests.get(endpoint, timeout=5, allow_redirects=True)
            if response.status_code == 200:
                return 'Endpoint MCP disponible'
        except requests.exceptions.RequestException:
            continue  # Essayer l'endpoint suivant
    
    return 'Non accessible'

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
                # Étape 1: Compléter automatiquement l'URL UCP
                ucp_url = complete_ucp_url(url)
                
                # Étape 2: Vérifier si l'URL UCP complète existe
                url_exists, json_data = verify_ucp_url_exists(ucp_url)
                
                if not url_exists:
                    # Si l'URL UCP n'existe pas, essayer l'URL originale
                    # Add protocol if missing
                    if not url.startswith(('http://', 'https://')):
                        url = 'https://' + url
                    
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
                    
                    final_url = url
                else:
                    # L'URL UCP complète existe, utiliser celle-ci
                    final_url = ucp_url
                    if json_data is None:
                        raise ValueError("L'URL UCP existe mais ne contient pas de JSON valide")
                
                # Check UCP capabilities
                capabilities = check_ucp_capabilities(json_data)
                
                # Format results with French labels
                result = {
                    'Statut': 'Succès',
                    'Code HTTP': 'HTTP 200',
                    'Type de contenu': 'application/json',
                    'Taille de la réponse': f"{len(str(json_data))} octets",
                    'Données JSON': json_data,
                    'URL': final_url,
                    'URL originale': url,
                    'URL complétée': ucp_url if url_exists else 'Non utilisée'
                }
                
                # Add capabilities to results
                if capabilities:
                    result['Capacités UCP'] = capabilities
                
            except requests.exceptions.Timeout:
                result = {
                    'Statut': 'Erreur',
                    'Code HTTP': 'Timeout',
                    'Erreur': 'Impossible d\'accéder au profil UCP - Délai d\'attente dépassé',
                    'URL': url,
                    'URL complétée': ucp_url
                }
            except requests.exceptions.ConnectionError:
                result = {
                    'Statut': 'Erreur',
                    'Code HTTP': 'Connexion',
                    'Erreur': 'Impossible d\'accéder au profil UCP - Erreur de connexion',
                    'URL': url,
                    'URL complétée': ucp_url
                }
            except requests.exceptions.HTTPError as e:
                result = {
                    'Statut': 'Erreur',
                    'Code HTTP': 'HTTP',
                    'Erreur': f'Impossible d\'accéder au profil UCP - {str(e)}',
                    'URL': url,
                    'URL complétée': ucp_url
                }
            except json.JSONDecodeError:
                result = {
                    'Statut': 'Erreur',
                    'Code HTTP': 'JSON',
                    'Erreur': 'Impossible d\'accéder au profil UCP - La réponse n\'est pas un JSON valide',
                    'URL': url,
                    'URL complétée': ucp_url
                }
            except ValueError as e:
                result = {
                    'Statut': 'Erreur',
                    'Code HTTP': 'Format',
                    'Erreur': f'Impossible d\'accéder au profil UCP - {str(e)}',
                    'URL': url,
                    'URL complétée': ucp_url
                }
            except Exception as e:
                result = {
                    'Statut': 'Erreur',
                    'Code HTTP': 'Inconnue',
                    'Erreur': f'Impossible d\'accéder au profil UCP - Erreur inattendue: {str(e)}',
                    'URL': url,
                    'URL complétée': ucp_url
                }
    
    return render_template('index.html', result=result, url=url)

@app.route('/shop-simulation', methods=['POST'])
def shop_simulation():
    result = None
    product_query = request.form.get('product_query', '').strip()
    shop_url = request.form.get('shop_url', '').strip()
    
    if product_query and shop_url:
        try:
            # Normaliser l'URL du site marchand
            if not shop_url.startswith(('http://', 'https://')):
                shop_url = 'https://' + shop_url
            
            # Compléter automatiquement l'URL UCP pour le site marchand
            ucp_url = complete_ucp_url(shop_url)
            
            # Vérifier si l'URL UCP complète existe
            url_exists, json_data = verify_ucp_url_exists(ucp_url)
            
            if not url_exists:
                # Si l'URL UCP n'existe pas, essayer l'URL originale
                headers = {'Accept': 'application/json'}
                response = requests.get(shop_url, headers=headers, timeout=10)
                
                if response.status_code == 404:
                    raise requests.exceptions.HTTPError("Site marchand non trouvé (404)")
                elif response.status_code == 403:
                    raise requests.exceptions.HTTPError("Accès interdit au site marchand (403)")
                elif response.status_code >= 500:
                    raise requests.exceptions.HTTPError(f"Erreur serveur ({response.status_code})")
                
                response.raise_for_status()
                
                final_url = shop_url
                ucp_available = False
            else:
                # L'URL UCP complète existe
                final_url = ucp_url
                ucp_available = True
                if json_data is None:
                    raise ValueError("L'URL UCP existe mais ne contient pas de JSON valide")
            
            # Simuler la recherche de produit
            search_result = simulate_product_search(product_query, json_data if ucp_available else None, final_url)
            
            # Format results
            result = {
                'Statut': 'Succès',
                'Type': 'Simulation Agent Shop',
                'Produit recherché': product_query,
                'Site marchand': shop_url,
                'URL utilisée': final_url,
                'UCP disponible': 'Oui' if ucp_available else 'Non',
                'Résultat simulation': search_result
            }
            
        except requests.exceptions.Timeout:
            result = {
                'Statut': 'Erreur',
                'Type': 'Simulation Agent Shop',
                'Erreur': 'Impossible d\'accéder au site marchand - Délai d\'attente dépassé',
                'Produit recherché': product_query,
                'Site marchand': shop_url
            }
        except requests.exceptions.ConnectionError:
            result = {
                'Statut': 'Erreur',
                'Type': 'Simulation Agent Shop',
                'Erreur': 'Impossible d\'accéder au site marchand - Erreur de connexion',
                'Produit recherché': product_query,
                'Site marchand': shop_url
            }
        except requests.exceptions.HTTPError as e:
            result = {
                'Statut': 'Erreur',
                'Type': 'Simulation Agent Shop',
                'Erreur': f'Impossible d\'accéder au site marchand - {str(e)}',
                'Produit recherché': product_query,
                'Site marchand': shop_url
            }
        except ValueError as e:
            result = {
                'Statut': 'Erreur',
                'Type': 'Simulation Agent Shop',
                'Erreur': f'Erreur lors de la simulation - {str(e)}',
                'Produit recherché': product_query,
                'Site marchand': shop_url
            }
        except Exception as e:
            result = {
                'Statut': 'Erreur',
                'Type': 'Simulation Agent Shop',
                'Erreur': f'Erreur inattendue lors de la simulation: {str(e)}',
                'Produit recherché': product_query,
                'Site marchand': shop_url
            }
    
    return render_template('index.html', result=result, url='', shop_mode=True)

def simulate_product_search(product_query, ucp_data, site_url):
    """
    Simule une recherche de produit en utilisant les données UCP si disponibles
    """
    simulation_result = {
        'message': f"Simulation de recherche pour '{product_query}'",
        'method_used': 'UCP' if ucp_data else 'HTTP standard',
        'site_url': site_url
    }
    
    if ucp_data:
        # Analyser les capacités UCP pour la recherche
        capabilities = check_ucp_capabilities(ucp_data)
        
        # Vérifier si les capacités de recherche sont disponibles
        search_capabilities = []
        for cap_name, cap_info in capabilities.items():
            if 'search' in cap_name.lower() or 'product' in cap_name.lower():
                search_capabilities.append({
                    'name': cap_name,
                    'status': cap_info.get('Présence', 'Inconnu'),
                    'endpoint': cap_info.get('Endpoint', 'Non accessible')
                })
        
        if search_capabilities:
            simulation_result['capacités_recherche'] = search_capabilities
            simulation_result['message'] += f" - {len(search_capabilities)} capacité(s) de recherche trouvée(s)"
        else:
            simulation_result['message'] += " - Aucune capacité de recherche spécifique trouvée"
        
        # Ajouter les informations UCP
        simulation_result['donnees_ucp'] = ucp_data
    else:
        simulation_result['message'] += " - Utilisation des méthodes HTTP standard"
        simulation_result['note'] = "Le site ne semble pas avoir de profil UCP disponible"
    
    return simulation_result

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
