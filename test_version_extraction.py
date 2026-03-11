#!/usr/bin/env python3
"""
Test script pour vérifier l'extraction exacte des versions depuis capabilities[*]
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import check_ucp_capabilities

def test_version_extraction():
    """Test l'extraction de versions avec différents formats"""
    
    # Test avec différents formats de version
    test_data_various_versions = {
        "capabilities": {
            "dev.ucp.shopping.checkout": {
                "version": "2026-01-23",  # Format date
                "enabled": True
            },
            "dev.ucp.common.identity_linking": {
                "v": "1.5.2",  # Champ 'v'
                "enabled": True
            },
            "dev.ucp.shopping.order": {
                "__version": "3.0.1",  # Champ '__version'
                "enabled": True
            },
            "dev.ucp.shopping.advanced_order": {
                "version_number": "2026.02.15",  # Champ 'version_number'
                "extends": "dev.ucp.shopping.order",
                "enabled": True
            },
            "dev.ucp.payment.processing": {
                "release": "v2.1.0-beta",  # Champ 'release'
                "enabled": True
            },
            "dev.ucp.inventory.management": {
                "build": "build-12345",  # Champ 'build'
                "enabled": True
            },
            "dev.ucp.analytics.reporting": "2026-03-01",  # Version comme string directe
            "dev.ucp.customer.support": {
                "enabled": True
                # Pas de champ de version - devrait être 'Non spécifiée'
            }
        },
        "services": [
            {
                "capability": "dev.ucp.shopping.checkout",
                "endpoint": "https://httpbin.org/status/200"
            },
            {
                "capability": "dev.ucp.common.identity_linking", 
                "endpoint": "https://httpbin.org/status/200"
            },
            {
                "capability": "dev.ucp.shopping.order",
                "endpoint": "https://httpbin.org/status/200"
            }
        ]
    }
    
    print("=== Test d'extraction de versions avec différents formats ===")
    print("Formats testés: version, v, __version, version_number, release, build, string directe")
    print("-" * 90)
    
    result = check_ucp_capabilities(test_data_various_versions)
    
    if result:
        print("Résultats avec versions extraites:")
        print("=" * 90)
        print(f"{'Capacité':<25} {'Présence':<35} {'Version':<15} {'Endpoint':<15}")
        print("=" * 90)
        
        for capability_name, capability_data in result.items():
            presence = capability_data['Présence']
            version = capability_data['Version']
            endpoint = capability_data['Endpoint']
            print(f"{capability_name:<25} {presence:<35} {version:<15} {endpoint:<15}")
        
        print("\n" + "=" * 90)
        print("Vérification des versions extraites:")
        print("-" * 90)
        expected_versions = {
            "Shopping Checkout": "2026-01-23",
            "Common Identity Linking": "1.5.2", 
            "Shopping Order": "3.0.1",
            "Advanced Order": "2026.02.15",  # Via extension
            "Payment Processing": "v2.1.0-beta",
            "Inventory Management": "build-12345",
            "Analytics Reporting": "2026-03-01",
            "Customer Support": "Non spécifiée"  # Pas de version
        }
        
        for capability_name, expected_version in expected_versions.items():
            if capability_name in result:
                actual_version = result[capability_name]['Version']
                status = "✅" if actual_version == expected_version else "❌"
                print(f"{status} {capability_name:<25} Attendu: {expected_version:<15} Réel: {actual_version}")
            else:
                print(f"❌ {capability_name:<25} Non trouvé dans les résultats")
    else:
        print("Aucune capacité détectée")

def test_extension_version_inheritance():
    """Test l'héritage de version via extensions"""
    
    test_data_extension_version = {
        "capabilities": {
            "dev.ucp.shopping.checkout": {
                "version": "2026-01-23",
                "enabled": True
            },
            "dev.ucp.shopping.advanced_checkout": {
                "version": "3.0.0",
                "extends": "dev.ucp.shopping.checkout",
                "enabled": True
            },
            "dev.ucp.shopping.premium_checkout": {
                "extends": "dev.ucp.shopping.checkout",
                "enabled": True
                # Pas de version - devrait hériter de checkout
            }
        }
    }
    
    print("\n=== Test d'héritage de version via extensions ===")
    result = check_ucp_capabilities(test_data_extension_version)
    
    if result:
        print("Résultats avec héritage de version:")
        print("-" * 70)
        print(f"{'Capacité':<25} {'Présence':<25} {'Version':<15}")
        print("-" * 70)
        
        for capability_name, capability_data in result.items():
            presence = capability_data['Présence']
            version = capability_data['Version']
            print(f"{capability_name:<25} {presence:<25} {version:<15}")
        
        print("\nVérification de l'héritage:")
        print("-" * 40)
        print("Shopping Checkout devrait avoir '2026-01-23'")
        print("Shopping Order devrait être 'Présent (via extension)' avec version héritée")
    else:
        print("Aucune capacité détectée")

if __name__ == "__main__":
    test_version_extraction()
    test_extension_version_inheritance()
