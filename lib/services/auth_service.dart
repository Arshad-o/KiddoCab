import 'package:supabase_flutter/supabase_flutter.dart' hide MapType;

class AuthService {
  static String? currentChildName;

  static Future<String?> getUserRole(String identifier) async {
    final supabase = Supabase.instance.client;
    final lowerId = identifier.toLowerCase().trim();
    final response = await supabase
        .from('users')
        .select('role')
        .or('email.eq.$lowerId,phone.eq.$lowerId')
        .limit(1);
    
    if (response.isNotEmpty) {
      return response.first['role'] as String?;
    }
    return null;
  }

  static Future<bool> checkUserExists(String identifier) async {
    final role = await getUserRole(identifier);
    return role != null;
  }

  static Future<String?> registerUserWithPassword(String email, String password, String phone, String role, String gender, {String? childName, String? vehicleType}) async {
    final supabase = Supabase.instance.client;
    if (childName != null) currentChildName = childName;
    try {
      final cleanEmail = email.toLowerCase().trim();
      
      // Create user in Supabase Auth
      final authResponse = await supabase.auth.signUp(
        email: cleanEmail,
        password: password,
      );

      if (authResponse.user == null) return "Unknown error: No user returned from Supabase.";

      // Insert into users table
      final data = {
        'id': authResponse.user!.id,
        'email': cleanEmail,
        'phone': phone.trim(),
        'role': role,
        'gender': gender,
      };
      if (childName != null) data['child_name'] = childName;
      if (vehicleType != null) data['vehicle_type'] = vehicleType;

      await supabase.from('users').insert(data);
      return null; // Success (no error)
    } on AuthException catch (e) {
      return e.message; // Return the exact error message from Supabase Auth!
    } catch (e) {
      return e.toString();
    }
  }

  static Future<bool> loginWithPassword(String email, String password) async {
    try {
      final res = await Supabase.instance.client.auth.signInWithPassword(
        email: email.toLowerCase().trim(),
        password: password,
      );
      return res.session != null;
    } catch (e) {
      print('Login Error: $e');
      return false;
    }
  }

  static Future<void> logout() async {
    await Supabase.instance.client.auth.signOut();
  }

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
