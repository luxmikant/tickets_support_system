#!/usr/bin/env python3
"""
Generate a secure Django SECRET_KEY for production deployment.
Used for Render, Supabase, and other cloud platforms.

Usage:
    python generate_secret_key.py
"""

import secrets
import string

def generate_django_secret_key(length=50):
    """
    Generate a cryptographically secure Django SECRET_KEY.
    
    Args:
        length (int): Length of the secret key (default: 50)
    
    Returns:
        str: A secure random string suitable for Django SECRET_KEY
    """
    # Use Django's character set for SECRET_KEY
    chars = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
    
    # Generate random string using secrets module (cryptographically secure)
    secret_key = ''.join(secrets.choice(chars) for _ in range(length))
    
    return secret_key


def generate_password(length=32):
    """
    Generate a secure random password.
    
    Args:
        length (int): Length of the password (default: 32)
    
    Returns:
        str: A secure random password
    """
    chars = string.ascii_letters + string.digits + '-_'
    password = ''.join(secrets.choice(chars) for _ in range(length))
    return password


if __name__ == '__main__':
    import sys
    
    print("\n" + "="*70)
    print("Secure Key Generator for Support Ticket System")
    print("="*70 + "\n")
    
    # Django SECRET_KEY
    secret_key = generate_django_secret_key()
    print("Django SECRET_KEY:")
    print("-" * 70)
    print(secret_key)
    print()
    
    # Database password
    db_password = generate_password(32)
    print("Secure Database Password:")
    print("-" * 70)
    print(db_password)
    print()
    
    # API Key placeholder
    print("Next Steps:")
    print("-" * 70)
    print("1. Copy the Django SECRET_KEY above")
    print("2. Set in Render environment as DJANGO_SECRET_KEY (mark as Secret)")
    print()
    print("3. Copy the Database Password above")
    print("4. Set in Supabase as your database password")
    print()
    print("5. Get your Google Gemini API key from:")
    print("   https://aistudio.google.com/apikey")
    print()
    print("6. For each secret, mark it as 'Secret' in Render dashboard")
    print("   by clicking the 'Secret' icon")
    print()
    print("="*70 + "\n")
