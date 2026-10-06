import re

def update_location_picker():
    filepath = 'lib/screens/parent/location_picker_screen.dart'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Add MapType variable
    old_vars = "  bool _isLoading = true;"
    new_vars = "  bool _isLoading = true;\n  MapType _currentMapType = MapType.normal;"
    content = content.replace(old_vars, new_vars)

    # Add MapType to GoogleMap
    old_map = "            myLocationEnabled: true,"
    new_map = "            mapType: _currentMapType,\n            myLocationEnabled: true,"
    content = content.replace(old_map, new_map)

    # Add PopupMenuButton to switch map types
    old_confirm_btn = """          if (_isLoading)
            const Center(child: CircularProgressIndicator()),
            
          // Confirm Button"""
    
    new_ui = """          if (_isLoading)
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
            
          // Confirm Button"""
    
    content = content.replace(old_confirm_btn, new_ui)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

update_location_picker()
