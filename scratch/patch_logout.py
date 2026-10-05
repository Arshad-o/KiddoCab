import re

def patch_logout(filepath, login_screen):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # The exact block for ParentDashboard
    old_logout = r"onPressed: \(\) async \{\s*await _supabase\.auth\.signOut\(\);\s*if \(mounted\) \{\s*Navigator\.pushAndRemoveUntil\(\s*context,\s*MaterialPageRoute\(builder: \(_\) => const " + login_screen + r"\(\)\),\s*\(route\) => false,\s*\);\s*\}\s*\}"
    
    new_logout = f"""onPressed: () async {{
              final bool? confirmLogout = await showDialog<bool>(
                context: context,
                builder: (BuildContext context) {{
                  return AlertDialog(
                    title: const Text('Confirm Logout'),
                    content: const Text('Do you really want to log out of KiddoCab?'),
                    actions: [
                      TextButton(
                        onPressed: () => Navigator.of(context).pop(false),
                        child: const Text('Cancel'),
                      ),
                      TextButton(
                        onPressed: () => Navigator.of(context).pop(true),
                        style: TextButton.styleFrom(foregroundColor: Colors.red),
                        child: const Text('Log Out'),
                      ),
                    ],
                  );
                }},
              );

              if (confirmLogout == true) {{
                await _supabase.auth.signOut();
                if (mounted) {{
                  Navigator.pushAndRemoveUntil(
                    context,
                    MaterialPageRoute(builder: (_) => const {login_screen}()),
                    (route) => false,
                  );
                }}
              }}
            }}"""

    # If the regex doesn't match, maybe it's written differently in driver_dashboard
    # Let's do a more robust string replace if regex fails
    content = re.sub(old_logout, new_logout, content)

    # In case driver uses AuthService.logout() or something else
    old_logout_driver = r"onPressed: \(\) async \{\s*await _supabase\.auth\.signOut\(\);\s*if \(mounted\) \{\s*Navigator\.pushAndRemoveUntil\(\s*context,\s*MaterialPageRoute\(builder: \(_\) => const " + login_screen + r"\(\)\),\s*\(route\) => false,\s*\);\s*\}\s*\}"
    content = re.sub(old_logout_driver, new_logout, content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

patch_logout('lib/screens/parent_dashboard.dart', 'ParentLoginScreen')
patch_logout('lib/screens/driver_dashboard.dart', 'DriverLoginScreen')
