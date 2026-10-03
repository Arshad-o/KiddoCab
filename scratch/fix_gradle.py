with open('android/app/build.gradle.kts', 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace("compileSdk = flutter.compileSdkVersion", "compileSdk = 34")
content = content.replace("minSdk = flutter.minSdkVersion", "minSdk = 21")
content = content.replace("targetSdk = flutter.targetSdkVersion", "targetSdk = 34")
with open('android/app/build.gradle.kts', 'w', encoding='utf-8') as f:
    f.write(content)
