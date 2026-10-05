import re

with open('pubspec.yaml', 'r', encoding='utf-8') as f:
    content = f.read()

# Add flutter_launcher_icons dependency
if "flutter_launcher_icons:" not in content:
    content = content.replace("dev_dependencies:\n", "dev_dependencies:\n  flutter_launcher_icons: ^0.14.3\n")

# Add configuration block
config = """
flutter_launcher_icons:
  android: "launcher_icon"
  ios: true
  image_path: "assets/images/logo.png.jpg"
  min_sdk_size: 21 # android min sdk min:16, default: 21
"""

if "flutter_launcher_icons:" not in content.split("dev_dependencies:")[1]:
     content += config

with open('pubspec.yaml', 'w', encoding='utf-8') as f:
    f.write(content)
