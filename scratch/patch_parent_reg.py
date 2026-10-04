import re

with open('lib/screens/parent/parent_register_screen.dart', 'r', encoding='utf-8') as f:
    code = f.read()

# Add dropLocation state variable
code = code.replace("  String? _location;\n  bool _acceptedTerms", "  String? _location;\n  String? _dropLocation;\n  bool _acceptedTerms")

# Add validation for dropLocation
old_val = """    if (_location == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please set your precise pick-up location!'), backgroundColor: Colors.red),
      );
      return;
    }"""
new_val = """    if (_location == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please set your precise pick-up location!'), backgroundColor: Colors.red),
      );
      return;
    }

    if (_dropLocation == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please set your precise drop-off (School) location!'), backgroundColor: Colors.red),
      );
      return;
    }"""
code = code.replace(old_val, new_val)

# Add UI for dropLocation
old_ui = """              if (_location != null) ...[
                const SizedBox(height: 8),
                Text('Location Saved!', style: theme.textTheme.bodyMedium?.copyWith(color: Colors.green, fontWeight: FontWeight.bold), textAlign: TextAlign.center),
              ],
              
              const SizedBox(height: 24),"""

new_ui = """              if (_location != null) ...[
                const SizedBox(height: 8),
                Text('Pick-up Location Saved!', style: theme.textTheme.bodyMedium?.copyWith(color: Colors.green, fontWeight: FontWeight.bold), textAlign: TextAlign.center),
              ],
              
              const SizedBox(height: 16),
              ElevatedButton.icon(
                onPressed: () async {
                  final LatLng? selectedLocation = await Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => const LocationPickerScreen()),
                  );
                  if (selectedLocation != null) {
                    setState(() {
                      _dropLocation = 'Lat: ${selectedLocation.latitude.toStringAsFixed(4)}, Lng: ${selectedLocation.longitude.toStringAsFixed(4)}';
                    });
                  }
                },
                icon: const Icon(Icons.school),
                label: const Text('Set Precise Drop-off (School) *'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: _dropLocation == null ? theme.colorScheme.tertiary : Colors.green,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
              ),
              if (_dropLocation != null) ...[
                const SizedBox(height: 8),
                Text('Drop-off Location Saved!', style: theme.textTheme.bodyMedium?.copyWith(color: Colors.green, fontWeight: FontWeight.bold), textAlign: TextAlign.center),
              ],
              
              const SizedBox(height: 24),"""
code = code.replace(old_ui, new_ui)

with open('lib/screens/parent/parent_register_screen.dart', 'w', encoding='utf-8') as f:
    f.write(code)
