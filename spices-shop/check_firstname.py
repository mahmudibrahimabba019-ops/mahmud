from pathlib import Path
content = Path('checkout.html').read_text(encoding='utf-8')
if "first_name: document.getElementById('firstName')" in content:
    print('FIRST_NAME PRESENT')
else:
    print('FIRST_NAME MISSING')
if "last_name: document.getElementById('lastName')" in content:
    print('LAST_NAME PRESENT')
else:
    print('LAST_NAME MISSING')