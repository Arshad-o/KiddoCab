import re

with open('.github/workflows/build-apk.yml', 'r', encoding='utf-8') as f:
    content = f.read()

old_build = """      - name: Build APK (with Military-Grade Obfuscation)
        run: flutter build apk --release --obfuscate --split-debug-info=build/app/outputs/symbols
        continue-on-error: false"""

new_build = """      - name: Patch legacy AGP plugins
        run: |
          sed -i 's/android {/android {\\n    namespace "appmire.be.flutterjailbreakdetection"/g' ~/.pub-cache/hosted/pub.dev/flutter_jailbreak_detection-*/android/build.gradle
          
      - name: Build APK (with Military-Grade Obfuscation)
        run: flutter build apk --release --obfuscate --split-debug-info=build/app/outputs/symbols
        continue-on-error: false"""

content = content.replace(old_build, new_build)

with open('.github/workflows/build-apk.yml', 'w', encoding='utf-8') as f:
    f.write(content)
