#!/usr/bin/env python3
"""
Test script pour vérifier le nouveau message d'absence clarifié
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import check_ucp_capabilities

def test_absent_message():
    """Test le nouveau message pour les capacités absentes"""
    
    # Test avec seulement checkout présent
    test_data_partial = {
        "capabilities": {
            "dev.ucp.shopping.checkout": {
                "version": "2.1.0",
                "enabled": True
            }
            # identity_linking et order sont absents
        },
        "services": [
            {
                "capability": "dev.ucp.shopping.checkout",
                "endpoint": "https://httpbin.org/status/200"
            }
        ]
    }
    
    print("=== Test du message d'absence clarifié ===")
    result = check_ucp_capabilities(test_data_partial)
    
    if result:
        print("Résultats des capacités UCP:")
        print("-" * 90)
        print(f"{'Capacité':<25} {'Présence':<45} {'Version':<10} {'Endpoint':<15}")
        print("-" * 90)
        
        for capability_name, capability_data in result.items():
            presence = capability_data['Présence']
            version = capability_data['Version']
            endpoint = capability_data['Endpoint']
            print(f"{capability_name:<25} {presence:<45} {version:<10} {endpoint:<15}")
    else:
        print("Aucune capacité détectée")

def test_all_present():
    """Test quand toutes les capacités sont présentes"""
    
    test_data_all_present = {
        "capabilities": {
            "dev.ucp.shopping.checkout": {"version": "2.1.0"},
            "dev.ucp.common.identity_linking": {"version": "1.5.2"},
            "dev.ucp.shopping.order": {"version": "3.0.1"}
        },
        "services": [
            {"capability": "dev.ucp.shopping.checkout", "endpoint": "https://httpbin.org/status/200"},
            {"capability": "dev.ucp.common.identity_linking", "endpoint": "https://httpbin.org/status/200"},
            {"capability": "dev.ucp.shopping.order", "endpoint": "https://httpbin.org/status/200"}
        ]
    }
    
    print("\n=== Test avec toutes les capacités présentes ===")
    result = check_ucp_capabilities(test_data_all_present)
    
    if result:
        print("Résultats des capacités UCP:")
        print("-" * 90)
        print(f"{'Capacité':<25} {'Présence':<45} {'Version':<10} {'Endpoint':<15}")
        print("-" * 90)
        
        for capability_name, capability_data in result.items():
            presence = capability_data['Présence']
            version = capability_data['Version']
            endpoint = capability_data['Endpoint']
            print(f"{capability_name:<25} {presence:<45} {version:<10} {endpoint:<15}")
    else:
        print("Aucune capacité détectée")

if __name__ == "__main__":
    test_absent_message()
    test_all_present()
