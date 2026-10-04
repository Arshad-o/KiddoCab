import 'package:supabase_flutter/supabase_flutter.dart' hide MapType;

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

  static Future<void> registerUser(String email, String phone, String role, {String? childName, String? vehicleType}) async {
    final supabase = Supabase.instance.client;
    if (childName != null) currentChildName = childName;
    try {
      final data = {
        'email': email.toLowerCase(),
        'phone': phone,
        'role': role,
      };
      if (childName != null) data['child_name'] = childName;
      if (vehicleType != null) data['vehicle_type'] = vehicleType;

      await supabase.from('users').insert(data);
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
