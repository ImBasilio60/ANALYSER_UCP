#!/usr/bin/env python3
"""
Test script pour vérifier l'inférence de présence pour Identity Linking et Order
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import check_ucp_capabilities

def test_identity_inference():
    """Test l'inférence de Identity Linking depuis d'autres endpoints"""
    
    # Test avec des indicateurs d'identité dans les capacités
    test_data_identity_indicators = {
        "capabilities": {
            "dev.ucp.shopping.checkout": {
                "version": "2026-01-23",
                "enabled": True
            },
            # Capacité avec indicateur d'identité
            "dev.ucp.customer.profile": {
                "version": "1.0.0",
                "enabled": True
            }
            # Identity Linking n'est pas directement présent
        },
        "services": [
            {
                "capability": "dev.ucp.shopping.checkout",
                "endpoint": "https://api.example.com/checkout/health"
            },
            {
                "capability": "dev.ucp.customer.profile",
                "endpoint": "https://api.example.com/user/profile"
            }
        ]
    }
    
    print("=== Test d'inférence de Identity Linking ===")
    print("Vérification que Identity Linking est inféré depuis 'profile'")
    print("-" * 80)
    
    result = check_ucp_capabilities(test_data_identity_indicators)
    
    if result:
        print("Résultats avec inférence Identity Linking:")
        print("=" * 80)
        print(f"{'Capacité':<25} {'Présence':<40} {'Version':<10} {'Endpoint':<15}")
        print("=" * 80)
        
        for capability_name, capability_data in result.items():
            presence = capability_data['Présence']
            version = capability_data['Version']
            endpoint = capability_data['Endpoint']
            print(f"{capability_name:<25} {presence:<40} {version:<10} {endpoint:<15}")
        
        print("\nVérification:")
        print("-" * 40)
        if 'Common Identity Linking' in result:
            identity_status = result['Common Identity Linking']['Présence']
            if 'inféré' in identity_status.lower():
                print(f"✅ Identity Linking correctement inféré: {identity_status}")
            else:
                print(f"❌ Identity Linking non inféré: {identity_status}")
        else:
            print("❌ Identity Linking non trouvé dans les résultats")
    else:
        print("Aucune capacité détectée")

def test_order_inference():
    """Test l'inférence de Order depuis d'autres endpoints"""
    
    # Test avec des indicateurs de commande dans les services
    test_data_order_indicators = {
        "capabilities": {
            "dev.ucp.shopping.checkout": {
                "version": "2026-01-23",
                "enabled": True
            }
            # Order n'est pas directement présent
        },
        "services": [
            {
                "capability": "dev.ucp.shopping.checkout",
                "endpoint": "https://api.example.com/checkout/health"
            },
            {
                "capability": "dev.ucp.cart.management",
                "endpoint": "https://api.example.com/cart/status"
            },
            {
                "capability": "dev.ucp.payment.processing",
                "endpoint": "https://api.example.com/payment/validate"
            }
        ]
    }
    
    print("\n=== Test d'inférence de Order ===")
    print("Vérification que Order est inféré depuis 'cart' et 'payment'")
    print("-" * 80)
    
    result = check_ucp_capabilities(test_data_order_indicators)
    
    if result:
        print("Résultats avec inférence Order:")
        print("=" * 80)
        print(f"{'Capacité':<25} {'Présence':<40} {'Version':<10} {'Endpoint':<15}")
        print("=" * 80)
        
        for capability_name, capability_data in result.items():
            presence = capability_data['Présence']
            version = capability_data['Version']
            endpoint = capability_data['Endpoint']
            print(f"{capability_name:<25} {presence:<40} {version:<10} {endpoint:<15}")
        
        print("\nVérification:")
        print("-" * 40)
        if 'Shopping Order' in result:
            order_status = result['Shopping Order']['Présence']
            if 'inféré' in order_status.lower():
                print(f"✅ Order correctement inféré: {order_status}")
            else:
                print(f"❌ Order non inféré: {order_status}")
        else:
            print("❌ Order non trouvé dans les résultats")
    else:
        print("Aucune capacité détectée")

def test_no_inference():
    """Test quand aucune inférence n'est possible"""
    
    test_data_no_indicators = {
        "capabilities": {
            "dev.ucp.shopping.checkout": {
                "version": "2026-01-23",
                "enabled": True
            }
        },
        "services": [
            {
                "capability": "dev.ucp.shopping.checkout",
                "endpoint": "https://api.example.com/checkout"
            }
        ]
        # Pas d'indicateurs pour Identity Linking ou Order
    }
    
    print("\n=== Test sans inférence possible ===")
    result = check_ucp_capabilities(test_data_no_indicators)
    
    if result:
        print("Résultats sans inférence:")
        print("=" * 80)
        print(f"{'Capacité':<25} {'Présence':<40} {'Version':<10}")
        print("=" * 80)
        
        for capability_name, capability_data in result.items():
            presence = capability_data['Présence']
            version = capability_data['Version']
            print(f"{capability_name:<25} {presence:<40} {version:<10}")
        
        print("\nVérification: Identity Linking et Order devraient être 'Absent (selon le JSON public...)'")
    else:
        print("Aucune capacité détectée")

def test_mixed_inference():
    """Test avec inférence mixte et présence directe"""
    
    test_data_mixed = {
        "capabilities": {
            "dev.ucp.shopping.checkout": {
                "version": "2026-01-23",
                "enabled": True
            },
            "dev.ucp.common.identity_linking": {
                "version": "2026-02-15",
                "enabled": True
            }
            # Order absent mais avec indicateurs
        },
        "services": [
            {
                "capability": "dev.ucp.shopping.checkout",
                "endpoint": "https://api.example.com/checkout"
            },
            {
                "capability": "dev.ucp.billing.invoice",
                "endpoint": "https://api.example.com/invoice/status"
            }
        ]
    }
    
    print("\n=== Test mixte (présence directe + inférence) ===")
    result = check_ucp_capabilities(test_data_mixed)
    
    if result:
        print("Résultats mixtes:")
        print("=" * 80)
        print(f"{'Capacité':<25} {'Présence':<40} {'Version':<10}")
        print("=" * 80)
        
        for capability_name, capability_data in result.items():
            presence = capability_data['Présence']
            version = capability_data['Version']
            print(f"{capability_name:<25} {presence:<40} {version:<10}")
        
        print("\nVérification: Identity Linking direct, Order inféré")
    else:
        print("Aucune capacité détectée")

if __name__ == "__main__":
    test_identity_inference()
    test_order_inference()
    test_no_inference()
    test_mixed_inference()
