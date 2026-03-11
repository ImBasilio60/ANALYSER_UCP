#!/usr/bin/env python3
"""
Test script pour vérifier la fonctionnalité des endpoints MCP pour Checkout
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import check_ucp_capabilities

def test_mcp_endpoint_checkout():
    """Test la vérification des endpoints MCP spécifiquement pour Checkout"""
    
    # Test avec Checkout ayant un endpoint MCP accessible
    test_data_mcp_checkout = {
        "capabilities": {
            "dev.ucp.shopping.checkout": {
                "version": "2026-01-23",
                "enabled": True
            },
            "dev.ucp.common.identity_linking": {
                "version": "1.5.2",
                "enabled": True
            },
            "dev.ucp.shopping.order": {
                "version": "3.0.1",
                "enabled": False
            }
        },
        "services": [
            {
                "capability": "dev.ucp.shopping.checkout",
                "endpoint": "https://httpbin.org/status/200"  # MCP endpoint accessible
            },
            {
                "capability": "dev.ucp.common.identity_linking", 
                "endpoint": "https://httpbin.org/status/404"  # Non accessible
            },
            {
                "capability": "dev.ucp.shopping.order",
                "endpoint": "https://httpbin.org/status/500"  # Non accessible
            }
        ]
    }
    
    print("=== Test des endpoints MCP pour Checkout ===")
    print("Vérification que Checkout a toujours un statut MCP, même si REST non accessible")
    print("-" * 90)
    
    result = check_ucp_capabilities(test_data_mcp_checkout)
    
    if result:
        print("Résultats avec vérification MCP:")
        print("=" * 90)
        print(f"{'Capacité':<25} {'Présence':<25} {'Version':<10} {'Endpoint':<15} {'Endpoint MCP':<20}")
        print("=" * 90)
        
        for capability_name, capability_data in result.items():
            presence = capability_data['Présence']
            version = capability_data['Version']
            endpoint = capability_data['Endpoint']
            mcp_endpoint = capability_data.get('Endpoint MCP', '-')
            print(f"{capability_name:<25} {presence:<25} {version:<10} {endpoint:<15} {mcp_endpoint:<20}")
        
        print("\n" + "=" * 90)
        print("Vérification spécifique pour Checkout:")
        print("-" * 90)
        
        if 'Shopping Checkout' in result:
            checkout_data = result['Shopping Checkout']
            mcp_status = checkout_data.get('Endpoint MCP', 'Non trouvé')
            print(f"✅ Shopping Checkout - Endpoint MCP: {mcp_status}")
            
            if mcp_status == 'Endpoint MCP disponible':
                print("🎉 Endpoint MCP correctement détecté comme accessible!")
            elif mcp_status == 'Non accessible':
                print("⚠️ Endpoint MCP détecté mais non accessible")
            elif mcp_status == 'Non testé':
                print("❓ Endpoint MCP non trouvé ou non testé")
        else:
            print("❌ Shopping Checkout non trouvé dans les résultats")
    else:
        print("Aucune capacité détectée")

def test_mcp_no_services():
    """Test MCP quand il n'y a pas de services"""
    
    test_data_no_services = {
        "capabilities": {
            "dev.ucp.shopping.checkout": {
                "version": "2026-01-23",
                "enabled": True
            },
            "dev.ucp.common.identity_linking": {
                "version": "1.5.2",
                "enabled": True
            }
        }
        # Pas de section services
    }
    
    print("\n=== Test MCP sans services ===")
    result = check_ucp_capabilities(test_data_no_services)
    
    if result:
        print("Résultats sans services MCP:")
        print("-" * 70)
        print(f"{'Capacité':<25} {'Présence':<25} {'Version':<10} {'Endpoint MCP':<15}")
        print("-" * 70)
        
        for capability_name, capability_data in result.items():
            presence = capability_data['Présence']
            version = capability_data['Version']
            mcp_endpoint = capability_data.get('Endpoint MCP', '-')
            print(f"{capability_name:<25} {presence:<25} {version:<10} {mcp_endpoint:<15}")
        
        print("\nVérification: Checkout devrait avoir 'Non testé' pour Endpoint MCP")
    else:
        print("Aucune capacité détectée")

def test_mcp_multiple_endpoints():
    """Test MCP avec plusieurs endpoints pour Checkout"""
    
    test_data_multiple_mcp = {
        "capabilities": {
            "dev.ucp.shopping.checkout": {
                "version": "2026-01-23",
                "enabled": True
            }
        },
        "services": [
            {
                "capability": "dev.ucp.shopping.checkout",
                "endpoint": "https://httpbin.org/status/404"  # Premier endpoint non accessible
            },
            {
                "capability": "dev.ucp.shopping.checkout",
                "endpoint": "https://httpbin.org/status/500"  # Deuxième endpoint non accessible
            },
            {
                "capability": "dev.ucp.shopping.checkout",
                "endpoint": "https://httpbin.org/status/200"  # Troisième endpoint accessible
            }
        ]
    }
    
    print("\n=== Test MCP avec plusieurs endpoints ===")
    result = check_ucp_capabilities(test_data_multiple_mcp)
    
    if result:
        print("Résultats avec multiples endpoints MCP:")
        print("-" * 60)
        print(f"{'Capacité':<25} {'Endpoint MCP':<20}")
        print("-" * 60)
        
        for capability_name, capability_data in result.items():
            mcp_endpoint = capability_data.get('Endpoint MCP', '-')
            print(f"{capability_name:<25} {mcp_endpoint:<20}")
        
        print("\nVérification: Devrait trouver 'Endpoint MCP disponible' (au moins un accessible)")
    else:
        print("Aucune capacité détectée")

if __name__ == "__main__":
    test_mcp_endpoint_checkout()
    test_mcp_no_services()
    test_mcp_multiple_endpoints()
