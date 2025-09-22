#!/usr/bin/env python3
"""
Check Gmail App Password Format
"""

def check_password_format(password):
    """Check if password is in correct Gmail App Password format"""
    print(f"Password: '{password}'")
    print(f"Length: {len(password)}")
    print(f"Characters: {list(password)}")
    
    # Check if it's exactly 16 characters
    if len(password) == 16:
        print("✅ Length is correct (16 characters)")
    else:
        print(f"❌ Length is incorrect (should be 16, got {len(password)})")
    
    # Check if it has spaces in the right places
    if password[4] == ' ' and password[9] == ' ' and password[14] == ' ':
        print("✅ Spaces are in correct positions")
    else:
        print("❌ Spaces are not in correct positions")
    
    # Check if it contains only alphanumeric characters and spaces
    if all(c.isalnum() or c.isspace() for c in password):
        print("✅ Contains only valid characters")
    else:
        print("❌ Contains invalid characters")
    
    # Overall check
    is_valid = (len(password) == 16 and 
                password[4] == ' ' and 
                password[9] == ' ' and 
                password[14] == ' ' and
                all(c.isalnum() or c.isspace() for c in password))
    
    print(f"\nOverall: {'✅ VALID' if is_valid else '❌ INVALID'}")
    return is_valid

if __name__ == "__main__":
    # Test your password
    password = "ohyl cyzw mnot dnte"
    check_password_format(password)
    
    print("\n" + "="*50)
    print("Expected format: 'abcd efgh ijkl mnop'")
    print("Your password:  'ohyl cyzw mnot dnte'")
    print("="*50)
