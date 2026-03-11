#!/usr/bin/env python3
"""
Test script pour la fonction de vérification des capacités UCP
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import check_ucp_capabilities

def test_capability_checking():
    """Test la fonction de vérification des capacités avec différents formats de données"""
    
    # Test 1: Structure simple avec capacités directes
    test_data_1 = {
        "capabilities": {
            "dev.ucp.shopping.checkout": {"version": "2.1.0"},
            "dev.ucp.common.identity_linking": {"v": "1.5.2"},
            "dev.ucp.shopping.order": "3.0.1"
        }
    }
    
    # Test 2: Structure imbriquée ucp.capabilities
    test_data_2 = {
        "ucp": {
            "capabilities": {
                "dev.ucp.shopping.checkout": {"__version": "2.1.0"},
                "dev.ucp.common.identity_linking": {"version": "1.5.2"}
                # dev.ucp.shopping.order manquant
            }
        }
    }
    
    # Test 3: Structure data.capabilities
    test_data_3 = {
        "data": {
            "capabilities": {
                "dev.ucp.shopping.checkout": {"version": "2.1.0"},
                "dev.ucp.shopping.order": {"version": "3.0.1"}
                # dev.ucp.common.identity_linking manquant
            }
        }
    }
    
    # Test 4: Capacités directement au niveau racine
    test_data_4 = {
        "dev.ucp.shopping.checkout": {"version": "2.1.0"},
        "dev.ucp.common.identity_linking": {"version": "1.5.2"},
        "dev.ucp.shopping.order": {"version": "3.0.1"}
    }
    
    # Test 5: Aucune capacité
    test_data_5 = {
        "other_data": "some_value"
    }
    
    tests = [
        ("Structure simple", test_data_1),
        ("Structure ucp.capabilities", test_data_2),
        ("Structure data.capabilities", test_data_3),
        ("Capacités au niveau racine", test_data_4),
        ("Aucune capacité", test_data_5)
    ]
    
    for test_name, test_data in tests:
        print(f"\n=== Test: {test_name} ===")
        result = check_ucp_capabilities(test_data)
        
        if result:
            for capability, info in result.items():
                print(f"{capability}:")
                print(f"  Présent: {info['Présent']}")
                print(f"  Version: {info['Version']}")
        else:
            print("Aucune capacité détectée")

if __name__ == "__main__":
    test_capability_checking()
