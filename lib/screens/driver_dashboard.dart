import 'dart:async';
import 'dart:ui';
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

  String _selectedTrip = 'Morning Pickup #1';
  final List<String> _trips = [
    'Morning Pickup #1',
    'Afternoon Drop-off #3',
    'Field Trip - Museum'
  ];

  // Dummy data mapping trips to students
  final Map<String, List<Map<String, dynamic>>> _tripStudents = {
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
  };

  Future<void> _toggleBroadcast() async {
    if (_isBroadcasting) {
      await _positionStream?.cancel();
      setState(() => _isBroadcasting = false);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Location broadcast stopped.')),
      );
      return;
    }

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
      distanceFilter: 10,
    );

    _positionStream = Geolocator.getPositionStream(locationSettings: locationSettings).listen((Position position) async {
      try {
        await _supabase.from('locations').insert({
          'driver_email': 'current_driver@test.com',
          'latitude': position.latitude,
          'longitude': position.longitude,
          'updated_at': DateTime.now().toUtc().toIso8601String(),
        });
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

  Widget _buildGlassContainer({required Widget child, double opacity = 0.75, double radius = 24}) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(radius),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
        child: Container(
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(opacity),
            borderRadius: BorderRadius.circular(radius),
            border: Border.all(color: Colors.white.withOpacity(0.2)),
          ),
          child: child,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Scaffold(
      extendBodyBehindAppBar: true,
      body: Stack(
        children: [
          // Background Map (Full Screen)
          const GoogleMap(
            initialCameraPosition: CameraPosition(
              target: LatLng(28.6139, 77.2090),
              zoom: 14.0,
            ),
            myLocationEnabled: true,
            zoomControlsEnabled: false,
          ),
          
          // Floating Top Profile & Trip Selector (Glassmorphism)
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
              child: _buildGlassContainer(
                opacity: 0.85,
                radius: 20,
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Row(
                    children: [
                      CircleAvatar(
                        radius: 24,
                        backgroundImage: const AssetImage('assets/images/driverimg.webp'),
                        backgroundColor: theme.colorScheme.primary.withOpacity(0.1),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Text('Welcome, Driver', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                            const SizedBox(height: 4),
                            DropdownButton<String>(
                              value: _selectedTrip,
                              isDense: true,
                              isExpanded: true,
                              underline: const SizedBox(),
                              icon: const Icon(Icons.keyboard_arrow_down),
                              items: _trips.map((String value) {
                                return DropdownMenuItem<String>(
                                  value: value,
                                  child: Text(value, style: TextStyle(color: theme.colorScheme.primary, fontWeight: FontWeight.w600)),
                                );
                              }).toList(),
                              onChanged: (newValue) {
                                if (newValue != null) {
                                  setState(() {
                                    _selectedTrip = newValue;
                                  });
                                }
                              },
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
          
          // Floating Bottom Panel (Glassmorphism Draggable Sheet)
          DraggableScrollableSheet(
            initialChildSize: 0.4,
            minChildSize: 0.2,
            maxChildSize: 0.8,
            builder: (BuildContext context, ScrollController scrollController) {
              return _buildGlassContainer(
                opacity: 0.90,
                radius: 32,
                child: Padding(
                  padding: const EdgeInsets.all(20.0),
                  child: Column(
                    children: [
                      // Drag Handle
                      Container(
                        width: 40,
                        height: 5,
                        decoration: BoxDecoration(
                          color: Colors.grey[400],
                          borderRadius: BorderRadius.circular(10),
                        ),
                      ),
                      const SizedBox(height: 16),
                      // Action Button
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
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 16),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(16),
                            ),
                            elevation: 0,
                          ),
                        ),
                      ),
                      const SizedBox(height: 24),
                      Align(
                        alignment: Alignment.centerLeft,
                        child: Text(
                          'Student Manifest',
                          style: theme.textTheme.titleLarge?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: theme.colorScheme.primary,
                          ),
                        ),
                      ),
                      const SizedBox(height: 12),
                      // Scrollable Student List
                      Expanded(
                        child: ListView.builder(
                          controller: scrollController,
                          itemCount: _tripStudents[_selectedTrip]?.length ?? 0,
                          itemBuilder: (context, index) {
                            final student = _tripStudents[_selectedTrip]![index];
                            return _buildStudentTile(
                              student['name'],
                              student['status'],
                              student['color'],
                            );
                          },
                        ),
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildStudentTile(String name, String status, Color statusColor) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.5),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white),
      ),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: Colors.grey[200],
          child: const Icon(Icons.person, color: Colors.grey),
        ),
        title: Text(name, style: const TextStyle(fontWeight: FontWeight.bold)),
        trailing: Chip(
          label: Text(status),
          backgroundColor: statusColor.withOpacity(0.15),
          labelStyle: TextStyle(color: statusColor, fontWeight: FontWeight.bold),
          side: BorderSide.none,
        ),
      ),
    );
  }
}
