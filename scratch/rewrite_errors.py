import re

# 1. Update AuthService
with open('lib/services/auth_service.dart', 'r', encoding='utf-8') as f:
    auth_content = f.read()

old_auth = """  static Future<bool> registerUserWithPassword(String email, String password, String phone, String role, String gender, {String? childName, String? vehicleType}) async {
    final supabase = Supabase.instance.client;
    if (childName != null) currentChildName = childName;
    try {
      final cleanEmail = email.toLowerCase().trim();
      
      // Create user in Supabase Auth
      final authResponse = await supabase.auth.signUp(
        email: cleanEmail,
        password: password,
      );

      if (authResponse.user == null) return false;

      // Insert into users table
      final data = {
        'id': authResponse.user!.id,
        'email': cleanEmail,
        'phone': phone.trim(),
        'role': role,
        'gender': gender,
      };
      if (childName != null) data['child_name'] = childName;
      if (vehicleType != null) data['vehicle_type'] = vehicleType;

      await supabase.from('users').upsert(data);
      return true;
    } catch (e) {
      print('Error saving to Supabase: $e');
      return false;
    }
  }"""

new_auth = """  static Future<String?> registerUserWithPassword(String email, String password, String phone, String role, String gender, {String? childName, String? vehicleType}) async {
    final supabase = Supabase.instance.client;
    if (childName != null) currentChildName = childName;
    try {
      final cleanEmail = email.toLowerCase().trim();
      
      // Create user in Supabase Auth
      final authResponse = await supabase.auth.signUp(
        email: cleanEmail,
        password: password,
      );

      if (authResponse.user == null) return "Unknown error: No user returned from Supabase.";

      // Insert into users table
      final data = {
        'id': authResponse.user!.id,
        'email': cleanEmail,
        'phone': phone.trim(),
        'role': role,
        'gender': gender,
      };
      if (childName != null) data['child_name'] = childName;
      if (vehicleType != null) data['vehicle_type'] = vehicleType;

      await supabase.from('users').upsert(data);
      return null; // Success (no error)
    } on AuthException catch (e) {
      return e.message; // Return the exact error message from Supabase Auth!
    } catch (e) {
      return e.toString();
    }
  }"""

auth_content = auth_content.replace(old_auth, new_auth)
with open('lib/services/auth_service.dart', 'w', encoding='utf-8') as f:
    f.write(auth_content)


def patch_register_screen(filepath, role):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # The exact regex to find the success logic
    old_logic = "final success = await AuthService.registerUserWithPassword"
    if role == 'parent':
        # Find exactly where it is called
        match = re.search(r"(final success = await AuthService\.registerUserWithPassword.*?;\s*setState\(\(\) => _isLoading = false\);\s*if \(!mounted\) return;\s*)if \(success\) \{", content)
        if match:
            start_idx = match.start()
            
            # Find the else block ending
            else_idx = content.find("Failed to register. Email may already be in use.", start_idx)
            end_idx = content.find("}", else_idx) + 1
            
            old_block = content[start_idx:end_idx]
            
            new_block = """final errorMessage = await AuthService.registerUserWithPassword(email, password, phone, 'parent', _gender, childName: _children[0]['name']!.text.trim());

    setState(() => _isLoading = false);
    if (!mounted) return;

    if (errorMessage == null) {
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => OtpScreen(
            email: email,
            onSuccess: () {
              Navigator.pushAndRemoveUntil(
                context,
                MaterialPageRoute(builder: (_) => const ParentDashboard()),
                (route) => false,
              );
            },
          ),
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Registration Failed: $errorMessage'), backgroundColor: Colors.red, duration: const Duration(seconds: 5)),
      );
    }"""
            content = content.replace(old_block, new_block)
    else:
        # For Driver
        match = re.search(r"(final success = await AuthService\.registerUserWithPassword.*?;\s*setState\(\(\) => _isLoading = false\);\s*if \(!mounted\) return;\s*)if \(success\) \{", content)
        if match:
            start_idx = match.start()
            else_idx = content.find("Failed to register. Email may already be in use.", start_idx)
            end_idx = content.find("}", else_idx) + 1
            
            old_block = content[start_idx:end_idx]
            
            new_block = """final errorMessage = await AuthService.registerUserWithPassword(email, password, phone, 'driver', _gender);

    setState(() => _isLoading = false);
    if (!mounted) return;

    if (errorMessage == null) {
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => OtpScreen(
            email: email,
            onSuccess: () {
              Navigator.pushAndRemoveUntil(
                context,
                MaterialPageRoute(builder: (_) => const DriverDashboard()),
                (route) => false,
              );
            },
          ),
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Registration Failed: $errorMessage'), backgroundColor: Colors.red, duration: const Duration(seconds: 5)),
      );
    }"""
            content = content.replace(old_block, new_block)
            
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

patch_register_screen('lib/screens/parent/parent_register_screen.dart', 'parent')
patch_register_screen('lib/screens/driver/driver_register_screen.dart', 'driver')

print("Patched errors!")
