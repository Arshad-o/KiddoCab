import re

with open('lib/services/auth_service.dart', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the last closing brace
content = content.strip().rsplit('}', 1)[0]

new_methods = """
  static Future<bool> sendOtp(String email) async {
    try {
      await Supabase.instance.client.auth.resend(
        type: OtpType.signup,
        email: email.toLowerCase().trim(),
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
        type: OtpType.signup,
        token: token.trim(),
        email: email.toLowerCase().trim(),
      );
      return res.session != null;
    } catch (e) {
      print('OTP Verify Error: $e');
      return false;
    }
  }
}
"""

content += new_methods

with open('lib/services/auth_service.dart', 'w', encoding='utf-8') as f:
    f.write(content)
