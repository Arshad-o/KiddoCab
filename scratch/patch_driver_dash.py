import re

with open('lib/screens/driver_dashboard.dart', 'r', encoding='utf-8') as f:
    code = f.read()

# Add ImagePicker import if not present
if "import 'package:image_picker/image_picker.dart';" not in code:
    code = code.replace("import 'package:supabase_flutter/supabase_flutter.dart';", "import 'package:supabase_flutter/supabase_flutter.dart';\nimport 'package:image_picker/image_picker.dart';")

# 1. Add mock pickup coordinates to the students list
old_trips = """  final Map<String, List<Map<String, dynamic>>> _tripStudents = {
    'Morning Pickup #1': [
      {'name': 'Emma Smith', 'status': 'Picked Up', 'color': Colors.green},
      {'name': 'Noah Johnson', 'status': 'Waiting', 'color': Colors.orange},
      {'name': 'Liam Williams', 'status': 'Absent', 'color': Colors.red},
    ],
    'Afternoon Drop-off #3': [
      {'name': 'Ava Davis', 'status': 'Dropped', 'color': Colors.green},
      {'name': 'Lucas Miller', 'status': 'In Transit', 'color': Colors.blue},
    ],
    'Field Trip - Museum': [
      {'name': 'Mia Wilson', 'status': 'Boarded', 'color': Colors.green},
      {'name': 'Ethan Moore', 'status': 'Boarded', 'color': Colors.green},
      {'name': 'Isabella Taylor', 'status': 'Missing', 'color': Colors.red},
    ],
  };"""

new_trips = """  final Map<String, List<Map<String, dynamic>>> _tripStudents = {
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
code = code.replace(old_trips, new_trips)


# 2. Add FRS logic method
frs_method = """  Future<void> _runFRSScan(String studentName, double targetLat, double targetLng) async {
    if (_currentPosition == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Waiting for GPS signal...'), backgroundColor: Colors.orange),
      );
      return;
    }

    final distanceInMeters = Geolocator.distanceBetween(
      _currentPosition!.latitude, 
      _currentPosition!.longitude, 
      targetLat, 
      targetLng
    );

    // Geo-Fence Security Check (e.g., 50 meters)
    if (distanceInMeters > 50) {
      showDialog(
        context: context,
        builder: (ctx) => AlertDialog(
          title: const Row(children: [Icon(Icons.warning, color: Colors.red), SizedBox(width: 8), Text('Security Alert')]),
          content: Text('You are ${distanceInMeters.toStringAsFixed(0)} meters away from the designated pickup location. FRS scanning is mathematically locked until you are within 50 meters.'),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx), 
              child: const Text('Understood')
            )
          ],
        )
      );
      return;
    }

    // Within Geo-Fence: Run Camera
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: ImageSource.camera, preferredCameraDevice: CameraDevice.front);
    if (pickedFile != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('FRS Match Successful! $studentName boarded.'), backgroundColor: Colors.green),
      );
      
      // Update UI (mock status change)
      setState(() {
        for (var trip in _tripStudents.values) {
          for (var s in trip) {
            if (s['name'] == studentName) {
              s['status'] = 'Boarded';
              s['color'] = Colors.green;
            }
          }
        }
      });
    }
  }

  Widget _buildStudentTile"""
code = code.replace("  Widget _buildStudentTile", frs_method)


# 3. Update the list builder to pass Lat/Lng
old_builder = """          ...(_tripStudents[_selectedTrip] ?? []).map((student) {
            return _buildStudentTile(student['name'], student['status'], student['color']);
          }).toList(),"""
new_builder = """          ...(_tripStudents[_selectedTrip] ?? []).map((student) {
            return _buildStudentTile(student['name'], student['status'], student['color'], student['lat'], student['lng']);
          }).toList(),"""
code = code.replace(old_builder, new_builder)


# 4. Update the _buildStudentTile signature and UI
old_tile = """  Widget _buildStudentTile(String name, String status, Color statusColor) {
    return Container("""
new_tile = """  Widget _buildStudentTile(String name, String status, Color statusColor, double lat, double lng) {
    return Container("""
code = code.replace(old_tile, new_tile)

old_tile_ui = """        trailing: Chip(
          label: Text(status),
          backgroundColor: statusColor.withOpacity(0.15),
          labelStyle: TextStyle(color: statusColor, fontWeight: FontWeight.bold),
          side: BorderSide.none,
        ),
      ),"""
new_tile_ui = """        trailing: status == 'Waiting'
            ? ElevatedButton.icon(
                onPressed: () => _runFRSScan(name, lat, lng),
                icon: const Icon(Icons.face_retouching_natural, size: 18),
                label: const Text('Scan'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blueAccent,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                  visualDensity: VisualDensity.compact,
                ),
              )
            : Chip(
                label: Text(status),
                backgroundColor: statusColor.withOpacity(0.15),
                labelStyle: TextStyle(color: statusColor, fontWeight: FontWeight.bold),
                side: BorderSide.none,
              ),
      ),"""
code = code.replace(old_tile_ui, new_tile_ui)

with open('lib/screens/driver_dashboard.dart', 'w', encoding='utf-8') as f:
    f.write(code)
