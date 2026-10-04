import re

with open('lib/screens/welcome_screen.dart', 'r', encoding='utf-8') as f:
    code = f.read()

if "import 'admin/admin_dashboard.dart';" not in code:
    code = code.replace("import 'parent/parent_login_screen.dart';", "import 'parent/parent_login_screen.dart';\nimport 'admin/admin_dashboard.dart';")

old_ui = """                ElevatedButton(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => const DriverLoginScreen()),
                    );
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: theme.colorScheme.secondary,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 16),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  child: const Text('I am a Driver', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                ),"""

new_ui = """                ElevatedButton(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => const DriverLoginScreen()),
                    );
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: theme.colorScheme.secondary,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 16),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  child: const Text('I am a Driver', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                ),
                
                const SizedBox(height: 40),
                TextButton.icon(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => const AdminDashboard()),
                    );
                  },
                  icon: const Icon(Icons.admin_panel_settings, color: Colors.grey),
                  label: const Text('Admin Portal', style: TextStyle(color: Colors.grey)),
                ),"""

code = code.replace(old_ui, new_ui)

with open('lib/screens/welcome_screen.dart', 'w', encoding='utf-8') as f:
    f.write(code)
