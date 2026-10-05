import re

def improve_validation_messages(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    old_logic = """    final existingRoleEmail = await AuthService.getUserRole(email);
      final existingRolePhone = await AuthService.getUserRole(phone);
      if (existingRoleEmail != null || existingRolePhone != null) {
        final role = existingRoleEmail ?? existingRolePhone;
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('These credentials already exist! Please use a different email or phone.'),
            backgroundColor: Colors.red,
            duration: Duration(seconds: 4),
          ),
        );
      }
      return;
    }"""

    new_logic = """    final existingRoleEmail = await AuthService.getUserRole(email);
    if (existingRoleEmail != null) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('This EMAIL is already registered as a ${existingRoleEmail.toUpperCase()}!'),
            backgroundColor: Colors.red,
            duration: const Duration(seconds: 4),
          ),
        );
      }
      return;
    }

    final existingRolePhone = await AuthService.getUserRole(phone);
    if (existingRolePhone != null) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('This PHONE NUMBER is already registered as a ${existingRolePhone.toUpperCase()}!'),
            backgroundColor: Colors.red,
            duration: const Duration(seconds: 4),
          ),
        );
      }
      return;
    }"""

    if old_logic in content:
        content = content.replace(old_logic, new_logic)
    else:
        # Fallback regex if exact string doesn't match
        pattern = r"final existingRoleEmail = await AuthService\.getUserRole\(email\);[\s\S]*?return;\s*\}"
        content = re.sub(pattern, new_logic, content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

improve_validation_messages('lib/screens/parent/parent_register_screen.dart')
improve_validation_messages('lib/screens/driver/driver_register_screen.dart')
