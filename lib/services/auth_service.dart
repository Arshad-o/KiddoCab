import 'package:supabase_flutter/supabase_flutter.dart';

class AuthService {
  static String? currentChildName;

  static Future<bool> checkUserExists(String identifier) async {
    final supabase = Supabase.instance.client;
    
    // Check if user exists by email or phone
    final response = await supabase
        .from('users')
        .select('id')
        .or('email.eq.\$identifier,phone.eq.\$identifier')
        .limit(1);
        
    return response.isNotEmpty;
  }

  static Future<void> registerUser(String email, String phone, String role, {String? childName}) async {
    final supabase = Supabase.instance.client;
    
    if (childName != null) {
      currentChildName = childName;
    }

    try {
      await supabase.from('users').insert({
        'email': email.toLowerCase(),
        'phone': phone,
        'role': role,
        'child_name': childName,
      });
    } catch (e) {
      print('Error saving to Supabase: \$e');
    }
  }
}
