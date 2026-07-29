from pathlib import Path
content = Path('main.py').read_text(encoding='utf-8')

if 'StaticFiles(directory=".")' in content or "StaticFiles(directory='.')" in content:
    print('DANGER: ROOT DIRECTORY IS EXPOSED AS STATIC FILES')
    print('Anyone can download your .env, database, and source code!')
else:
    print('Root not exposed as static - this specific risk is not present')

# Also check what static directories are mounted
lines = content.splitlines()
for i, line in enumerate(lines, 1):
    if 'StaticFiles' in line:
        print(f'Line {i}: {line.strip()}')