import re

with open('.github/workflows/build-apk.yml', 'r', encoding='utf-8') as f:
    content = f.read()

old_build = """      - name: Build APK
        run: flutter build apk --release > build_log.txt 2>&1"""

new_build = """      - name: Build APK (with Military-Grade Obfuscation)
        run: flutter build apk --release --obfuscate --split-debug-info=build/app/outputs/symbols > build_log.txt 2>&1"""

content = content.replace(old_build, new_build)

with open('.github/workflows/build-apk.yml', 'w', encoding='utf-8') as f:
    f.write(content)
