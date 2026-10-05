import re

for filepath in ['lib/screens/parent/parent_register_screen.dart', 'lib/screens/driver/driver_register_screen.dart']:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the exact block that needs removing
    content = re.sub(
        r"final success = await AuthService\.sendOtp\(email\);[\s\S]*?\} else \{\s*ScaffoldMessenger\.of\(context\)\.showSnackBar\([\s\S]*?\);\s*\}",
        "",
        content
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
