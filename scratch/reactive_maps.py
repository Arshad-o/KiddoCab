import re

def make_map_reactive(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Wrap the entire Map widget with ListenableBuilder if it's not already
    
    # We'll just hook into the build method or Tab structure.
    # Actually, simpler: in _buildLiveMap / _buildLiveTracking, we add a listener to AppSettings in initState, but that's complex since we don't have a StatefulWidget for the tabs, it's all in the dashboard state.
    # We can just wrap the GoogleMap in a ListenableBuilder and call setMapStyle directly!
    
    target_google_map = "return GoogleMap("
    
    new_google_map = """return ListenableBuilder(
      listenable: AppSettings.instance,
      builder: (context, _) {
        // Dynamically apply style when settings or theme changes
        if (_mapController != null) {
          final isDark = Theme.of(context).brightness == Brightness.dark;
          _mapController!.setMapStyle(MapStyles.getStyle(AppSettings.instance.mapStyle, isDark));
        }
        return GoogleMap("""
        
    if target_google_map in content and "return ListenableBuilder(\n      listenable: AppSettings.instance," not in content:
        content = content.replace(target_google_map, new_google_map)
        
        # Don't forget to close the ListenableBuilder
        # GoogleMap ends with `);` at the end of the return statement.
        # This requires regex to find the end of GoogleMap properly.
        # Instead of parsing the AST in Python, let's just do a simple replace on the end:
        # Since _buildLiveMap ends with:
        #       },
        #     );
        #   }
        # We can replace the specific return GoogleMap block end.
        
        # In driver_dashboard.dart:
        #       },
        #     );
        #   }
        
        content = re.sub(r'(\s+onMapCreated:[\s\S]*?\}?,\n\s*\);)', r'\1\n      }\n    );', content)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

make_map_reactive('lib/screens/parent_dashboard.dart')
make_map_reactive('lib/screens/driver_dashboard.dart')
print("Maps made reactive")
