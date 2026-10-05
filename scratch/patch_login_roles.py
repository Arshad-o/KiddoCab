import re
import glob

def patch_file(filepath, allowed_role):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Login screen patch
    if "login_screen" in filepath:
        old_check = "if (!(await AuthService.checkUserExists(identifier))) {"
        new_check = f"""final role = await AuthService.getUserRole(identifier);
    if (role == null) {{
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Account does not exist, please register.')));
      return;
    }}
    if (role != '{allowed_role}') {{
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('This email is registered as a ${{role.toUpperCase()}}. Please use the correct login portal.')));
      return;
    }}"""
        
        # Replace the entire if block
        pattern = re.compile(r'if \(!\(await AuthService\.checkUserExists\(identifier\)\)\) \{[\s\S]*?return;\s*\}')
        content = re.sub(pattern, new_check, content)

    # Register screen patch
    if "register_screen" in filepath:
        old_check = "if ((await AuthService.checkUserExists(email)) || (await AuthService.checkUserExists(phone))) {"
        new_check = f"""final existingRoleEmail = await AuthService.getUserRole(email);
      final existingRolePhone = await AuthService.getUserRole(phone);
      if (existingRoleEmail != null || existingRolePhone != null) {{
        final role = existingRoleEmail ?? existingRolePhone;"""
        
        content = content.replace(old_check, new_check)
        
        content = content.replace("const SnackBar(\n              content: Text('These credentials already exist! Please use a different email or phone.'),\n            ),", "SnackBar(\n              content: Text('This email or phone is already registered as a ${role?.toUpperCase()}!'),\n            ),")
        
        content = content.replace("const SnackBar(content: Text('User already exists with this email or phone number!'), backgroundColor: Colors.red),", "SnackBar(content: Text('This email or phone is already registered as a ${role?.toUpperCase()}!'), backgroundColor: Colors.red),")
        content = content.replace("const SnackBar(content: Text('User already exists with this email or phone number!'), backgroundColor: \nColors.red),", "SnackBar(content: Text('This email or phone is already registered as a ${role?.toUpperCase()}!'), backgroundColor: Colors.red),")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

patch_file('lib/screens/parent/parent_login_screen.dart', 'parent')
patch_file('lib/screens/driver/driver_login_screen.dart', 'driver')
patch_file('lib/screens/parent/parent_register_screen.dart', 'parent')
patch_file('lib/screens/driver/driver_register_screen.dart', 'driver')
