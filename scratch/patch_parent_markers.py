import re

with open('lib/screens/parent_dashboard.dart', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add imports for marker processing
if "import 'dart:ui' as ui;" not in code:
    code = code.replace("import 'package:flutter/material.dart';", "import 'package:flutter/material.dart';\nimport 'dart:ui' as ui;\nimport 'package:flutter/services.dart';")

# 2. Add state variables for driver tracking
state_vars = """  MapType _selectedMapType = MapType.normal;

  LatLng? _driverPosition;
  BitmapDescriptor? _driverMarkerIcon;
  String _driverVehicleType = 'School Bus'; // Default fallback
"""
code = code.replace("  MapType _selectedMapType = MapType.normal;", state_vars)

# 3. Add _loadDriverIcon logic
init_state = """  @override
  void initState() {
    super.initState();
    _listenToDriverStatus();
    _listenToSecurityAlerts();
    _determinePosition();
    _fetchDriverVehicleType();
  }

  Future<void> _fetchDriverVehicleType() async {
    try {
      // In MVP, we just get any driver's vehicle or a specific one if tied.
      final response = await _supabase.from('users').select('vehicle_type').eq('role', 'driver').limit(1);
      if (response.isNotEmpty && response[0]['vehicle_type'] != null) {
        _driverVehicleType = response[0]['vehicle_type'];
      }
      _loadDriverIcon();
    } catch (e) {
      _loadDriverIcon();
    }
  }

  Future<void> _loadDriverIcon() async {
    String assetPath = 'assets/images/tata_magic.png'; // default fallback
    if (_driverVehicleType == 'Auto Rickshaw') assetPath = 'assets/images/autoimg.jpg';
    if (_driverVehicleType == 'Large Auto') assetPath = 'assets/images/big_auto_img.jpg';
    if (_driverVehicleType == 'Tata Magic') assetPath = 'assets/images/tata_magic.png';
    if (_driverVehicleType == 'Cab' || _driverVehicleType == 'Sedan') assetPath = 'assets/images/cab.avif';
    
    try {
      ByteData data = await rootBundle.load(assetPath);
      ui.Codec codec = await ui.instantiateImageCodec(data.buffer.asUint8List(), targetWidth: 120);
      ui.FrameInfo fi = await codec.getNextFrame();
      final bytes = (await fi.image.toByteData(format: ui.ImageByteFormat.png))!.buffer.asUint8List();
      setState(() {
        _driverMarkerIcon = BitmapDescriptor.fromBytes(bytes);
      });
    } catch (e) {
      print('Error loading custom marker: $e');
      setState(() {
        _driverMarkerIcon = BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueOrange);
      });
    }
  }
"""
code = code.replace("""  @override
  void initState() {
    super.initState();
    _listenToDriverStatus();
    _listenToSecurityAlerts();
    _determinePosition();
  }""", init_state)


# 4. Update _listenToDriverStatus to update _driverPosition and animate map
old_listen = """  void _listenToDriverStatus() {
    _locationsChannel = _supabase.channel('public:locations').onPostgresChanges(
      event: PostgresChangeEvent.insert,
      schema: 'public',
      table: 'locations',
      callback: (payload) {
        NotificationService.showNotification(
          id: 1,"""
new_listen = """  bool _hasTriggeredStartNotification = false;

  void _listenToDriverStatus() {
    _locationsChannel = _supabase.channel('public:locations').onPostgresChanges(
      event: PostgresChangeEvent.insert,
      schema: 'public',
      table: 'locations',
      callback: (payload) {
        final newRecord = payload.newRecord;
        if (mounted) {
          setState(() {
            _driverPosition = LatLng(newRecord['latitude'], newRecord['longitude']);
          });
          if (_mapController != null && _driverPosition != null) {
            _mapController!.animateCamera(CameraUpdate.newLatLngZoom(_driverPosition!, 16.0));
          }
        }
        
        if (!_hasTriggeredStartNotification) {
          _hasTriggeredStartNotification = true;
          NotificationService.showNotification(
            id: 1,"""
code = code.replace(old_listen, new_listen)


# 5. Update _buildLiveMap to draw the driver's marker!
old_map = """        GoogleMap(
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
        ),"""
new_map = """        GoogleMap(
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
          markers: {
            if (_driverPosition != null)
              Marker(
                markerId: const MarkerId('driver'),
                position: _driverPosition!,
                icon: _driverMarkerIcon ?? BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueOrange),
                infoWindow: InfoWindow(title: 'KiddoCab - $_driverVehicleType', snippet: 'Live Tracking'),
              )
          },
          onMapCreated: (GoogleMapController controller) {
            _mapController = controller;
            if (_driverPosition != null) {
              _mapController!.animateCamera(CameraUpdate.newLatLngZoom(_driverPosition!, 16.0));
            } else if (_currentPosition != null) {
              _mapController!.animateCamera(CameraUpdate.newLatLngZoom(_currentPosition!, 16.0));
            }
          },
        ),"""
code = code.replace(old_map, new_map)

with open('lib/screens/parent_dashboard.dart', 'w', encoding='utf-8') as f:
    f.write(code)
