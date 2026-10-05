import re

with open('lib/screens/parent/parent_login_screen.dart', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace sendOtp logic with loginWithPassword
old_logic = r"    // Show a loading snackbar[\s\S]*?Failed to send OTP\. Please check your email or try again\.'\)\),\s*\);\s*\}"

new_logic = """    // Show a loading snackbar
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Logging in...')),
    );

    final password = _passwordController.text.trim();
    if (password.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please enter your password')));
      return;
    }

    final success = await AuthService.loginWithPassword(email, password);

    if (!mounted) return;

    if (success) {
      Navigator.pushAndRemoveUntil(
        context,
        MaterialPageRoute(builder: (_) => const ParentDashboard()),
        (route) => false,
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Invalid email or password.'), backgroundColor: Colors.red),
      );
    }"""

content = re.sub(old_logic, new_logic, content)

# Remove unused imports
content = content.replace("import '../auth/otp_screen.dart';", "")

with open('lib/screens/parent/parent_login_screen.dart', 'w', encoding='utf-8') as f:
    f.write(content)
