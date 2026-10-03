import re
import os

# 1. Fix cab_selection_screen.dart
with open('lib/screens/parent/cab_selection_screen.dart', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace(r"'\${trip['seats']} seats left'", r"'\${trip[\"seats\"]} seats left'")
with open('lib/screens/parent/cab_selection_screen.dart', 'w', encoding='utf-8') as f:
    f.write(c)

# 2. Fix parent_login_screen.dart
with open('lib/screens/parent/parent_login_screen.dart', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace("builder: (_) => const OtpScreen(", "builder: (_) => OtpScreen(")
with open('lib/screens/parent/parent_login_screen.dart', 'w', encoding='utf-8') as f:
    f.write(c)

# 3. Fix parent_register_screen.dart
with open('lib/screens/parent/parent_register_screen.dart', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace("builder: (_) => const OtpScreen(", "builder: (_) => OtpScreen(")
with open('lib/screens/parent/parent_register_screen.dart', 'w', encoding='utf-8') as f:
    f.write(c)

# 4. Fix notification_service.dart
notif_code = """import 'package:flutter_local_notifications/flutter_local_notifications.dart';

class NotificationService {
  static final FlutterLocalNotificationsPlugin _notificationsPlugin = FlutterLocalNotificationsPlugin();

  static Future<void> init() async {
    const AndroidInitializationSettings androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');
    const DarwinInitializationSettings iosSettings = DarwinInitializationSettings();
    const InitializationSettings initSettings = InitializationSettings(android: androidSettings, iOS: iosSettings);
    
    await _notificationsPlugin.initialize(initSettings);
    
    // Request permission for Android 13+
    _notificationsPlugin
        .resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>()
        ?.requestNotificationsPermission();
  }

  static Future<void> showNotification({required int id, required String title, required String body}) async {
    const AndroidNotificationDetails androidDetails = AndroidNotificationDetails(
      'kiddocab_channel',
      'KiddoCab Notifications',
      importance: Importance.max,
      priority: Priority.high,
      icon: '@mipmap/ic_launcher',
    );
    const NotificationDetails details = NotificationDetails(android: androidDetails);
    
    await _notificationsPlugin.show(id, title, body, notificationDetails: details);
  }
}
"""
with open('lib/services/notification_service.dart', 'w', encoding='utf-8') as f:
    f.write(notif_code)

# 5. Fix widget_test.dart
test_code = """import 'package:flutter_test/flutter_test.dart';
import 'package:kiddo_cab/main.dart';

void main() {
  testWidgets('App starts', (WidgetTester tester) async {
    await tester.pumpWidget(const KiddoCabApp());
  });
}
"""
with open('test/widget_test.dart', 'w', encoding='utf-8') as f:
    f.write(test_code)
