import 'dart:async';
import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:geolocator/geolocator.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'driver/driver_login_screen.dart';

class DriverDashboard extends StatefulWidget {
  const DriverDashboard({super.key});

  @override
  State<DriverDashboard> createState() => _DriverDashboardState();
}

class _DriverDashboardState extends State<DriverDashboard> {
  final _supabase = Supabase.instance.client;
  
  bool _isBroadcasting = false;
  StreamSubscription<Position>? _positionStream;
  
  GoogleMapController? _mapController;
  LatLng? _currentPosition;
  
  // Profile Settings
  String _selectedLanguage = 'English';
  final List<String> _languages = [
    'English', 'Telugu (తెలుగు)', 'Hindi (हिन्दी)', 'Tamil (தமிழ்)', 
    'Kannada (ಕನ್ನಡ)', 'Malayalam (മലയാളം)', 'Punjabi (ਪੰਜਾਬੀ)', 
    'Gujarati (ગુજરાતી)', 'Rajasthani (राजस्थानी)'
  ];
  MapType _selectedMapType = MapType.normal;

  String _selectedTrip = 'Morning Pickup #1';
  final List<String> _trips = [
    'Morning Pickup #1',
    'Afternoon Drop-off #3',
    'Field Trip - Museum'
  ];

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

  @override
  void initState() {
    super.initState();
    _determinePosition();
  }

  Future<void> _determinePosition() async {
    bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) return;

