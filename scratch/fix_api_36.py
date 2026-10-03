with open('android/app/build.gradle.kts', 'r', encoding='utf-8') as f:
    gradle = f.read()

gradle = gradle.replace('compileSdk = 34', 'compileSdk = 36')
gradle = gradle.replace('targetSdk = 34', 'targetSdk = 36')
gradle = gradle.replace('desugar_jdk_libs:2.0.4', 'desugar_jdk_libs:2.1.4')

with open('android/app/build.gradle.kts', 'w', encoding='utf-8') as f:
    f.write(gradle)
