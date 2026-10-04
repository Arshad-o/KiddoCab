import re

with open('lib/screens/parent_dashboard.dart', 'r', encoding='utf-8') as f:
    content = f.read()

# I will use a very greedy regex to replace the entire _listenToDriverStatus method
# to ensure it is 100% syntactically correct.

pattern = re.compile(r'void _listenToDriverStatus\(\) \{.*?\}\)\.subscribe\(\);\s*\}', re.DOTALL)

new_method = """void _listenToDriverStatus() {
    _locationsChannel = _supabase.channel('public:locations').onPostgresChanges(
      event: PostgresChangeEvent.insert,
      schema: 'public',
      table: 'locations',
      callback: (payload) {
        final newRecord = payload.newRecord;
        if (mounted) {
          setState(() {
            _driverPosition = LatLng(newRecord['latitude'], newRecord['longitude']);
          });
          if (_mapController != null && _driverPosition != null) {
            _mapController!.animateCamera(CameraUpdate.newLatLngZoom(_driverPosition!, 16.0));
          }
        }
        
        if (!_hasTriggeredStartNotification) {
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
    ).subscribe();
  }"""

content = re.sub(pattern, new_method, content)

with open('lib/screens/parent_dashboard.dart', 'w', encoding='utf-8') as f:
    f.write(content)
