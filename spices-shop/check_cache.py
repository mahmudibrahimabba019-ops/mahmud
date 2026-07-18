from pathlib import Path
content = Path('checkout.html').read_text(encoding='utf-8')

if "'HHS-' + Date.now()" in content:
    print('HHS STILL PRESENT - file was not updated')
else:
    print('HHS REMOVED - file is correct')

if 'payment-reference' in content:
    print('PATCH PRESENT - new code is there')
else:
    print('PATCH MISSING - new code not found')