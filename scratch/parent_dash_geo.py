import re

with open('lib/screens/parent_dashboard.dart', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the _listenToDriverStatus method
old_method = r"  void _listenToDriverStatus\(\) \{[\s\S]*?\}\)\.subscribe\(\);\n  \}"

new_method = """  bool _notifiedTripStart = false;
  bool _notifiedTwoStopsAway = false;

  // Mocking 10 Stops along a route
  final List<Map<String, double>> _routeStops = [
    {'lat': 28.6139, 'lng': 77.2090}, // Stop 1
    {'lat': 28.6145, 'lng': 77.2095}, // Stop 2
    {'lat': 28.6150, 'lng': 77.2100}, // Stop 3
    {'lat': 28.6155, 'lng': 77.2105}, // Stop 4
    {'lat': 28.6160, 'lng': 77.2110}, // Stop 5
    {'lat': 28.6165, 'lng': 77.2115}, // Stop 6
    {'lat': 28.6170, 'lng': 77.2120}, // Stop 7
    {'lat': 28.6175, 'lng': 77.2125}, // Stop 8 (Trigger Stop for Parent at Stop 10)
    {'lat': 28.6180, 'lng': 77.2130}, // Stop 9
    {'lat': 28.6185, 'lng': 77.2135}, // Stop 10 (Parent's Stop)
  ];

  void _listenToDriverStatus() {
    _locationsChannel = _supabase.channel('public:locations').onPostgresChanges(
      event: PostgresChangeEvent.insert,
      schema: 'public',
      table: 'locations',
      callback: (payload) {
        final newRecord = payload.newRecord;
        final driverLat = newRecord['latitude'] as double;
        final driverLng = newRecord['longitude'] as double;

        // 1. Notify that trip started (only once)
        if (!_notifiedTripStart) {
          NotificationService.showNotification(
            id: 1,
            title: '🚐 Trip Started!',
            body: 'Your KiddoCab has started broadcasting its live location.',
          );
          _notifiedTripStart = true;
        }

        // 2. Geofencing Logic for "2 Stops Away"
        if (!_notifiedTwoStopsAway) {
          final stop8 = _routeStops[7]; // Stop 8 (0-indexed)
          
          // Calculate distance in meters using Geolocator
          final distanceInMeters = Geolocator.distanceBetween(
            driverLat, driverLng, 
            stop8['lat']!, stop8['lng']!
          );

          // If the driver is within a 50-meter radius of Stop 8, trigger notification!
          if (distanceInMeters <= 50) {
            NotificationService.showNotification(
              id: 2,
              title: '📍 Almost There!',
              body: 'The KiddoCab just reached Stop 8! It is exactly 2 stops away. Please get ready.',
            );
            _notifiedTwoStopsAway = true;
          }
        }
      },
    ).subscribe();
  }"""

content = re.sub(old_method, new_method, content)

# Add Geolocator import if not present
if "import 'package:geolocator/geolocator.dart';" not in content:
    content = content.replace("import '../services/auth_service.dart';", "import '../services/auth_service.dart';\nimport 'package:geolocator/geolocator.dart';")

with open('lib/screens/parent_dashboard.dart', 'w', encoding='utf-8') as f:
    f.write(content)
