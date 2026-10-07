import re

def fix_driver_dashboard():
    filepath = 'lib/screens/driver_dashboard.dart'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # The exact block to replace
    pattern = r'// --- TAB 2: Live Map ---[\s\S]*?// --- TAB 3: Profile ---'
    
    clean_live_map = """// --- TAB 2: Live Map ---
  Widget _buildLiveMap(ThemeData theme) {
    return ListenableBuilder(
      listenable: AppSettings.instance,
      builder: (context, _) {
        if (_mapController != null) {
          final isDark = Theme.of(context).brightness == Brightness.dark;
          _mapController!.setMapStyle(MapStyles.getStyle(AppSettings.instance.mapStyle, isDark));
        }
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
      },
    );
  }

  // --- TAB 3: Profile ---"""

    new_content = re.sub(pattern, clean_live_map, content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

fix_driver_dashboard()
