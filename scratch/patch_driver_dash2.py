import re

with open('lib/screens/driver_dashboard.dart', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update Trip Students to include phone numbers
old_trips = """  final Map<String, List<Map<String, dynamic>>> _tripStudents = {
    'Morning Pickup #1': [
      {'name': 'Emma Smith', 'status': 'Picked Up', 'color': Colors.green, 'lat': 28.6139, 'lng': 77.2090},
      {'name': 'Noah Johnson', 'status': 'Waiting', 'color': Colors.orange, 'lat': 28.6140, 'lng': 77.2091},
      {'name': 'Liam Williams', 'status': 'Absent', 'color': Colors.red, 'lat': 28.6150, 'lng': 77.2100},
    ],
    'Afternoon Drop-off #3': [
      {'name': 'Ava Davis', 'status': 'Dropped', 'color': Colors.green, 'lat': 28.6139, 'lng': 77.2090},
      {'name': 'Lucas Miller', 'status': 'In Transit', 'color': Colors.blue, 'lat': 28.6139, 'lng': 77.2090},
    ],
    'Field Trip - Museum': [
      {'name': 'Mia Wilson', 'status': 'Boarded', 'color': Colors.green, 'lat': 28.6139, 'lng': 77.2090},
      {'name': 'Ethan Moore', 'status': 'Boarded', 'color': Colors.green, 'lat': 28.6139, 'lng': 77.2090},
      {'name': 'Isabella Taylor', 'status': 'Missing', 'color': Colors.red, 'lat': 28.6139, 'lng': 77.2090},
    ],
  };"""

new_trips = """  final Map<String, List<Map<String, dynamic>>> _tripStudents = {
    'Morning Pickup #1': [
      {'name': 'Emma Smith', 'status': 'Picked Up', 'color': Colors.green, 'lat': 28.6139, 'lng': 77.2090, 'phone': '+1 555-0101'},
      {'name': 'Noah Johnson', 'status': 'Waiting', 'color': Colors.orange, 'lat': 28.6140, 'lng': 77.2091, 'phone': '+1 555-0102'},
      {'name': 'Liam Williams', 'status': 'Absent', 'color': Colors.red, 'lat': 28.6150, 'lng': 77.2100, 'phone': '+1 555-0103'},
    ],
    'Afternoon Drop-off #3': [
      {'name': 'Ava Davis', 'status': 'Dropped', 'color': Colors.green, 'lat': 28.6139, 'lng': 77.2090, 'phone': '+1 555-0104'},
      {'name': 'Lucas Miller', 'status': 'In Transit', 'color': Colors.blue, 'lat': 28.6139, 'lng': 77.2090, 'phone': '+1 555-0105'},
    ],
    'Field Trip - Museum': [
      {'name': 'Mia Wilson', 'status': 'Boarded', 'color': Colors.green, 'lat': 28.6139, 'lng': 77.2090, 'phone': '+1 555-0106'},
      {'name': 'Ethan Moore', 'status': 'Boarded', 'color': Colors.green, 'lat': 28.6139, 'lng': 77.2090, 'phone': '+1 555-0107'},
      {'name': 'Isabella Taylor', 'status': 'Missing', 'color': Colors.red, 'lat': 28.6139, 'lng': 77.2090, 'phone': '+1 555-0108'},
    ],
  };
  
  // Track auto-popups to prevent spam
  Set<String> _promptedChildren = {};
  bool _isAlarmTriggered = false;
"""
code = code.replace(old_trips, new_trips)


# 2. Add Anti-Skip Alarm and Auto-Popup logic inside _positionStream
old_listen = """        if (user != null) {
          try {
            await _supabase.from('locations').insert({
              'driver_id': user.id,
              'latitude': position.latitude,
              'longitude': position.longitude,
            });
          } catch (e) {
            print('Error broadcasting location: $e');
          }
        }
      });
    }
  }"""

new_listen = """        if (user != null) {
          try {
            await _supabase.from('locations').insert({
              'driver_id': user.id,
              'latitude': position.latitude,
              'longitude': position.longitude,
            });
          } catch (e) {
            print('Error broadcasting location: $e');
          }
        }
        _checkGeoFencesAndAlarms(position);
      });
    }
  }

  void _checkGeoFencesAndAlarms(Position position) {
    if (_isAlarmTriggered) return;

    List<Map<String, dynamic>> currentTrip = _tripStudents[_selectedTrip] ?? [];
    List<String> skippedChildren = [];

    for (var student in currentTrip) {
      if (student['status'] == 'Waiting' || student['status'] == 'In Transit') {
        double dist = Geolocator.distanceBetween(
          position.latitude, position.longitude, 
          student['lat'], student['lng']
        );

        // 1. Auto-Popup Logic (Driver enters 50m radius)
        if (dist <= 50 && !_promptedChildren.contains(student['name'])) {
          _promptedChildren.add(student['name']);
          _showFrsAutoPopup(student);
        }
        
        // 2. Anti-Skip Alarm Logic (Driver leaves 200m radius AFTER being near)
        if (dist > 200 && _promptedChildren.contains(student['name'])) {
          skippedChildren.add(student['name']);
        }
      }
    }

    if (skippedChildren.isNotEmpty) {
      _isAlarmTriggered = true;
      _triggerAntiSkipAlarm(skippedChildren);
    }
  }

  void _showFrsAutoPopup(Map<String, dynamic> student) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => AlertDialog(
        title: const Text('📍 Location Reached', style: TextStyle(color: Colors.blue)),
        content: Text('You have arrived at the location for ${student['name']}. Please run the FRS scan immediately.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          ElevatedButton.icon(
            onPressed: () {
              Navigator.pop(ctx);
              _runFRSScan(student['name'], student['lat'], student['lng']);
            },
            icon: const Icon(Icons.face),
            label: const Text('Run FRS Scan'),
          )
        ],
      )
    );
  }

  void _triggerAntiSkipAlarm(List<String> missing) {
    // Attempt system beep
    print('\\x07');
    
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => AlertDialog(
        backgroundColor: Colors.red[900],
        title: const Row(children: [Icon(Icons.warning_amber, color: Colors.white, size: 32), SizedBox(width: 8), Text('CRITICAL ALERT', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold))]),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('ALARM TRIGGERED: VEHICLE MOVED WITHOUT FRS SCAN!', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),
            const Text('You have left the Geo-fence for:', style: TextStyle(color: Colors.white70)),
            ...missing.map((name) => Text(name, style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold))),
          ],
        ),
        actions: [
          ElevatedButton(
            onPressed: () {
              setState(() => _isAlarmTriggered = false);
              Navigator.pop(ctx);
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.white, foregroundColor: Colors.red[900]),
            child: const Text('Acknowledge & Fix'),
          )
        ],
      )
    );
  }
"""
code = code.replace(old_listen, new_listen)


# 3. Update the _buildStudentTile signature and UI to include parentPhone
old_builder = """          ...(_tripStudents[_selectedTrip] ?? []).map((student) {
            return _buildStudentTile(student['name'], student['status'], student['color'], student['lat'], student['lng']);
          }).toList(),"""
new_builder = """          ...(_tripStudents[_selectedTrip] ?? []).map((student) {
            return _buildStudentTile(student['name'], student['status'], student['color'], student['lat'], student['lng'], student['phone'] ?? 'N/A');
          }).toList(),"""
code = code.replace(old_builder, new_builder)


old_tile = """  Widget _buildStudentTile(String name, String status, Color statusColor, double lat, double lng) {
    return Container("""
new_tile = """  Widget _buildStudentTile(String name, String status, Color statusColor, double lat, double lng, String phone) {
    return Container("""
code = code.replace(old_tile, new_tile)


old_tile_ui = """        title: Text(name, style: const TextStyle(fontWeight: FontWeight.bold)),
        trailing: status == 'Waiting'"""
new_tile_ui = """        title: Text(name, style: const TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Row(
          children: [
            const Icon(Icons.phone, size: 14, color: Colors.grey),
            const SizedBox(width: 4),
            Text(phone, style: const TextStyle(color: Colors.grey, fontSize: 13)),
          ],
        ),
        trailing: status == 'Waiting'"""
code = code.replace(old_tile_ui, new_tile_ui)

with open('lib/screens/driver_dashboard.dart', 'w', encoding='utf-8') as f:
    f.write(code)
