#!/usr/bin/env python3
"""
Test script pour vérifier la détection et l'affichage des extensions de capacités
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import check_ucp_capabilities

def test_extension_detection_and_display():
    """Test la détection des capacités qui étendent d'autres capacités"""
    
    # Test avec plusieurs capacités qui étendent les capacités de base
    test_data_extensions = {
        "capabilities": {
            "dev.ucp.shopping.checkout": {
                "version": "2026-01-23",
                "enabled": True
            },
            "dev.ucp.common.identity_linking": {
                "version": "2026-02-15",
                "enabled": True
            },
            "dev.ucp.shopping.order": {
                "version": "2026-03-01",
                "enabled": False
            },
            # Capacités qui étendent les capacités de base
            "dev.ucp.shopping.advanced_checkout": {
                "version": "3.0.0",
                "extends": "dev.ucp.shopping.checkout",
                "enabled": True
            },
            "dev.ucp.shopping.premium_checkout": {
                "version": "3.1.0",
                "extends": "dev.ucp.shopping.checkout",
                "enabled": True
            },
            "dev.ucp.shopping.express_order": {
                "version": "2.5.0",
                "extends": "dev.ucp.shopping.order",
                "enabled": True
            },
            "dev.ucp.common.enhanced_identity": {
                "version": "1.8.0",
                "extends": "dev.ucp.common.identity_linking",
                "enabled": True
            }
        },
        "services": [
            {
                "capability": "dev.ucp.shopping.checkout",
                "endpoint": "https://httpbin.org/status/200"
            },
            {
                "capability": "dev.ucp.common.identity_linking", 
                "endpoint": "https://httpbin.org/status/404"
            },
            {
                "capability": "dev.ucp.shopping.order",
                "endpoint": "https://httpbin.org/status/500"
            },
            {
                "capability": "dev.ucp.shopping.advanced_checkout",
                "endpoint": "https://httpbin.org/status/200"
            },
            {
                "capability": "dev.ucp.shopping.express_order",
                "endpoint": "https://httpbin.org/status/404"
            }
        ]
    }
    
    print("=== Test de détection et d'affichage des extensions ===")
    print("Vérification que les extensions sont affichées avec 'via BaseCapability'")
    print("-" * 100)
    
    result = check_ucp_capabilities(test_data_extensions)
    
    if result:
        print("Résultats avec extensions détectées:")
        print("=" * 100)
        print(f"{'Capacité':<35} {'Présence':<20} {'Version':<10} {'Endpoint':<15}")
        print("=" * 100)
        
        for capability_name, capability_data in result.items():
            presence = capability_data['Présence']
            version = capability_data['Version']
            endpoint = capability_data['Endpoint']
            print(f"{capability_name:<35} {presence:<20} {version:<10} {endpoint:<15}")
        
        print("\n" + "=" * 100)
        print("Vérification des extensions détectées:")
        print("-" * 100)
        
        expected_extensions = {
            "Advanced Checkout (via Shopping Checkout)": "3.0.0",
            "Premium Checkout (via Shopping Checkout)": "3.1.0", 
            "Express Order (via Shopping Order)": "2.5.0",
            "Enhanced Identity (via Common Identity Linking)": "1.8.0"
        }
        
        all_correct = True
        for ext_name, expected_version in expected_extensions.items():
            if ext_name in result:
                actual_version = result[ext_name]['Version']
                status = "✅" if actual_version == expected_version else "❌"
                if actual_version != expected_version:
                    all_correct = False
                print(f"{status} {ext_name:<35} Version: {actual_version} (attendu: {expected_version})")
            else:
                print(f"❌ {ext_name:<35} Non trouvé dans les résultats")
                all_correct = False
        
        if all_correct:
            print("\n🎉 Toutes les extensions ont été correctement détectées et affichées!")
        else:
            print("\n⚠️ Certaines extensions n'ont pas été correctement détectées.")
    else:
        print("Aucune capacité détectée")

def test_extension_without_version():
    """Test les extensions sans information de version"""
    
    test_data_no_version = {
        "capabilities": {
            "dev.ucp.shopping.checkout": {
                "version": "2026-01-23",
                "enabled": True
            },
            "dev.ucp.shopping.discount_checkout": {
                "extends": "dev.ucp.shopping.checkout",
                "enabled": True
                # Pas de version
            }
        },
        "services": [
            {
                "capability": "dev.ucp.shopping.checkout",
                "endpoint": "https://httpbin.org/status/200"
            },
            {
                "capability": "dev.ucp.shopping.discount_checkout",
                "endpoint": "https://httpbin.org/status/404"
            }
        ]
    }
    
    print("\n=== Test d'extensions sans version ===")
    result = check_ucp_capabilities(test_data_no_version)
    
    if result:
        print("Résultats avec extension sans version:")
        print("-" * 70)
        print(f"{'Capacité':<35} {'Présence':<20} {'Version':<10}")
        print("-" * 70)
        
        for capability_name, capability_data in result.items():
            presence = capability_data['Présence']
            version = capability_data['Version']
            print(f"{capability_name:<35} {presence:<20} {version:<10}")
        
        print("\nVérification: L'extension devrait avoir 'Non spécifiée' comme version")
    else:
        print("Aucune capacité détectée")

def test_extension_not_in_base_list():
    """Test les capacités qui étendent des capacités non vérifiées"""
    
    test_data_other_extensions = {
        "capabilities": {
            "dev.ucp.shopping.checkout": {
                "version": "2026-01-23",
                "enabled": True
            },
            "dev.ucp.shopping.discount": {
                "version": "1.0.0",
                "extends": "dev.ucp.shopping.checkout",
                "enabled": True
            },
            "dev.ucp.analytics.reporting": {
                "version": "2.0.0",
                "extends": "dev.ucp.analytics.dashboard",  # Non dans la liste de vérification
                "enabled": True
            }
        }
    }
    
    print("\n=== Test d'extensions vers capacités non vérifiées ===")
    result = check_ucp_capabilities(test_data_other_extensions)
    
    if result:
        print("Résultats:")
        print("-" * 60)
        print(f"{'Capacité':<35} {'Présence':<20} {'Version':<10}")
        print("-" * 60)
        
        for capability_name, capability_data in result.items():
            presence = capability_data['Présence']
            version = capability_data['Version']
            print(f"{capability_name:<35} {presence:<20} {version:<10}")
        
        print("\nVérification: Seule l'extension vers Checkout devrait être affichée")
    else:
        print("Aucune capacité détectée")

if __name__ == "__main__":
    test_extension_detection_and_display()
    test_extension_without_version()
    test_extension_not_in_base_list()
