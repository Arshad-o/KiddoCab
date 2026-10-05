import re

with open('.github/workflows/build-apk.yml', 'r', encoding='utf-8') as f:
    content = f.read()

old_patch = """      - name: Patch legacy AGP plugins
        run: |
          sed -i 's/android {/android {\\n    namespace "appmire.be.flutterjailbreakdetection"/g' ~/.pub-cache/hosted/pub.dev/flutter_jailbreak_detection-*/android/build.gradle"""

new_patch = """      - name: Patch legacy AGP plugins
        run: |
          sed -i 's/android {/android {\\n    namespace "appmire.be.flutterjailbreakdetection"/g' ~/.pub-cache/hosted/pub.dev/flutter_jailbreak_detection-*/android/build.gradle
          cat << 'EOF' >> ~/.pub-cache/hosted/pub.dev/flutter_jailbreak_detection-*/android/build.gradle
          
          android {
              compileOptions {
                  sourceCompatibility JavaVersion.VERSION_17
                  targetCompatibility JavaVersion.VERSION_17
              }
          }
          tasks.withType(org.jetbrains.kotlin.gradle.tasks.KotlinCompile).configureEach {
              kotlinOptions {
                  jvmTarget = "17"
              }
          }
          EOF"""

content = content.replace(old_patch, new_patch)

with open('.github/workflows/build-apk.yml', 'w', encoding='utf-8') as f:
    f.write(content)
