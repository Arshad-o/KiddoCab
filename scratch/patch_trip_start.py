import re

with open('lib/screens/driver_dashboard.dart', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add Timer import and state vars
if "import 'dart:async';" not in code:
    code = "import 'dart:async';\n" + code

if "import '../services/notification_service.dart';" not in code:
    code = code.replace("import 'package:supabase_flutter/supabase_flutter.dart';", "import 'package:supabase_flutter/supabase_flutter.dart';\nimport '../services/notification_service.dart';")

state_vars = """  MapType _selectedMapType = MapType.normal;

  String _selectedTrip = 'Morning Pickup #1';
  final Map<String, String> _tripTimes = {
    'Morning Pickup #1': '06:00', // 24-hour format
    'Afternoon Drop-off #3': '15:30',
    'Field Trip - Museum': '09:00',
  };
  
  Timer? _scheduleTimer;
  bool _tripReminderShown = false;
"""
code = code.replace("  MapType _selectedMapType = MapType.normal;\n\n  String _selectedTrip = 'Morning Pickup #1';", state_vars)

# 2. Add Timer setup in initState
init_old = """  @override
  void initState() {
    super.initState();
    _determinePosition();
  }"""
init_new = """  @override
  void initState() {
    super.initState();
    _determinePosition();
    
    // Check every 10 seconds if it's time to alert the driver
    _scheduleTimer = Timer.periodic(const Duration(seconds: 10), (timer) {
      _checkTripSchedule();
    });
  }
  
  void _checkTripSchedule() {
    if (_tripReminderShown || _isBroadcasting) return;
    
    final now = DateTime.now();
    final tripTimeStr = _tripTimes[_selectedTrip] ?? '06:00';
    final parts = tripTimeStr.split(':');
    final tripHour = int.parse(parts[0]);
    final tripMinute = int.parse(parts[1]);
    
    // Create a DateTime for the trip time today
    final tripTime = DateTime(now.year, now.month, now.day, tripHour, tripMinute);
    
    // If we are within 15 minutes of the trip, or past it, sound the alarm!
    if (now.isAfter(tripTime.subtract(const Duration(minutes: 15)))) {
      _tripReminderShown = true;
      
      // Send Mobile Push Notification to Driver
      NotificationService.showNotification(
        id: 55,
        title: '⏰ TRIP REMINDER ALARM',
        body: 'It is almost time for $_selectedTrip! Get ready and Start the Trip.',
      );
      
      // Show in-app alarm
      if (mounted) {
        showDialog(
          context: context,
          barrierDismissible: false,
          builder: (ctx) => AlertDialog(
            title: const Row(children: [Icon(Icons.access_alarms, color: Colors.orange), SizedBox(width: 8), Text('Time to Drive!')]),
            content: Text('Your scheduled trip ($_selectedTrip) starts at $tripTimeStr. Are you ready to begin?'),
            actions: [
              TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Not Yet')),
              ElevatedButton.icon(
                onPressed: () {
                  Navigator.pop(ctx);
                  _toggleBroadcast(); // Start Trip!
                },
                icon: const Icon(Icons.play_arrow),
                label: const Text('START TRIP NOW'),
                style: ElevatedButton.styleFrom(backgroundColor: Colors.green, foregroundColor: Colors.white),
              )
            ],
          )
        );
      }
    }
  }"""
code = code.replace(init_old, init_new)

# 3. Cancel Timer in dispose
disp_old = """  @override
  void dispose() {
    _positionStream?.cancel();
    super.dispose();
  }"""
disp_new = """  @override
  void dispose() {
    _positionStream?.cancel();
    _scheduleTimer?.cancel();
    super.dispose();
  }"""
code = code.replace(disp_old, disp_new)

# 4. Modify the Button in Manifest Tab
btn_old = """          // Action Button
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: _toggleBroadcast,
              icon: Icon(_isBroadcasting ? Icons.stop_circle : Icons.location_on),
              label: Text(
                _isBroadcasting ? 'Stop Broadcasting' : 'Broadcast Location',
                style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: _isBroadcasting ? Colors.red : theme.colorScheme.secondary,
                foregroundColor: Colors.white,"""
btn_new = """          // Action Button
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: _toggleBroadcast,
              icon: Icon(_isBroadcasting ? Icons.stop_circle : Icons.play_arrow),
              label: Text(
                _isBroadcasting ? 'END TRIP' : '▶ START TRIP',
                style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, letterSpacing: 1.2),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: _isBroadcasting ? Colors.red : Colors.green,
                foregroundColor: Colors.white,"""
code = code.replace(btn_old, btn_new)


# 5. Modify _toggleBroadcast to also send an alert table record for parents
toggle_old = """    } else {
      setState(() => _isBroadcasting = true);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Broadcasting live location...')),
        );
      }"""
toggle_new = """    } else {
      setState(() => _isBroadcasting = true);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Trip Started! Parents notified.'), backgroundColor: Colors.green),
        );
      }
      
      // Broadcast to ALL parents that the trip started via the alerts table
      try {
        _supabase.from('alerts').insert({
          'child_name': 'ALL', // Global alert identifier
          'message': '🚀 TRIP STARTED: Your driver has started the $_selectedTrip route!',
        });
      } catch (e) {
        print('Trip start alert error: $e');
      }
"""
code = code.replace(toggle_old, toggle_new)

with open('lib/screens/driver_dashboard.dart', 'w', encoding='utf-8') as f:
    f.write(code)
