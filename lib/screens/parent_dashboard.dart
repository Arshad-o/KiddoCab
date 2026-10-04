import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:geolocator/geolocator.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../services/auth_service.dart';
import '../services/notification_service.dart';
import 'parent/cab_selection_screen.dart';
import 'parent/parent_login_screen.dart';

class ParentDashboard extends StatefulWidget {
  const ParentDashboard({super.key});
  
  @override
  State<ParentDashboard> createState() => _ParentDashboardState();
}

class _ParentDashboardState extends State<ParentDashboard> {
  final _supabase = Supabase.instance.client;
  RealtimeChannel? _locationsChannel;
  RealtimeChannel? _alertsChannel;

  GoogleMapController? _mapController;
  LatLng? _currentPosition;
  
  // NEW: Profile Settings State
  String _selectedLanguage = 'English';
  final List<String> _languages = [
    'English', 'Telugu (తెలుగు)', 'Hindi (हिन्दी)', 'Tamil (தமிழ்)', 
    'Kannada (ಕನ್ನಡ)', 'Malayalam (മലയാളം)', 'Punjabi (ਪੰਜਾਬੀ)', 
    'Gujarati (ગુજરાતી)', 'Rajasthani (राजस्थानी)'
  ];
  MapType _selectedMapType = MapType.normal;



  @override
  void initState() {
    super.initState();
    _listenToDriverStatus();
    _listenToSecurityAlerts();
    _determinePosition();
  }

