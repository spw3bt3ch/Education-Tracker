#!/usr/bin/env python3
"""
Fix Gmail App Password Format
"""

def fix_password(original_password):
    """Try to fix the password format"""
    print(f"Original password: '{original_password}'")
    print(f"Length: {len(original_password)}")
    
    # Remove extra spaces and characters
    # Gmail App Passwords should be: 4 chars + space + 4 chars + space + 4 chars + space + 4 chars
    parts = original_password.split()
    print(f"Parts: {parts}")
    
    if len(parts) == 4:
        # Check if any part has more than 4 characters
        for i, part in enumerate(parts):
            if len(part) > 4:
                print(f"Part {i+1} '{part}' has {len(part)} characters (should be 4)")
                # Take only first 4 characters
                parts[i] = part[:4]
                print(f"Fixed to: '{parts[i]}'")
        
        # Reconstruct password
        fixed_password = ' '.join(parts)
        print(f"Fixed password: '{fixed_password}'")
        print(f"Fixed length: {len(fixed_password)}")
        
        if len(fixed_password) == 16:
            print("✅ Password format is now correct!")
            return fixed_password
        else:
            print("❌ Still not correct format")
            return None
    else:
        print(f"❌ Expected 4 parts, got {len(parts)}")
        return None

if __name__ == "__main__":
    original = "ohyl cyzw mnot dnte"
    fixed = fix_password(original)
    
    if fixed:
        print(f"\n🎯 Use this password: '{fixed}'")
        print("Update your aiven_config.env file with this corrected password.")
    else:
        print("\n❌ Could not fix the password format.")
        print("Please generate a new Gmail App Password:")
        print("1. Go to https://myaccount.google.com/")
        print("2. Security → 2-Step Verification")
        print("3. App passwords → Generate app password")
        print("4. Select 'Mail' and 'Other (custom name)'")
        print("5. Enter 'EduTrack' as the name")
        print("6. Copy the 16-character password exactly as shown")
