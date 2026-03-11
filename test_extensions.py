#!/usr/bin/env python3
"""
Test script pour la fonction améliorée avec détection des extensions de capacités
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import check_ucp_capabilities
import json

def test_capability_extensions():
    """Test la fonction avec des capacités qui étendent d'autres capacités"""
    
    # Test avec extensions
    test_data_with_extensions = {
        "capabilities": {
            "dev.ucp.shopping.checkout": {
                "version": "2.1.0",
                "enabled": True
            },
            "dev.ucp.shopping.advanced_checkout": {
                "version": "3.0.0",
                "enabled": True,
                "extends": "dev.ucp.shopping.checkout"
            },
            "dev.ucp.common.identity_linking": {
                "version": "1.5.2",
                "enabled": True
            },
            "dev.ucp.shopping.express_order": {
                "extends": "dev.ucp.shopping.order",
                "enabled": True
            }
            # dev.ucp.shopping.order n'est pas directement présent
        },
        "services": [
            {
                "capability": "dev.ucp.shopping.checkout",
                "endpoint": "https://httpbin.org/status/200"
            },
            {
                "capability": "dev.ucp.common.identity_linking", 
                "endpoint": "https://httpbin.org/status/404"
            }
        ]
    }
    
    print("=== Test avec extensions de capacités ===")
    result = check_ucp_capabilities(test_data_with_extensions)
    
    if result:
        print("Résultats des capacités UCP:")
        print("-" * 80)
        print(f"{'Capacité':<25} {'Présence':<20} {'Version':<10} {'Endpoint':<15}")
        print("-" * 80)
        
        for capability_name, capability_data in result.items():
            presence = capability_data['Présence']
            version = capability_data['Version']
            endpoint = capability_data['Endpoint']
            print(f"{capability_name:<25} {presence:<20} {version:<10} {endpoint:<15}")
        
        print("\nDétails des extensions détectées:")
        print("-" * 40)
        for capability_name, capability_data in result.items():
            if 'via extension' in capability_data['Présence']:
                print(f"• {capability_name}: {capability_data['Présence']}")
    else:
        print("Aucune capacité détectée")

def test_mixed_capabilities():
    """Test avec un mélange de capacités directes et étendues"""
    
    test_data_mixed = {
        "capabilities": {
            "dev.ucp.shopping.checkout": {
                "version": "2.1.0",
                "enabled": True
            },
            # Directement présent
            "dev.ucp.shopping.order": {
                "version": "3.0.1",
                "enabled": False
            },
            # Étend checkout
            "dev.ucp.shopping.premium_checkout": {
                "extends": "dev.ucp.shopping.checkout",
                "enabled": True
            }
        },
        "services": [
            {
                "capability": "dev.ucp.shopping.checkout",
                "endpoint": "https://httpbin.org/status/200"
            },
            {
                "capability": "dev.ucp.shopping.order",
                "endpoint": "https://httpbin.org/status/500"
            }
        ]
    }
    
    print("\n=== Test mixte (directes + étendues) ===")
    result = check_ucp_capabilities(test_data_mixed)
    
    if result:
        print("Résultats des capacités UCP:")
        print("-" * 80)
        print(f"{'Capacité':<25} {'Présence':<20} {'Version':<10} {'Endpoint':<15}")
        print("-" * 80)
        
        for capability_name, capability_data in result.items():
            presence = capability_data['Présence']
            version = capability_data['Version']
            endpoint = capability_data['Endpoint']
            print(f"{capability_name:<25} {presence:<20} {version:<10} {endpoint:<15}")
    else:
        print("Aucune capacité détectée")

if __name__ == "__main__":
    test_capability_extensions()
    test_mixed_capabilities()
