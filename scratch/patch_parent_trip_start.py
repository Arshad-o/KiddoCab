import re

with open('lib/screens/parent_dashboard.dart', 'r', encoding='utf-8') as f:
    code = f.read()

# Add the 'ALL' condition to the security alerts listener
old_alert = """        // If the alert is for THIS parent's child
        if (newRecord['child_name'] == (AuthService.currentChildName ?? 'Emma Smith')) {"""
new_alert = """        // Global Trip Started Alert
        if (newRecord['child_name'] == 'ALL') {
          NotificationService.showNotification(
            id: 888,
            title: '🚀 TRIP STARTED',
            body: newRecord['message'],
          );
          return;
        }

        // If the alert is for THIS parent's child specifically
        if (newRecord['child_name'] == (AuthService.currentChildName ?? 'Emma Smith')) {"""
code = code.replace(old_alert, new_alert)

with open('lib/screens/parent_dashboard.dart', 'w', encoding='utf-8') as f:
    f.write(code)