  void _listenToSecurityAlerts() {
    _alertsChannel = _supabase.channel('public:alerts').onPostgresChanges(
      event: PostgresChangeEvent.insert,
      schema: 'public',
      table: 'alerts',
      callback: (payload) {
        final newRecord = payload.newRecord;
        
        // If the alert is for THIS parent's child
        if (newRecord['child_name'] == (AuthService.currentChildName ?? 'Emma Smith')) {
          // Trigger high-priority mobile push notification
          NotificationService.showNotification(
            id: 999,
            title: '🚨 SECURITY ALERT',
            body: newRecord['message'] ?? 'Driver missed the FRS scan for your child!',
          );
          
          // Also show a massive red dialog on screen if app is open
          if (mounted) {
            showDialog(
              context: context,
              barrierDismissible: false,
              builder: (ctx) => AlertDialog(
                backgroundColor: Colors.red[900],
                title: const Row(children: [Icon(Icons.warning_amber, color: Colors.white, size: 32), SizedBox(width: 8), Text('CRITICAL ALERT', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold))]),
                content: Text(
                  newRecord['message'] ?? 'The driver has left the Geo-fence without scanning your childs face via FRS! Please contact the driver immediately.',
                  style: const TextStyle(color: Colors.white, fontSize: 16),
                ),
                actions: [
                  ElevatedButton(
                    onPressed: () => Navigator.pop(ctx),
                    style: ElevatedButton.styleFrom(backgroundColor: Colors.white, foregroundColor: Colors.red[900]),
                    child: const Text('Dismiss & Call Driver'),
                  )
                ],
              )
            );
          }
        }
      },
    ).subscribe();
  }

  Future<void> _determinePosition() async {
    bool serviceEnabled;
    LocationPermission permission;

    serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) return;

    permission = await Geolocator.checkPermission();
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


  void _listenToDriverStatus() {
    _locationsChannel = _supabase.channel('public:locations').onPostgresChanges(
      event: PostgresChangeEvent.insert,
      schema: 'public',
      table: 'locations',
      callback: (payload) {
        NotificationService.showNotification(
          id: 1,
          title: '🚐 Trip Started!',
          body: 'Your KiddoCab has started broadcasting its live location.',
        );
        Future.delayed(const Duration(seconds: 15), () {
          NotificationService.showNotification(
            id: 2,
            title: '🚐 Almost There!',
            body: 'The KiddoCab is 2 stops away. Please get ready.',
          );
        });
      },
    ).subscribe();
  }

  @override
  void dispose() {
    _locationsChannel?.unsubscribe();
    _alertsChannel?.unsubscribe();
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

  // --- TAB 1: Children Profiles ---
  Widget _buildChildrenProfiles(ThemeData theme) {
    return Container(
      color: theme.colorScheme.background,
      child: ListView(
        padding: const EdgeInsets.all(16.0),
        children: [
          Text(
            'Live Child Status',
            style: theme.textTheme.titleLarge?.copyWith(
              fontWeight: FontWeight.bold,
              color: theme.colorScheme.primary,
            ),
          ),
          const SizedBox(height: 16),
          // Child Status Card
          Card(
            elevation: 4,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            child: Column(
              children: [
                ListTile(
                  leading: CircleAvatar(
                    backgroundColor: theme.colorScheme.secondary.withOpacity(0.2),
                    child: Icon(Icons.person, color: theme.colorScheme.secondary),
                  ),
                  title: Text(AuthService.currentChildName ?? 'Emma Smith', style: const TextStyle(fontWeight: FontWeight.bold)),
                  subtitle: const Text('In Transit - Heading to School'),
                  trailing: Chip(
                    label: const Text('Boarded'),
                    backgroundColor: theme.colorScheme.tertiary.withOpacity(0.2),
                    labelStyle: TextStyle(color: theme.colorScheme.tertiary, fontWeight: FontWeight.bold),
                    side: BorderSide.none,
                  ),
                ),
                const Divider(),
                // Facial Recognition / AI Sensor Banner
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: theme.colorScheme.primary.withOpacity(0.05),
                    borderRadius: const BorderRadius.only(bottomLeft: Radius.circular(16), bottomRight: Radius.circular(16)),
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.face, color: theme.colorScheme.primary, size: 32),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('AI Check-in Active', style: TextStyle(fontWeight: FontWeight.bold, color: theme.colorScheme.primary)),
                            const SizedBox(height: 4),
                            const Text('Facial recognition confirmed boarding at 07:35 AM.', style: TextStyle(fontSize: 12)),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 32),
          // Assign New Cab Button
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => const CabSelectionScreen()),
                );
              },
              icon: const Icon(Icons.search),
              label: const Text('Find & Assign Another Trip', style: TextStyle(fontSize: 16)),
              style: ElevatedButton.styleFrom(
                backgroundColor: theme.colorScheme.secondary,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                elevation: 2,
              ),
            ),
          ),
        ],
      ),
    );
  }

  // --- TAB 2: Live Map ---
  Widget _buildLiveMap(ThemeData theme) {
    return Stack(
      children: [
        // Full Screen Map
        GoogleMap(
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
        ),
        // Floating Top Banner
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
                      backgroundImage: const AssetImage('assets/images/parentimg.png'),
                      backgroundColor: theme.colorScheme.primary.withOpacity(0.1),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Text('Good Morning, Parent', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                          const SizedBox(height: 4),
                          Text(
                            'Driver Michael is 5 mins away',
                            style: TextStyle(color: theme.colorScheme.tertiary, fontWeight: FontWeight.bold),
                          ),
                        ],
                      ),
                    ),
                    IconButton(
                      icon: Icon(Icons.notifications_active, color: theme.colorScheme.secondary),
                      onPressed: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Push Notifications Enabled!')),
                        );
                      },
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }

  // --- TAB 3: Parent Profile ---
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
              child: Icon(Icons.person, size: 60, color: theme.colorScheme.primary),
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
                  MaterialPageRoute(builder: (_) => const ParentLoginScreen()),
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
          title: const Text('KiddoCab Dashboard', style: TextStyle(fontWeight: FontWeight.bold)),
          backgroundColor: theme.colorScheme.primary,
          foregroundColor: Colors.white,
          elevation: 0,
          bottom: const TabBar(
            indicatorColor: Colors.white,
            indicatorWeight: 4,
            labelColor: Colors.white,
            unselectedLabelColor: Colors.white70,
            tabs: [
              Tab(icon: Icon(Icons.child_care), text: 'Children'),
              Tab(icon: Icon(Icons.map), text: 'Live Map'),
              Tab(icon: Icon(Icons.person), text: 'Profile'),
            ],
          ),
        ),
        body: TabBarView(
          physics: const NeverScrollableScrollPhysics(), // Prevent map sliding issues
          children: [
            _buildChildrenProfiles(theme),
            _buildLiveMap(theme),
            _buildProfile(theme),
          ],
        ),
      ),
    );
  }
}
