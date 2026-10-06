import 'dart:async';
import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:geolocator/geolocator.dart';
import 'package:supabase_flutter/supabase_flutter.dart' hide MapType;
import '../services/notification_service.dart';
import 'package:image_picker/image_picker.dart';
import 'driver/live_frs_scanner_screen.dart';
import 'driver/driver_login_screen.dart';
import 'chat_screen.dart';

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
  final Map<String, String> _tripTimes = {
    'Morning Pickup #1': '06:00', // 24-hour format
    'Afternoon Drop-off #3': '15:30',
    'Field Trip - Museum': '09:00',
  };
  
  Timer? _scheduleTimer;
  bool _tripReminderShown = false;

  final List<String> _trips = [
    'Morning Pickup #1',
    'Afternoon Drop-off #3',
    'Field Trip - Museum'
  ];

  final Map<String, List<Map<String, dynamic>>> _tripStudents = {
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


  @override
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
  }

  Future<void> _determinePosition() async {
    bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please enable GPS Location Services!'), backgroundColor: Colors.red));
      return;
    }

    LocationPermission permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) {
        if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Location permissions denied!'), backgroundColor: Colors.red));
        return;
      }
    }
    if (permission == LocationPermission.deniedForever) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Location permissions are permanently denied, please enable in settings.'), backgroundColor: Colors.red));
      return;
    }

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

        // Calculate live ETA (assuming city speed 25 km/h = ~416 meters / min)
        int etaMins = (dist / 416).ceil();
        String distStr = dist > 1000 ? '${(dist/1000).toStringAsFixed(1)} km' : '${dist.toStringAsFixed(0)} m';
        student['live_eta'] = 'ETA: $etaMins min ($distStr)';

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

  void _triggerAntiSkipAlarm(List<String> missing) async {
    // Attempt system beep
    print('\x07');
    
    // 1. Send Alert to Parents via Supabase
    for (String child in missing) {
      try {
        await _supabase.from('alerts').insert({
          'child_name': child,
          'message': 'CRITICAL: Driver left location without FRS scanning!',
        });
      } catch (e) {
        print('Error sending alert: $e');
      }
    }
    
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


  @override
  void dispose() {
    _positionStream?.cancel();
    _scheduleTimer?.cancel();
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

  Future<void> _runFRSScan(String studentName, double targetLat, double targetLng) async {
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

    // Within Geo-Fence: Run Live ML Kit FRS Scanner
    final verified = await Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => LiveFrsScannerScreen(studentName: studentName)),
    );

    if (verified == true) {
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

  Widget _buildStudentTile(String name, String status, Color statusColor, double lat, double lng, String phone, String? etaText) {
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
        subtitle: Column(
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
        ),
        trailing: status == 'Waiting'
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
              icon: Icon(_isBroadcasting ? Icons.stop_circle : Icons.play_arrow),
              label: Text(
                _isBroadcasting ? 'END TRIP' : '▶ START TRIP',
                style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, letterSpacing: 1.2),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: _isBroadcasting ? Colors.red : Colors.green,
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
            return _buildStudentTile(
              student['name'], 
              student['status'], 
              student['color'], 
              student['lat'], 
              student['lng'], 
              student['phone'] ?? 'N/A',
              student['live_eta']
            );
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
              final bool? confirmLogout = await showDialog<bool>(
                context: context,
                builder: (BuildContext context) {
                  return AlertDialog(
                    title: const Text('Confirm Logout'),
                    content: const Text('Do you really want to log out of KiddoCab?'),
                    actions: [
                      TextButton(
                        onPressed: () => Navigator.of(context).pop(false),
                        child: const Text('Cancel'),
                      ),
                      TextButton(
                        onPressed: () => Navigator.of(context).pop(true),
                        style: TextButton.styleFrom(foregroundColor: Colors.red),
                        child: const Text('Log Out'),
                      ),
                    ],
                  );
                },
              );

              if (confirmLogout == true) {
                await _supabase.auth.signOut();
                if (mounted) {
                  Navigator.pushAndRemoveUntil(
                    context,
                    MaterialPageRoute(builder: (_) => const DriverLoginScreen()),
                    (route) => false,
                  );
                }
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
        floatingActionButton: FloatingActionButton(
          onPressed: () {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => const ChatScreen(
                  otherUserId: 'parent-placeholder-id', // MVP mapping
                  otherUserName: 'Parent (Noah)',
                )
              ),
            );
          },
          backgroundColor: theme.colorScheme.secondary,
          child: const Icon(Icons.chat, color: Colors.white),
        ),
      ),
    );
  }
}
