import re

with open('lib/screens/parent_dashboard.dart', 'r', encoding='utf-8') as f:
    code = f.read()

# Add imports if missing (geolocator should be there, but let's check)
if 'package:geolocator/geolocator.dart' not in code:
    code = code.replace("import 'package:google_maps_flutter/google_maps_flutter.dart';", "import 'package:google_maps_flutter/google_maps_flutter.dart';\nimport 'package:geolocator/geolocator.dart';")

# Add state variables
state_vars = """
  GoogleMapController? _mapController;
  LatLng? _currentPosition;
"""
code = code.replace("RealtimeChannel? _locationsChannel;", "RealtimeChannel? _locationsChannel;\n" + state_vars)

# Add _determinePosition inside initState
init_state = """  @override
  void initState() {
    super.initState();
    _listenToDriverStatus();
    _determinePosition();
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
"""

code = re.sub(r"  @override\s+void initState\(\) \{\s+super\.initState\(\);\s+_listenToDriverStatus\(\);\s+\}", init_state, code)

# Fix the GoogleMap widget
old_map = """        // Full Screen Map
        const GoogleMap(
          initialCameraPosition: CameraPosition(
            target: LatLng(28.6139, 77.2090),
            zoom: 14.0,
          ),
          myLocationEnabled: true,
          zoomControlsEnabled: false,
        ),"""

new_map = """        // Full Screen Map
        GoogleMap(
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

code = code.replace(old_map, new_map)

with open('lib/screens/parent_dashboard.dart', 'w', encoding='utf-8') as f:
    f.write(code)
