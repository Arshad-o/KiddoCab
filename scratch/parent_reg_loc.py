import re

with open('lib/screens/parent/parent_register_screen.dart', 'r', encoding='utf-8') as f:
    content = f.read()

# Add import
if "import 'location_picker_screen.dart';" not in content:
    content = content.replace("import 'package:flutter/material.dart';", "import 'package:flutter/material.dart';\nimport 'location_picker_screen.dart';\nimport 'package:google_maps_flutter/google_maps_flutter.dart';")

# Replace button logic
old_btn = r"ElevatedButton\.icon\([\s\S]*?Fix Geo Location \(Automated\)'\),[\s\S]*?padding: const EdgeInsets\.symmetric\(vertical: 16\),\n\s*\),\n\s*\),"

new_btn = """ElevatedButton.icon(
                onPressed: () async {
                  final LatLng? selectedLocation = await Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => const LocationPickerScreen()),
                  );
                  
                  if (selectedLocation != null) {
                    setState(() {
                      _location = 'Lat: ${selectedLocation.latitude.toStringAsFixed(4)}, Lng: ${selectedLocation.longitude.toStringAsFixed(4)}';
                    });
                  }
                },
                icon: const Icon(Icons.map),
                label: const Text('Set Precise Pick-up Location on Map'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: theme.colorScheme.tertiary,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
              ),"""

content = re.sub(old_btn, new_btn, content)

with open('lib/screens/parent/parent_register_screen.dart', 'w', encoding='utf-8') as f:
    f.write(content)
