class AuthService {
  // Mock database for registered users
  static final List<String> registeredEmails = [];
  static final List<String> registeredPhones = [];
  
  static String? currentChildName;

  static bool checkUserExists(String identifier) {
    return registeredEmails.contains(identifier.toLowerCase()) || 
           registeredPhones.contains(identifier);
  }

  static void registerUser(String email, String phone, {String? childName}) {
    if (email.isNotEmpty) registeredEmails.add(email.toLowerCase());
    if (phone.isNotEmpty) registeredPhones.add(phone);
    if (childName != null) currentChildName = childName;
  }
}
