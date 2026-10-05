import re

with open('lib/screens/driver/driver_register_screen.dart', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("'image': 'assets/images/cab.avif'", "'image': 'assets/images/cab.png'")

with open('lib/screens/driver/driver_register_screen.dart', 'w', encoding='utf-8') as f:
    f.write(content)
