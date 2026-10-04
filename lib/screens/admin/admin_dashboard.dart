import 'package:flutter/material.dart';
import 'dart:ui' as ui;
import 'package:flutter/services.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class AdminDashboard extends StatefulWidget {
  const AdminDashboard({super.key});

  @override
  State<AdminDashboard> createState() => _AdminDashboardState();
}

class _AdminDashboardState extends State<AdminDashboard> {
  final _supabase = Supabase.instance.client;
  
  Map<String, LatLng> _liveDrivers = {};
  List<Map<String, dynamic>> _securityAlerts = [];
  Map<String, BitmapDescriptor> _customMarkers = {};

  @override
  void initState() {
    super.initState();
    _fetchSecurityAlerts();
    _listenToFleetLocations();
  }

  Future<BitmapDescriptor> _getMarkerForVehicleType(String? type) async {
    if (_customMarkers.containsKey(type)) return _customMarkers[type]!;
    
    String assetPath = 'assets/images/tata_magic.png';
    if (type == 'Auto Rickshaw') assetPath = 'assets/images/autoimg.jpg';
    if (type == 'Large Auto') assetPath = 'assets/images/big_auto_img.jpg';
    if (type == 'Tata Magic') assetPath = 'assets/images/tata_magic.png';
    if (type == 'Cab' || type == 'Sedan') assetPath = 'assets/images/cab.avif';
    
    try {
      ByteData data = await rootBundle.load(assetPath);
      ui.Codec codec = await ui.instantiateImageCodec(data.buffer.asUint8List(), targetWidth: 100);
      ui.FrameInfo fi = await codec.getNextFrame();
      final bytes = (await fi.image.toByteData(format: ui.ImageByteFormat.png))!.buffer.asUint8List();
      final bmp = BitmapDescriptor.fromBytes(bytes);
      _customMarkers[type ?? 'unknown'] = bmp;
      return bmp;
    } catch (e) {
      return BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueAzure);
    }
  }

  void _fetchSecurityAlerts() async {
    final response = await _supabase.from('alerts').select().order('created_at', ascending: false).limit(50);
    if (mounted) {
      setState(() {
        _securityAlerts = List<Map<String, dynamic>>.from(response);
      });
    }
  }

  Map<String, String> _driverVehicleMap = {};
  Map<String, BitmapDescriptor> _driverMarkerIcons = {};

  void _listenToFleetLocations() {
    _supabase.channel('public:locations').onPostgresChanges(
      event: PostgresChangeEvent.insert,
      schema: 'public',
      table: 'locations',
      callback: (payload) async {
        final newRecord = payload.newRecord;
        final driverId = newRecord['driver_id'].toString();
        
        // Fetch vehicle type if we don't have it
        if (!_driverVehicleMap.containsKey(driverId)) {
          final res = await _supabase.from('users').select('vehicle_type').eq('id', driverId).limit(1);
          if (res.isNotEmpty && res[0]['vehicle_type'] != null) {
            _driverVehicleMap[driverId] = res[0]['vehicle_type'];
          } else {
            _driverVehicleMap[driverId] = 'unknown';
          }
          _driverMarkerIcons[driverId] = await _getMarkerForVehicleType(_driverVehicleMap[driverId]);
        }

        if (mounted) {
          setState(() {
            _liveDrivers[driverId] = LatLng(
              newRecord['latitude'],
              newRecord['longitude'],
            );
          });
        }
      },
    ).subscribe();
    
    // Also listen to live alerts
    _supabase.channel('public:alerts_admin').onPostgresChanges(
      event: PostgresChangeEvent.insert,
      schema: 'public',
      table: 'alerts',
      callback: (payload) {
        _fetchSecurityAlerts();
      }
    ).subscribe();
  }

  Widget _buildFleetMap() {
    return GoogleMap(
      initialCameraPosition: const CameraPosition(
        target: LatLng(28.6139, 77.2090),
        zoom: 12.0,
      ),
      markers: _liveDrivers.entries.map((entry) {
        return Marker(
          markerId: MarkerId(entry.key),
          position: entry.value,
          infoWindow: InfoWindow(title: 'KiddoCab Driver', snippet: _driverVehicleMap[entry.key] ?? 'Tracking'),
          icon: _driverMarkerIcons[entry.key] ?? BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueBlue),
        );
      }).toSet(),
    );
  }

  Widget _buildSecurityLogs() {
    return _securityAlerts.isEmpty
        ? const Center(child: Text('No security alerts detected. System secure.', style: TextStyle(color: Colors.green, fontWeight: FontWeight.bold)))
        : ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: _securityAlerts.length,
            itemBuilder: (context, index) {
              final alert = _securityAlerts[index];
              return Card(
                color: Colors.red[50],
                child: ListTile(
                  leading: const Icon(Icons.warning, color: Colors.red),
                  title: Text(alert['message'], style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.red)),
                  subtitle: Text('Child: ${alert['child_name']} | Time: ${DateTime.parse(alert['created_at']).toLocal().toString().split('.')[0]}'),
                ),
              );
            },
          );
  }

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 2,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Admin Command Center', style: TextStyle(fontWeight: FontWeight.bold)),
          backgroundColor: Colors.black87,
          foregroundColor: Colors.white,
          actions: [
            IconButton(
              icon: const Icon(Icons.logout),
              onPressed: () => Navigator.pop(context), // Simple pop for MVP
            )
          ],
          bottom: const TabBar(
            indicatorColor: Colors.amber,
            labelColor: Colors.amber,
            unselectedLabelColor: Colors.white70,
            tabs: [
              Tab(icon: Icon(Icons.map), text: 'Live Fleet Map'),
              Tab(icon: Icon(Icons.security), text: 'Security Logs'),
            ],
          ),
        ),
        body: TabBarView(
          physics: const NeverScrollableScrollPhysics(),
          children: [
            _buildFleetMap(),
            _buildSecurityLogs(),
          ],
        ),
      ),
    );
  }
}
