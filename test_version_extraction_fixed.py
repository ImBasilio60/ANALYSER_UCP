#!/usr/bin/env python3
"""
Test script pour vérifier l'extraction exacte des versions depuis capabilities[*]
pour les 3 capacités UCP spécifiques
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import check_ucp_capabilities

def test_date_format_versions():
    """Test l'extraction de versions avec format date comme '2026-01-23'"""
    
    # Test avec format date pour les 3 capacités UCP
    test_data_date_versions = {
        "capabilities": {
            "dev.ucp.shopping.checkout": {
                "version": "2026-01-23",  # Format date demandé
                "enabled": True
            },
            "dev.ucp.common.identity_linking": {
                "version": "2026-02-15",  # Format date
                "enabled": True
            },
            "dev.ucp.shopping.order": {
                "version": "2026-03-01",  # Format date
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
            }
        ]
    }
    
    print("=== Test d'extraction de versions avec format date ===")
    print("Formats testés: 2026-01-23, 2026-02-15, 2026-03-01")
    print("-" * 80)
    
    result = check_ucp_capabilities(test_data_date_versions)
    
    if result:
        print("Résultats avec versions en format date:")
        print("=" * 80)
        print(f"{'Capacité':<25} {'Présence':<25} {'Version':<15} {'Endpoint':<15}")
        print("=" * 80)
        
        for capability_name, capability_data in result.items():
            presence = capability_data['Présence']
            version = capability_data['Version']
            endpoint = capability_data['Endpoint']
            print(f"{capability_name:<25} {presence:<25} {version:<15} {endpoint:<15}")
        
        print("\n" + "=" * 80)
        print("Vérification des versions extraites (format date):")
        print("-" * 80)
        expected_versions = {
            "Shopping Checkout": "2026-01-23",
            "Common Identity Linking": "2026-02-15", 
            "Shopping Order": "2026-03-01"
        }
        
        all_correct = True
        for capability_name, expected_version in expected_versions.items():
            if capability_name in result:
                actual_version = result[capability_name]['Version']
                status = "✅" if actual_version == expected_version else "❌"
                if actual_version != expected_version:
                    all_correct = False
                print(f"{status} {capability_name:<25} Attendu: {expected_version:<15} Réel: {actual_version}")
        
        if all_correct:
            print("\n🎉 Toutes les versions ont été correctement extraites!")
        else:
            print("\n⚠️ Certaines versions n'ont pas été correctement extraites.")
    else:
        print("Aucune capacité détectée")

def test_mixed_version_formats():
    """Test avec différents formats de version pour les 3 capacités"""
    
    test_data_mixed = {
        "capabilities": {
            "dev.ucp.shopping.checkout": {
                "v": "2.1.0",  # Champ 'v'
                "enabled": True
            },
            "dev.ucp.common.identity_linking": {
                "__version": "1.5.2",  # Champ '__version'
                "enabled": True
            },
            "dev.ucp.shopping.advanced_order": {
                "version_number": "2026.02.15",  # Champ 'version_number'
                "extends": "dev.ucp.shopping.order",  # Étend order
                "enabled": True
            }
            # order n'est pas directement présent mais étendu
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
    
    print("\n=== Test avec formats de version mixtes et extensions ===")
    result = check_ucp_capabilities(test_data_mixed)
    
    if result:
        print("Résultats avec formats mixtes:")
        print("-" * 80)
        print(f"{'Capacité':<25} {'Présence':<25} {'Version':<15} {'Endpoint':<15}")
        print("-" * 80)
        
        for capability_name, capability_data in result.items():
            presence = capability_data['Présence']
            version = capability_data['Version']
            endpoint = capability_data['Endpoint']
            print(f"{capability_name:<25} {presence:<25} {version:<15} {endpoint:<15}")
        
        print("\nVérification:")
        print("-" * 40)
        print("Shopping Checkout: version '2.1.0' depuis champ 'v'")
        print("Common Identity Linking: version '1.5.2' depuis champ '__version'")
        print("Shopping Order: 'Présent (via extension)' avec version héritée")
    else:
        print("Aucune capacité détectée")

def test_no_version_fields():
    """Test quand aucune information de version n'est disponible"""
    
    test_data_no_version = {
        "capabilities": {
            "dev.ucp.shopping.checkout": {
                "enabled": True
                # Pas de champ de version
            },
            "dev.ucp.common.identity_linking": {
                "enabled": True
                # Pas de champ de version
            }
        },
        "services": [
            {
                "capability": "dev.ucp.shopping.checkout",
                "endpoint": "https://httpbin.org/status/200"
            }
        ]
    }
    
    print("\n=== Test sans information de version ===")
    result = check_ucp_capabilities(test_data_no_version)
    
    if result:
        print("Résultats sans version:")
        print("-" * 70)
        print(f"{'Capacité':<25} {'Présence':<25} {'Version':<15}")
        print("-" * 70)
        
        for capability_name, capability_data in result.items():
            presence = capability_data['Présence']
            version = capability_data['Version']
            print(f"{capability_name:<25} {presence:<25} {version:<15}")
        
        print("\nVérification: Les versions devraient être 'Non spécifiée'")
    else:
        print("Aucune capacité détectée")

if __name__ == "__main__":
    test_date_format_versions()
    test_mixed_version_formats()
    test_no_version_fields()
