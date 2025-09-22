#!/usr/bin/env python3
"""
Fix syntax errors in app.py
"""

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the problematic section and fix it
fixed_lines = []
in_payment_section = False
try_block_depth = 0

for i, line in enumerate(lines):
    if 'Initialize payment directly in the route to avoid context issues' in line:
        in_payment_section = True
        # Add proper indentation for imports
        fixed_lines.append(line)
        fixed_lines.append('    from payment_service import PaymentService\n')
        fixed_lines.append('    import requests\n')
        fixed_lines.append('    import json\n')
        fixed_lines.append('    from datetime import datetime\n')
        fixed_lines.append('\n')
        fixed_lines.append('    # Get Paystack configuration\n')
        fixed_lines.append('    public_key = app.config.get(\'PAYSTACK_PUBLIC_KEY\')\n')
        fixed_lines.append('    secret_key = app.config.get(\'PAYSTACK_SECRET_KEY\')\n')
        fixed_lines.append('    base_url = "https://api.paystack.co"\n')
        continue
    elif in_payment_section and line.strip().startswith('from payment_service import PaymentService'):
        # Skip the duplicate import lines
        continue
    elif in_payment_section and line.strip().startswith('import requests'):
        continue
    elif in_payment_section and line.strip().startswith('import json'):
        continue
    elif in_payment_section and line.strip().startswith('from datetime import datetime'):
        continue
    elif in_payment_section and 'Get Paystack configuration' in line:
        continue
    elif in_payment_section and 'public_key = app.config.get' in line:
        continue
    elif in_payment_section and 'secret_key = app.config.get' in line:
        continue
    elif in_payment_section and 'base_url = "https://api.paystack.co"' in line:
        continue
    elif in_payment_section and line.strip() == '':
        in_payment_section = False
        fixed_lines.append(line)
    else:
        fixed_lines.append(line)

# Write the fixed content back
with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print('Fixed syntax errors in app.py')
