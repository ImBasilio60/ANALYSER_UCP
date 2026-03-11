#!/usr/bin/env python3
"""
Test script pour la fonction modifiée de vérification des capacités UCP avec services endpoints
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import check_ucp_capabilities
import json

def test_new_functionality():
    """Test la fonction modifiée avec des données contenant services endpoints"""
    
    # Test avec services endpoints
    test_data_with_services = {
        "user_id": "user_12345",
        "profile_name": "Jean Dupont",
        "capabilities": {
            "dev.ucp.shopping.checkout": {
                "version": "2.1.0",
                "enabled": True,
                "last_updated": "2024-01-15"
            },
            "dev.ucp.common.identity_linking": {
                "version": "1.5.2",
                "enabled": True,
                "last_updated": "2024-01-10"
            },
            "dev.ucp.shopping.order": {
                "version": "3.0.1",
                "enabled": False,
                "last_updated": "2024-01-08"
            }
        },
        "services": [
            {
                "capability": "dev.ucp.shopping.checkout",
                "endpoint": "https://httpbin.org/status/200"  # Endpoint qui retourne 200
            },
            {
                "capability": "dev.ucp.common.identity_linking", 
                "endpoint": "https://httpbin.org/status/404"  # Endpoint qui retourne 404
            },
            {
                "capability": "dev.ucp.shopping.order",
                "endpoint": "https://invalid-endpoint-that-does-not-exist.com/ping"  # Endpoint invalide
            }
        ]
    }
    
    print("=== Test avec services endpoints ===")
    result = check_ucp_capabilities(test_data_with_services)
    
    if result:
        print("Résultats des capacités UCP:")
        print("-" * 60)
        print(f"{'Capacité':<25} {'Présence':<10} {'Version':<10} {'Endpoint':<15}")
        print("-" * 60)
        
        for capability_name, capability_data in result.items():
            presence = capability_data['Présence']
            version = capability_data['Version']
            endpoint = capability_data['Endpoint']
            print(f"{capability_name:<25} {presence:<10} {version:<10} {endpoint:<15}")
    else:
        print("Aucune capacité détectée")

def test_without_services():
    """Test la fonction sans services endpoints"""
    
    test_data_without_services = {
        "capabilities": {
            "dev.ucp.shopping.checkout": {"version": "2.1.0"},
            "dev.ucp.common.identity_linking": {"version": "1.5.2"}
        }
        # Pas de section services
    }
    
    print("\n=== Test sans services endpoints ===")
    result = check_ucp_capabilities(test_data_without_services)
    
    if result:
        print("Résultats des capacités UCP:")
        print("-" * 60)
        print(f"{'Capacité':<25} {'Présence':<10} {'Version':<10} {'Endpoint':<15}")
        print("-" * 60)
        
        for capability_name, capability_data in result.items():
            presence = capability_data['Présence']
            version = capability_data['Version']
            endpoint = capability_data['Endpoint']
            print(f"{capability_name:<25} {presence:<10} {version:<10} {endpoint:<15}")
    else:
        print("Aucune capacité détectée")

if __name__ == "__main__":
    test_new_functionality()
    test_without_services()
