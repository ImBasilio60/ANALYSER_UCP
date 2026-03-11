#!/usr/bin/env python3
"""
Test script pour la fonction de vérification des endpoints REST
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import check_rest_endpoint

def test_endpoint_checking():
    """Test la fonction de vérification des endpoints REST"""
    
    print("=== Test de vérification des endpoints REST ===\n")
    
    # Tester chaque capacité
    capabilities = [
        'dev.ucp.shopping.checkout',
        'dev.ucp.common.identity_linking',
        'dev.ucp.shopping.order',
        'dev.ucp.nonexistent.capability'  # Capacité non existante
    ]
    
    for capability in capabilities:
        print(f"Test de la capacité: {capability}")
        status = check_rest_endpoint(capability)
        print(f"  Statut de l'endpoint: {status}")
        print()

if __name__ == "__main__":
    test_endpoint_checking()
