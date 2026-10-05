import re

for filepath in ['lib/screens/parent/parent_register_screen.dart', 'lib/screens/driver/driver_register_screen.dart']:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # We need to add the import for OtpScreen
    if "import '../auth/otp_screen.dart';" not in content:
        content = content.replace("import '../../services/auth_service.dart';", "import '../../services/auth_service.dart';\nimport '../auth/otp_screen.dart';")

    # Change the success block
    # from: Navigator.pushAndRemoveUntil(...) to OtpScreen
    old_success_parent = r"if \(success\) \{\s*Navigator\.pushAndRemoveUntil\(\s*context,\s*MaterialPageRoute\(builder: \(_\) => const ParentDashboard\(\)\),\s*\(route\) => false,\s*\);\s*\}"
    new_success_parent = """if (success) {
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
    }"""
    
    old_success_driver = r"if \(success\) \{\s*Navigator\.pushAndRemoveUntil\(\s*context,\s*MaterialPageRoute\(builder: \(_\) => const DriverDashboard\(\)\),\s*\(route\) => false,\s*\);\s*\}"
    new_success_driver = """if (success) {
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
    }"""

    content = re.sub(old_success_parent, new_success_parent, content)
    content = re.sub(old_success_driver, new_success_driver, content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
