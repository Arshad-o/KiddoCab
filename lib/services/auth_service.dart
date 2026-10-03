import 'package:supabase_flutter/supabase_flutter.dart';

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
