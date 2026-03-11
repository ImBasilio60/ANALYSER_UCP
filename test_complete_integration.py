#!/usr/bin/env python3
"""
Test complet pour vérifier que toutes les améliorations fonctionnent ensemble
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import check_ucp_capabilities

def test_all_features_together():
    """Test complet avec toutes les fonctionnalités: extensions, endpoints HTTP, notes d'absence"""
    
    comprehensive_test_data = {
        "capabilities": {
            # Capacité directement présente
            "dev.ucp.shopping.checkout": {
                "version": "2.1.0",
                "enabled": True,
                "last_updated": "2024-01-15"
            },
            # Capacité qui étend checkout
            "dev.ucp.shopping.advanced_checkout": {
                "version": "3.0.0",
                "enabled": True,
                "extends": "dev.ucp.shopping.checkout",
                "last_updated": "2024-01-20"
            },
            # Capacité directement présente
            "dev.ucp.common.identity_linking": {
                "version": "1.5.2",
                "enabled": True,
                "last_updated": "2024-01-10"
            },
            # Capacité absente mais étendue par une autre
            "dev.ucp.shopping.order": {
                "version": "3.0.1",
                "enabled": False,
                "last_updated": "2024-01-08"
            },
            # Capacité qui étend order
            "dev.ucp.shopping.express_order": {
                "extends": "dev.ucp.shopping.order",
                "enabled": True,
                "last_updated": "2024-01-12"
            }
            # Note: payment.processing n'est pas dans capabilities_to_check donc ignoré
        },
        "services": [
            {
                "capability": "dev.ucp.shopping.checkout",
                "endpoint": "https://httpbin.org/status/200"  # Accessible
            },
            {
                "capability": "dev.ucp.common.identity_linking", 
                "endpoint": "https://httpbin.org/status/404"  # Non accessible
            },
            {
                "capability": "dev.ucp.shopping.order",
                "endpoint": "https://httpbin.org/status/500"  # Non accessible
            }
            # Pas de service pour advanced_checkout ou express_order
        ],
        "metadata": {
            "created_at": "2024-01-01",
            "last_login": "2024-01-20",
            "account_type": "premium"
        }
    }
    
    print("=== Test complet de toutes les fonctionnalités ===")
    print("Ce test inclut:")
    print("- Capacités directement présentes")
    print("- Capacités étendues (via extends)")
    print("- Vérifications HTTP réelles des endpoints")
    print("- Messages clarifiés pour capacités absentes")
    print("- Héritage de version")
    print("-" * 80)
    
    result = check_ucp_capabilities(comprehensive_test_data)
    
    if result:
        print("Rapport final des capacités UCP:")
        print("=" * 100)
        print(f"{'Capacité':<25} {'Présence':<50} {'Version':<10} {'Endpoint':<15}")
        print("=" * 100)
        
        for capability_name, capability_data in result.items():
            presence = capability_data['Présence']
            version = capability_data['Version']
            endpoint = capability_data['Endpoint']
            print(f"{capability_name:<25} {presence:<50} {version:<10} {endpoint:<15}")
        
        print("\n" + "=" * 100)
        print("Légende:")
        print("• 'Présent' - Capacité directement déclarée dans le JSON")
        print("• 'Présent (via extension)' - Capacité inférée via extension")
        print("• 'Absent (selon le JSON public...)' - Non déclaré mais可能 géré côté serveur")
        print("• 'Accessible' - Endpoint répond HTTP 200")
        print("• 'Non accessible' - Endpoint ne répond pas ou erreur")
        print("=" * 100)
    else:
        print("Aucune capacité détectée")

def test_minimal_data():
    """Test avec données minimales pour vérifier le comportement par défaut"""
    
    minimal_data = {
        "capabilities": {
            "dev.ucp.shopping.checkout": {"version": "1.0.0"}
        }
        # Pas de services, pas d'autres capacités
    }
    
    print("\n=== Test avec données minimales ===")
    result = check_ucp_capabilities(minimal_data)
    
    if result:
        print("Rapport avec données minimales:")
        print("-" * 100)
        print(f"{'Capacité':<25} {'Présence':<50} {'Version':<10} {'Endpoint':<15}")
        print("-" * 100)
        
        for capability_name, capability_data in result.items():
            presence = capability_data['Présence']
            version = capability_data['Version']
            endpoint = capability_data['Endpoint']
            print(f"{capability_name:<25} {presence:<50} {version:<10} {endpoint:<15}")

if __name__ == "__main__":
    test_all_features_together()
    test_minimal_data()
