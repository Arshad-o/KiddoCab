import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:geolocator/geolocator.dart';

class LocationPickerScreen extends StatefulWidget {
  const LocationPickerScreen({super.key});

  @override
  State<LocationPickerScreen> createState() => _LocationPickerScreenState();
}

class _LocationPickerScreenState extends State<LocationPickerScreen> {
  GoogleMapController? _mapController;
  LatLng _currentCenter = const LatLng(28.6139, 77.2090); // Default placeholder
  bool _isLoading = true;
  MapType _currentMapType = MapType.normal;

  @override
  void initState() {
    super.initState();
    _fetchCurrentLocation();
  }

  Future<void> _fetchCurrentLocation() async {
    try {
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        throw Exception('Location services are disabled on your device.');
      }

      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          throw Exception('Location permissions were denied.');
        }
      }
      
      if (permission == LocationPermission.deniedForever) {
        throw Exception('Location permissions are permanently denied. Please allow them in Settings.');
      }

      final position = await Geolocator.getCurrentPosition(
        locationSettings: const LocationSettings(accuracy: LocationAccuracy.high),
      );
      final newLatLng = LatLng(position.latitude, position.longitude);

      setState(() {
        _currentCenter = newLatLng;
        _isLoading = false;
      });

      _mapController?.animateCamera(CameraUpdate.newLatLngZoom(newLatLng, 17.0));
    } catch (e) {
      setState(() => _isLoading = false);
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Could not get location: $e'),
            duration: const Duration(seconds: 4),
          )
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('Set Pick-up/Drop Point'),
        backgroundColor: theme.colorScheme.primary,
        foregroundColor: Colors.white,
      ),
      body: Stack(
        children: [
          GoogleMap(
            initialCameraPosition: CameraPosition(target: _currentCenter, zoom: 16),
            onMapCreated: (controller) => _mapController = controller,
            onCameraMove: (position) {
              _currentCenter = position.target;
            },
            mapType: _currentMapType,
            myLocationEnabled: true,
            myLocationButtonEnabled: true,
            zoomControlsEnabled: false,
          ),
          
          // Static Map Pin in the exact center of the screen
          const Center(
            child: Padding(
              padding: EdgeInsets.only(bottom: 40.0), // Shift up to point exactly at center
              child: Icon(Icons.location_pin, size: 50, color: Colors.red),
            ),
          ),
          
          if (_isLoading)
            const Center(child: CircularProgressIndicator()),
            
          // Map Type Switcher
          Positioned(
            top: 16,
            right: 16,
            child: PopupMenuButton<MapType>(
              icon: CircleAvatar(
                backgroundColor: Colors.white,
                child: Icon(Icons.layers, color: theme.colorScheme.primary),
              ),
              onSelected: (MapType result) {
                setState(() {
                  _currentMapType = result;
                });
              },
              itemBuilder: (BuildContext context) => <PopupMenuEntry<MapType>>[
                const PopupMenuItem<MapType>(
                  value: MapType.normal,
                  child: Text('Normal View'),
                ),
                const PopupMenuItem<MapType>(
                  value: MapType.satellite,
                  child: Text('Satellite View'),
                ),
                const PopupMenuItem<MapType>(
                  value: MapType.terrain,
                  child: Text('Terrain View'),
                ),
                const PopupMenuItem<MapType>(
                  value: MapType.hybrid,
                  child: Text('Hybrid View'),
                ),
              ],
            ),
          ),
            
          // Confirm Button
          Positioned(
            bottom: 40,
            left: 20,
            right: 20,
            child: SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: () {
                  // Return the exact coordinates the user selected
                  Navigator.pop(context, _currentCenter);
                },
                icon: const Icon(Icons.check_circle),
                label: const Text('Confirm This Location', style: TextStyle(fontSize: 18)),
                style: ElevatedButton.styleFrom(
                  backgroundColor: theme.colorScheme.secondary,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  elevation: 8,
                ),
              ),
            ),
          )
        ],
      ),
    );
  }
}
