import os

# 1. Update build.gradle.kts
with open('android/app/build.gradle.kts', 'r', encoding='utf-8') as f:
    gradle = f.read()

if "isCoreLibraryDesugaringEnabled" not in gradle:
    gradle = gradle.replace(
        "targetCompatibility = JavaVersion.VERSION_17", 
        "targetCompatibility = JavaVersion.VERSION_17\n        isCoreLibraryDesugaringEnabled = true"
    )

if "coreLibraryDesugaring(" not in gradle:
    gradle += "\n\ndependencies {\n    coreLibraryDesugaring(\"com.android.tools:desugar_jdk_libs:2.0.4\")\n}\n"

with open('android/app/build.gradle.kts', 'w', encoding='utf-8') as f:
    f.write(gradle)

# 2. Update AndroidManifest.xml
with open('android/app/src/main/AndroidManifest.xml', 'r', encoding='utf-8') as f:
    manifest = f.read()

if "android.permission.POST_NOTIFICATIONS" not in manifest:
    manifest = manifest.replace(
        '<uses-permission android:name="android.permission.INTERNET" />',
        '<uses-permission android:name="android.permission.INTERNET" />\n    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />\n    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED"/>\n    <uses-permission android:name="android.permission.VIBRATE" />'
    )

with open('android/app/src/main/AndroidManifest.xml', 'w', encoding='utf-8') as f:
    f.write(manifest)
