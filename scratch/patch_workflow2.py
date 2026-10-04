import re

with open('.github/workflows/build-apk.yml', 'r', encoding='utf-8') as f:
    content = f.read()

old_build = """      - name: Build APK (with Military-Grade Obfuscation)
        run: flutter build apk --release --obfuscate --split-debug-info=build/app/outputs/symbols > build_log.txt 2>&1
        continue-on-error: true"""

new_build = """      - name: Build APK (with Military-Grade Obfuscation)
        run: flutter build apk --release --obfuscate --split-debug-info=build/app/outputs/symbols
        continue-on-error: false"""

content = content.replace(old_build, new_build)

with open('.github/workflows/build-apk.yml', 'w', encoding='utf-8') as f:
    f.write(content)
