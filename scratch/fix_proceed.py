import os

def fix_proceed(filepath, role):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find where to start replacing
    # We will search for:
    # "if (mounted) {\n      ScaffoldMessenger.of(context).showSnackBar(\n        const SnackBar(content: Text('Sending OTP...'))"
    # Or just use regex to replace everything after the existing role check until the end of the method.
    
    start_str = "    if (mounted) {\n      ScaffoldMessenger.of(context).showSnackBar("
    
    # We want to replace from start_str to "\n  }\n\n  Widget" for parent, or "\n  }\n\n  @override" for driver
    start_index = content.find(start_str)
    if start_index == -1:
        print(f"Could not find start_str in {filepath}")
        return
        
    end_index = content.find("\n  }\n\n  Widget", start_index)
    if end_index == -1:
        end_index = content.find("\n  }\n\n  @override", start_index)
        
    if end_index == -1:
        print(f"Could not find end of method in {filepath}")
        return

    child_name_arg = "childName: _children[0]['name']!.text.trim()" if role == 'parent' else ""
    child_name_param = f", {child_name_arg}" if role == 'parent' else ""

    dashboard_route = "ParentDashboard" if role == 'parent' else "DriverDashboard"

    new_logic = f"""    final password = _passwordController.text.trim();
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

    final success = await AuthService.registerUserWithPassword(email, password, phone, '{role}', _gender{child_name_param});

    setState(() => _isLoading = false);
    if (!mounted) return;

    if (success) {{
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => OtpScreen(
            email: email,
            onSuccess: () {{
              Navigator.pushAndRemoveUntil(
                context,
                MaterialPageRoute(builder: (_) => const {dashboard_route}()),
                (route) => false,
              );
            }},
          ),
        ),
      );
    }} else {{
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Failed to register. Email may already be in use.'), backgroundColor: Colors.red),
      );
    }}"""

    new_content = content[:start_index] + new_logic + content[end_index:]

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
        print(f"Patched {filepath}")

fix_proceed('lib/screens/parent/parent_register_screen.dart', 'parent')
fix_proceed('lib/screens/driver/driver_register_screen.dart', 'driver')
