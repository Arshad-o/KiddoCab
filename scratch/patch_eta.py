import re

with open('lib/screens/driver_dashboard.dart', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Inside _checkGeoFencesAndAlarms, calculate ETA and Distance
old_dist_logic = """        double dist = Geolocator.distanceBetween(
          position.latitude, position.longitude, 
          student['lat'], student['lng']
        );

        // 1. Auto-Popup Logic (Driver enters 50m radius)"""
new_dist_logic = """        double dist = Geolocator.distanceBetween(
          position.latitude, position.longitude, 
          student['lat'], student['lng']
        );

        // Calculate live ETA (assuming city speed 25 km/h = ~416 meters / min)
        int etaMins = (dist / 416).ceil();
        String distStr = dist > 1000 ? '${(dist/1000).toStringAsFixed(1)} km' : '${dist.toStringAsFixed(0)} m';
        student['live_eta'] = 'ETA: $etaMins min ($distStr)';

        // 1. Auto-Popup Logic (Driver enters 50m radius)"""
code = code.replace(old_dist_logic, new_dist_logic)


# 2. Modify _buildStudentTile to accept ETA string
old_tile_sig = """  Widget _buildStudentTile(String name, String status, Color statusColor, double lat, double lng, String phone) {"""
new_tile_sig = """  Widget _buildStudentTile(String name, String status, Color statusColor, double lat, double lng, String phone, String? etaText) {"""
code = code.replace(old_tile_sig, new_tile_sig)


# 3. Modify builder call
old_builder = """          ...(_tripStudents[_selectedTrip] ?? []).map((student) {
            return _buildStudentTile(student['name'], student['status'], student['color'], student['lat'], student['lng'], student['phone'] ?? 'N/A');
          }).toList(),"""
new_builder = """          ...(_tripStudents[_selectedTrip] ?? []).map((student) {
            return _buildStudentTile(
              student['name'], 
              student['status'], 
              student['color'], 
              student['lat'], 
              student['lng'], 
              student['phone'] ?? 'N/A',
              student['live_eta']
            );
          }).toList(),"""
code = code.replace(old_builder, new_builder)


# 4. Update the subtitle UI to show ETA
old_subtitle = """        subtitle: Row(
          children: [
            const Icon(Icons.phone, size: 14, color: Colors.grey),
            const SizedBox(width: 4),
            Text(phone, style: const TextStyle(color: Colors.grey, fontSize: 13)),
          ],
        ),"""
new_subtitle = """        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.phone, size: 14, color: Colors.grey),
                const SizedBox(width: 4),
                Text(phone, style: const TextStyle(color: Colors.grey, fontSize: 13)),
              ],
            ),
            if (etaText != null && status == 'Waiting') ...[
              const SizedBox(height: 4),
              Row(
                children: [
                  const Icon(Icons.navigation, size: 14, color: Colors.blueAccent),
                  const SizedBox(width: 4),
                  Text(etaText, style: const TextStyle(color: Colors.blueAccent, fontSize: 13, fontWeight: FontWeight.bold)),
                ],
              ),
            ]
          ],
        ),"""
code = code.replace(old_subtitle, new_subtitle)

with open('lib/screens/driver_dashboard.dart', 'w', encoding='utf-8') as f:
    f.write(code)
