import os
import re

def update_file(path, search, replace):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace(search, replace)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# 1. Update AuthService
auth_service = """import 'package:supabase_flutter/supabase_flutter.dart';

class AuthService {
  static String? currentChildName;

  static Future<bool> checkUserExists(String identifier) async {
    final supabase = Supabase.instance.client;
    final response = await supabase
        .from('users')
        .select('id')
        .or('email.eq.$identifier,phone.eq.$identifier')
        .limit(1);
    return response.isNotEmpty;
  }

  static Future<void> registerUser(String email, String phone, String role, {String? childName}) async {
    final supabase = Supabase.instance.client;
    if (childName != null) currentChildName = childName;
    try {
      await supabase.from('users').insert({
        'email': email.toLowerCase(),
        'phone': phone,
        'role': role,
        'child_name': childName,
      });
    } catch (e) {
      print('Error saving to Supabase: $e');
    }
  }

  static Future<bool> sendOtp(String email) async {
    try {
      await Supabase.instance.client.auth.signInWithOtp(
        email: email,
        shouldCreateUser: true,
      );
      return true;
    } catch (e) {
      print('OTP Send Error: $e');
      return false;
    }
  }

  static Future<bool> verifyOtp(String email, String token) async {
    try {
      final res = await Supabase.instance.client.auth.verifyOTP(
        type: OtpType.email,
        token: token,
        email: email,
      );
      return res.session != null;
    } catch (e) {
      print('OTP Verify Error: $e');
      return false;
    }
  }
}
"""
with open('lib/services/auth_service.dart', 'w', encoding='utf-8') as f:
    f.write(auth_service)

# 2. Update OtpScreen
with open('lib/screens/auth/otp_screen.dart', 'r', encoding='utf-8') as f:
    otp_content = f.read()

otp_content = otp_content.replace(
    "final String expectedOtp;", 
    "// expectedOtp removed for Supabase Auth"
)
otp_content = otp_content.replace(
    "required this.expectedOtp,", 
    "// required this.expectedOtp,"
)

otp_content = otp_content.replace(
    "import 'package:flutter/material.dart';",
    "import 'package:flutter/material.dart';\nimport '../../services/auth_service.dart';"
)

verify_fn = """  Future<void> _verifyOtp() async {
    final isValid = await AuthService.verifyOtp(widget.email, _otpController.text.trim());
    if (isValid) {
      widget.onSuccess();
    } else {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Invalid OTP! Please try again.'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }"""
otp_content = re.sub(r'  void _verifyOtp\(\) \{[\s\S]*?\}\n  \}', verify_fn, otp_content)

with open('lib/screens/auth/otp_screen.dart', 'w', encoding='utf-8') as f:
    f.write(otp_content)

# Replace in login/register screens
def rewrite_login_register(path):
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    
    # logic
    c = re.sub(r"final otp = EmailService\.generateOTP\(\);", "", c)
    c = re.sub(r"final success = await EmailService\.sendOTP\(email, otp\);", "final success = await AuthService.sendOtp(email);", c)
    c = re.sub(r"final success = await EmailService\.sendOTP\(email, EmailService\.generateOTP\(\)\);", "final success = await AuthService.sendOtp(email);", c)
    
    c = c.replace("expectedOtp: otp,", "// expectedOtp removed")
    
    # for register screens that inline it without saving to a variable:
    c = re.sub(r"EmailService\.sendOTP\(email, otp\)", "AuthService.sendOtp(email)", c)
    
    c = c.replace("import '../../services/email_service.dart';", "")
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)

rewrite_login_register('lib/screens/parent/parent_login_screen.dart')
rewrite_login_register('lib/screens/driver/driver_login_screen.dart')
rewrite_login_register('lib/screens/parent/parent_register_screen.dart')
rewrite_login_register('lib/screens/driver/driver_register_screen.dart')
