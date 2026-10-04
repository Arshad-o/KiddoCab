import 'package:flutter/material.dart';
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

  @override
  void initState() {
    super.initState();
    _fetchSecurityAlerts();
    _listenToFleetLocations();
  }

  void _fetchSecurityAlerts() async {
    final response = await _supabase.from('alerts').select().order('created_at', ascending: false).limit(50);
    if (mounted) {
      setState(() {
        _securityAlerts = List<Map<String, dynamic>>.from(response);
      });
    }
  }

  void _listenToFleetLocations() {
    _supabase.channel('public:locations').onPostgresChanges(
      event: PostgresChangeEvent.insert,
      schema: 'public',
      table: 'locations',
      callback: (payload) {
        final newRecord = payload.newRecord;
        if (mounted) {
          setState(() {
            _liveDrivers[newRecord['driver_id'].toString()] = LatLng(
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
          infoWindow: InfoWindow(title: 'Driver ID: ${entry.key.substring(0, 6)}'),
          icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueBlue),
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
