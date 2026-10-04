import re

with open('lib/screens/driver_dashboard.dart', 'r', encoding='utf-8') as f:
    code = f.read()

old_trigger = """  void _triggerAntiSkipAlarm(List<String> missing) {
    // Attempt system beep
    print('\\x07');"""

new_trigger = """  void _triggerAntiSkipAlarm(List<String> missing) async {
    // Attempt system beep
    print('\\x07');
    
    // 1. Send Alert to Parents via Supabase
    for (String child in missing) {
      try {
        await _supabase.from('alerts').insert({
          'child_name': child,
          'message': 'CRITICAL: Driver left location without FRS scanning!',
        });
      } catch (e) {
        print('Error sending alert: $e');
      }
    }"""

code = code.replace(old_trigger, new_trigger)

with open('lib/screens/driver_dashboard.dart', 'w', encoding='utf-8') as f:
    f.write(code)
