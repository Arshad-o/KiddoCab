import 'dart:async';
import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:geolocator/geolocator.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class DriverDashboard extends StatefulWidget {
  const DriverDashboard({super.key});

  @override
  State<DriverDashboard> createState() => _DriverDashboardState();
}

class _DriverDashboardState extends State<DriverDashboard> {
  bool _isBroadcasting = false;
  StreamSubscription<Position>? _positionStream;
  final _supabase = Supabase.instance.client;

  Future<void> _toggleBroadcast() async {
    if (_isBroadcasting) {
      // Stop broadcasting
      await _positionStream?.cancel();
      setState(() => _isBroadcasting = false);
      
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Location broadcast stopped.')),
      );
      return;
    }

    // Start broadcasting
    bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Location services are disabled.')));
      return;
    }

    LocationPermission permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Location permissions are denied.')));
        return;
      }
    }

    if (permission == LocationPermission.deniedForever) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Location permissions are permanently denied.')));
      return;
    }

    setState(() => _isBroadcasting = true);
    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Live tracking started!')));

    const locationSettings = LocationSettings(
      accuracy: LocationAccuracy.high,
      distanceFilter: 10, // update every 10 meters
    );

    _positionStream = Geolocator.getPositionStream(locationSettings: locationSettings).listen((Position position) async {
      try {
        await _supabase.from('locations').insert({
          'driver_email': 'current_driver@test.com', // In a real app, use the actual logged-in user
          'latitude': position.latitude,
          'longitude': position.longitude,
          'updated_at': DateTime.now().toUtc().toIso8601String(),
        });
        print('Location sent to Supabase: \${position.latitude}, \${position.longitude}');
      } catch (e) {
        print('Error sending location: \$e');
      }
    });
  }

  @override
  void dispose() {
    _positionStream?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      backgroundColor: theme.colorScheme.background,
      appBar: AppBar(
        title: const Text('Driver Dashboard'),
        backgroundColor: theme.colorScheme.primary,
        foregroundColor: Colors.white,
      ),
      body: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(20),
            color: theme.colorScheme.primary.withOpacity(0.1),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Route 4: Afternoon Drop-off',
                      style: theme.textTheme.titleLarge?.copyWith(
                        color: theme.colorScheme.primary,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    const Text('Next Stop: Oakwood Elementary (2.1 mi)'),
                  ],
                ),
                Icon(Icons.route, color: theme.colorScheme.primary, size: 32),
              ],
            ),
          ),
          SizedBox(
            height: 200,
            child: const GoogleMap(
              initialCameraPosition: CameraPosition(
                target: LatLng(28.6139, 77.2090),
                zoom: 14.0,
              ),
              myLocationEnabled: true,
              zoomControlsEnabled: false,
            ),
          ),
          Expanded(
            child: ListView(
              padding: const EdgeInsets.all(16),
              children: [
                Text(
                  'Student Manifest',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: Colors.grey[800],
                  ),
                ),
                const SizedBox(height: 12),
                _buildStudentTile(context, 'Emma Smith', 'Picked Up', theme.colorScheme.tertiary),
                _buildStudentTile(context, 'Noah Johnson', 'Waiting', theme.colorScheme.secondary),
                _buildStudentTile(context, 'Liam Williams', 'Absent', Colors.red),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: _toggleBroadcast,
                icon: Icon(_isBroadcasting ? Icons.stop_circle : Icons.location_on),
                label: Text(
                  _isBroadcasting ? 'Stop Broadcasting' : 'Broadcast Location',
                  style: const TextStyle(fontSize: 18),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: _isBroadcasting ? Colors.red : theme.colorScheme.secondary,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStudentTile(BuildContext context, String name, String status, Color statusColor) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: Colors.grey[200],
          child: const Icon(Icons.person, color: Colors.grey),
        ),
        title: Text(name, style: const TextStyle(fontWeight: FontWeight.w600)),
        trailing: Chip(
          label: Text(status),
          backgroundColor: statusColor.withOpacity(0.1),
          labelStyle: TextStyle(color: statusColor, fontWeight: FontWeight.bold),
          side: BorderSide.none,
        ),
      ),
    );
  }
}
