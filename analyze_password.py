#!/usr/bin/env python3
"""
Analyze Gmail App Password Character by Character
"""

def analyze_password(password):
    """Analyze password character by character"""
    print("Password Analysis:")
    print("=" * 50)
    print(f"Password: '{password}'")
    print(f"Length: {len(password)}")
    print()
    
    print("Character by character:")
    for i, char in enumerate(password):
        if char == ' ':
            print(f"Position {i:2d}: SPACE")
        else:
            print(f"Position {i:2d}: '{char}'")
    
    print()
    print("Expected format: 4 chars + space + 4 chars + space + 4 chars + space + 4 chars")
    print("Expected length: 16 characters")
    print(f"Your length: {len(password)} characters")
    
    if len(password) == 16:
        print("✅ Length is correct!")
    else:
        print(f"❌ Length is incorrect! Should be 16, got {len(password)}")
        print("This suggests there's an extra character somewhere.")

if __name__ == "__main__":
    password = "ohyl cyzw mnot dnte"
    analyze_password(password)
    
    print("\n" + "="*50)
    print("SOLUTION:")
    print("Please generate a NEW Gmail App Password:")
    print("1. Go to https://myaccount.google.com/")
    print("2. Security → 2-Step Verification")
    print("3. App passwords → Generate app password")
    print("4. Select 'Mail' and 'Other (custom name)'")
    print("5. Enter 'EduTrack' as the name")
    print("6. Copy the EXACT 16-character password as shown")
    print("7. It should look like: 'abcd efgh ijkl mnop'")
