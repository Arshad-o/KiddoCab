import re

with open('lib/screens/admin/admin_dashboard.dart', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add imports for marker processing
if "import 'dart:ui' as ui;" not in code:
    code = code.replace("import 'package:flutter/material.dart';", "import 'package:flutter/material.dart';\nimport 'dart:ui' as ui;\nimport 'package:flutter/services.dart';")

# 2. Add marker cache map
state_vars = """  Map<String, LatLng> _liveDrivers = {};
  List<Map<String, dynamic>> _securityAlerts = [];
  Map<String, BitmapDescriptor> _customMarkers = {};"""
code = code.replace("  Map<String, LatLng> _liveDrivers = {};\n  List<Map<String, dynamic>> _securityAlerts = [];", state_vars)

# 3. Add marker generation logic
init_state_old = """  @override
  void initState() {
    super.initState();
    _fetchSecurityAlerts();
    _listenToFleetLocations();
  }"""
init_state_new = """  @override
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
  }"""
code = code.replace(init_state_old, init_state_new)

# 4. Update the _listenToFleetLocations
listen_old = """  void _listenToFleetLocations() {
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
    ).subscribe();"""
listen_new = """  Map<String, String> _driverVehicleMap = {};
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
    ).subscribe();"""
code = code.replace(listen_old, listen_new)

# 5. Update marker drawing
marker_old = """      markers: _liveDrivers.entries.map((entry) {
        return Marker(
          markerId: MarkerId(entry.key),
          position: entry.value,
          infoWindow: InfoWindow(title: 'Driver ID: ${entry.key.substring(0, 6)}'),
          icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueBlue),
        );
      }).toSet(),"""
marker_new = """      markers: _liveDrivers.entries.map((entry) {
        return Marker(
          markerId: MarkerId(entry.key),
          position: entry.value,
          infoWindow: InfoWindow(title: 'KiddoCab Driver', snippet: _driverVehicleMap[entry.key] ?? 'Tracking'),
          icon: _driverMarkerIcons[entry.key] ?? BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueBlue),
        );
      }).toSet(),"""
code = code.replace(marker_old, marker_new)

with open('lib/screens/admin/admin_dashboard.dart', 'w', encoding='utf-8') as f:
    f.write(code)