    LocationPermission permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) return;
    }
    if (permission == LocationPermission.deniedForever) return;

    Position position = await Geolocator.getCurrentPosition(desiredAccuracy: LocationAccuracy.high);
    if (mounted) {
      setState(() {
        _currentPosition = LatLng(position.latitude, position.longitude);
      });
      if (_mapController != null) {
        _mapController!.animateCamera(
          CameraUpdate.newLatLngZoom(_currentPosition!, 16.0),
        );
      }
    }
  }

  Future<void> _toggleBroadcast() async {
    if (_isBroadcasting) {
      await _positionStream?.cancel();
      setState(() => _isBroadcasting = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Location broadcast stopped.')),
        );
      }
    } else {
      setState(() => _isBroadcasting = true);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Broadcasting live location...')),
        );
      }
      _positionStream = Geolocator.getPositionStream(
        locationSettings: const LocationSettings(
          accuracy: LocationAccuracy.high,
          distanceFilter: 10,
        ),
      ).listen((Position position) async {
        setState(() {
          _currentPosition = LatLng(position.latitude, position.longitude);
        });
        if (_mapController != null) {
          _mapController!.animateCamera(
            CameraUpdate.newLatLngZoom(_currentPosition!, 16.0),
          );
        }
        
        final user = _supabase.auth.currentUser;
        if (user != null) {
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

  Widget _buildStudentTile(String name, String status, Color statusColor) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.grey.withOpacity(0.2)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          )
        ]
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

  // --- TAB 1: Manifest ---
  Widget _buildManifest(ThemeData theme) {
    return Container(
      color: theme.colorScheme.background,
      child: ListView(
        padding: const EdgeInsets.all(16.0),
        children: [
          // Trip Selector
          Card(
            elevation: 2,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
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
                              setState(() => _selectedTrip = newValue);
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
          const SizedBox(height: 24),
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
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                elevation: 2,
              ),
            ),
          ),
          const SizedBox(height: 32),
          Text(
            'Student Manifest',
            style: theme.textTheme.titleLarge?.copyWith(
              fontWeight: FontWeight.bold,
              color: theme.colorScheme.primary,
            ),
          ),
          const SizedBox(height: 16),
          ...(_tripStudents[_selectedTrip] ?? []).map((student) {
            return _buildStudentTile(student['name'], student['status'], student['color']);
          }).toList(),
        ],
      ),
    );
  }

  // --- TAB 2: Live Map ---
  Widget _buildLiveMap(ThemeData theme) {
    return GoogleMap(
      mapType: _selectedMapType,
      initialCameraPosition: _currentPosition != null 
          ? CameraPosition(target: _currentPosition!, zoom: 16.0)
          : const CameraPosition(
              target: LatLng(28.6139, 77.2090),
              zoom: 14.0,
            ),
      myLocationEnabled: true,
      myLocationButtonEnabled: true,
      zoomControlsEnabled: false,
      onMapCreated: (GoogleMapController controller) {
        _mapController = controller;
        if (_currentPosition != null) {
          _mapController!.animateCamera(
            CameraUpdate.newLatLngZoom(_currentPosition!, 16.0),
          );
        }
      },
    );
  }

  // --- TAB 3: Profile ---
  Widget _buildProfile(ThemeData theme) {
    final user = _supabase.auth.currentUser;
    return Container(
      color: theme.colorScheme.background,
      child: ListView(
        padding: const EdgeInsets.all(24.0),
        children: [
          Center(
            child: CircleAvatar(
              radius: 60,
              backgroundColor: theme.colorScheme.primary.withOpacity(0.1),
              child: Icon(Icons.drive_eta, size: 60, color: theme.colorScheme.primary),
            ),
          ),
          const SizedBox(height: 24),
          Card(
            elevation: 2,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                children: [
                  ListTile(
                    leading: const Icon(Icons.email),
                    title: const Text('Email'),
                    subtitle: Text(user?.email ?? 'Not available'),
                  ),
                  const Divider(),
                  ListTile(
                    leading: const Icon(Icons.phone),
                    title: const Text('Phone'),
                    subtitle: Text(user?.phone ?? 'Not available'),
                  ),
                  const Divider(),
                  ListTile(
                    leading: const Icon(Icons.language, color: Colors.blue),
                    title: const Text('App Language'),
                    trailing: DropdownButton<String>(
                      value: _selectedLanguage,
                      underline: const SizedBox(),
                      icon: const Icon(Icons.arrow_drop_down),
                      items: _languages.map((String lang) {
                        return DropdownMenuItem<String>(
                          value: lang,
                          child: Text(lang, style: const TextStyle(fontSize: 14)),
                        );
                      }).toList(),
                      onChanged: (String? newValue) {
                        if (newValue != null) {
                          setState(() => _selectedLanguage = newValue);
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(content: Text('Language updated to $newValue')),
                          );
                        }
                      },
                    ),
                  ),
                  const Divider(),
                  ListTile(
                    leading: const Icon(Icons.layers, color: Colors.green),
                    title: const Text('Map View Type'),
                    trailing: DropdownButton<MapType>(
                      value: _selectedMapType,
                      underline: const SizedBox(),
                      icon: const Icon(Icons.arrow_drop_down),
                      items: const [
                        DropdownMenuItem(value: MapType.normal, child: Text('Default (Ola/Uber)', style: TextStyle(fontSize: 14))),
                        DropdownMenuItem(value: MapType.satellite, child: Text('Satellite View', style: TextStyle(fontSize: 14))),
                        DropdownMenuItem(value: MapType.terrain, child: Text('Terrain View', style: TextStyle(fontSize: 14))),
                        DropdownMenuItem(value: MapType.hybrid, child: Text('Hybrid View', style: TextStyle(fontSize: 14))),
                      ],
                      onChanged: (MapType? newValue) {
                        if (newValue != null) {
                          setState(() => _selectedMapType = newValue);
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Map View updated! Check the Live Map tab.')),
                          );
                        }
                      },
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 32),
          ElevatedButton.icon(
            onPressed: () async {
              await _supabase.auth.signOut();
              if (mounted) {
                Navigator.pushAndRemoveUntil(
                  context,
                  MaterialPageRoute(builder: (_) => const DriverLoginScreen()),
                  (route) => false,
                );
              }
            },
            icon: const Icon(Icons.logout),
            label: const Text('Log Out'),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.redAccent,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return DefaultTabController(
      length: 3,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Driver Dashboard', style: TextStyle(fontWeight: FontWeight.bold)),
          backgroundColor: theme.colorScheme.primary,
          foregroundColor: Colors.white,
          elevation: 0,
          bottom: const TabBar(
            indicatorColor: Colors.white,
            indicatorWeight: 4,
            labelColor: Colors.white,
            unselectedLabelColor: Colors.white70,
            tabs: [
              Tab(icon: Icon(Icons.assignment), text: 'Manifest'),
              Tab(icon: Icon(Icons.map), text: 'Live Map'),
              Tab(icon: Icon(Icons.person), text: 'Profile'),
            ],
          ),
        ),
        body: TabBarView(
          physics: const NeverScrollableScrollPhysics(),
          children: [
            _buildManifest(theme),
            _buildLiveMap(theme),
            _buildProfile(theme),
          ],
        ),
      ),
    );
  }
}
