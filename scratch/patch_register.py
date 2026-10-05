import re
import os

def patch_register_screen(filepath, role):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Add Controllers and Gender state
    if "_passwordController" not in content:
        content = re.sub(
            r"final _emailController = TextEditingController\(\);",
            r"final _emailController = TextEditingController();\n  final _passwordController = TextEditingController();\n  final _rePasswordController = TextEditingController();\n  String _gender = 'male';",
            content
        )

    # Modify _proceed function
    # Replace OTP check logic with Password Auth logic
    old_proceed = r"    if \(mounted\) \{\s*ScaffoldMessenger\.of\(context\)\.showSnackBar\(\s*const SnackBar\(content: Text\('Sending OTP\.\.\.'\)\),\s*\);\s*\}\s*final success = await AuthService\.sendOtp\(email\);\s*setState\(\(\) => _isLoading = false\);\s*if \(!mounted\) return;\s*if \(success\) \{[\s\S]*?\} else \{\s*ScaffoldMessenger\.of\(context\)\.showSnackBar\(\s*SnackBar\(content: Text\('Failed to send OTP\.(?:.*?)\'\)(?:.*?)?\),\s*\);\s*\}"

    new_proceed = f"""
    final password = _passwordController.text.trim();
    final rePassword = _rePasswordController.text.trim();
    if (password != rePassword) {{
      setState(() => _isLoading = false);
      if (mounted) {{
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Passwords do not match!'), backgroundColor: Colors.red));
      }}
      return;
    }}

    if (mounted) {{
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Creating Account...')));
    }}

    final success = await AuthService.registerUserWithPassword(email, password, phone, '{role}', _gender);

    setState(() => _isLoading = false);
    if (!mounted) return;

    if (success) {{
      Navigator.pushAndRemoveUntil(
        context,
        MaterialPageRoute(builder: (_) => const {"ParentDashboard()" if role == 'parent' else "DriverDashboard()"}),
        (route) => false,
      );
    }} else {{
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Failed to register. Email may already be in use.'), backgroundColor: Colors.red),
      );
    }}"""
    
    # We also need to extract `firstChildName` if it's parent logic. Let's just pass none or keep it simple.
    if role == 'parent':
        new_proceed = new_proceed.replace("registerUserWithPassword(email, password, phone, 'parent', _gender)", "registerUserWithPassword(email, password, phone, 'parent', _gender, childName: _children[0]['name']!.text.trim())")
    
    content = re.sub(old_proceed, new_proceed, content)

    # Insert Gender and Password UI before Terms
    gender_ui = r"""
              const SizedBox(height: 24),
              Text('Gender', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold, color: theme.colorScheme.primary)),
              Row(
                children: [
                  Expanded(
                    child: RadioListTile<String>(
                      title: const Text('Male'),
                      value: 'male',
                      groupValue: _gender,
                      onChanged: (value) => setState(() => _gender = value!),
                      secondary: Image.asset('assets/images/male.jpg', width: 40, height: 40),
                    ),
                  ),
                  Expanded(
                    child: RadioListTile<String>(
                      title: const Text('Female'),
                      value: 'female',
                      groupValue: _gender,
                      onChanged: (value) => setState(() => _gender = value!),
                      secondary: Image.asset('assets/images/female.jpg', width: 40, height: 40),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _passwordController,
                decoration: const InputDecoration(labelText: 'Password *', border: OutlineInputBorder()),
                obscureText: true,
                validator: (value) => value == null || value.length < 6 ? 'Password must be at least 6 characters' : null,
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _rePasswordController,
                decoration: const InputDecoration(labelText: 'Re-enter Password *', border: OutlineInputBorder()),
                obscureText: true,
                validator: (value) => value == null || value.isEmpty ? 'Required' : null,
              ),
              const SizedBox(height: 24),"""
    
    # We'll inject this before the terms checkbox
    content = content.replace("const SizedBox(height: 24),\n              Row(\n                children: [\n                  Checkbox(\n                    value: _acceptedTerms,", gender_ui + "\n              Row(\n                children: [\n                  Checkbox(\n                    value: _acceptedTerms,")

    # Remove otp import
    content = content.replace("import '../auth/otp_screen.dart';", "")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

patch_register_screen('lib/screens/parent/parent_register_screen.dart', 'parent')
patch_register_screen('lib/screens/driver/driver_register_screen.dart', 'driver')
