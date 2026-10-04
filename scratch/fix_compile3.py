import re

with open('lib/screens/parent_dashboard.dart', 'r', encoding='utf-8') as f:
    content = f.read()

old_block = """        if (!_hasTriggeredStartNotification) {
          _hasTriggeredStartNotification = true;
          NotificationService.showNotification(
            id: 1,
          title: 'dYs? Trip Started!',
          body: 'Your KiddoCab has started broadcasting its live location.',
        );
        Future.delayed(const Duration(seconds: 15), () {
          NotificationService.showNotification(
            id: 2,
            title: 'dYs? Almost There!',
            body: 'The KiddoCab is 2 stops away. Please get ready.',
          );
        });
      },
    ).subscribe();"""

new_block = """        if (!_hasTriggeredStartNotification) {
          _hasTriggeredStartNotification = true;
          NotificationService.showNotification(
            id: 1,
            title: 'Trip Started!',
            body: 'Your KiddoCab has started broadcasting its live location.',
          );
          Future.delayed(const Duration(seconds: 15), () {
            NotificationService.showNotification(
              id: 2,
              title: 'Almost There!',
              body: 'The KiddoCab is 2 stops away. Please get ready.',
            );
          });
        }
      },
    ).subscribe();"""

content = content.replace(old_block, new_block)

with open('lib/screens/parent_dashboard.dart', 'w', encoding='utf-8') as f:
    f.write(content)
