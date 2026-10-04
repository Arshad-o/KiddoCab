import re

with open('lib/screens/parent_dashboard.dart', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add state variables
state_vars = """  GoogleMapController? _mapController;
  LatLng? _currentPosition;
  
  // NEW: Profile Settings State
  String _selectedLanguage = 'English';
  final List<String> _languages = [
    'English', 'Telugu (తెలుగు)', 'Hindi (हिन्दी)', 'Tamil (தமிழ்)', 
    'Kannada (ಕನ್ನಡ)', 'Malayalam (മലയാളം)', 'Punjabi (ਪੰਜਾਬੀ)', 
    'Gujarati (ગુજરાતી)', 'Rajasthani (राजस्थानी)'
  ];
  MapType _selectedMapType = MapType.normal;
"""

code = code.replace("""  GoogleMapController? _mapController;
  LatLng? _currentPosition;""", state_vars)

# 2. Update GoogleMap widget to use mapType
old_map = """        GoogleMap(
          initialCameraPosition"""
new_map = """        GoogleMap(
          mapType: _selectedMapType,
          initialCameraPosition"""
code = code.replace(old_map, new_map)

# 3. Add UI to the Profile tab
old_profile_card = """                  const Divider(),
                  ListTile(
                    leading: const Icon(Icons.phone),
                    title: const Text('Phone'),
                    subtitle: Text(user?.phone ?? 'Not available'),
                  ),
                ],
              ),
            ),
          ),"""

new_profile_card = """                  const Divider(),
                  ListTile(
                    leading: const Icon(Icons.phone),
                    title: const Text('Phone'),
                    subtitle: Text(user?.phone ?? 'Not available'),
                  ),
                  const Divider(),
                  ListTile(
                    leading: const Icon(Icons.language, color: Colors.blue),
                    title: const Text('App Language'),
                    trailing: DropdownButton<String>(
                      value: _selectedLanguage,
                      underline: const SizedBox(),
                      icon: const Icon(Icons.arrow_drop_down),
                      items: _languages.map((String lang) {
                        return DropdownMenuItem<String>(
                          value: lang,
                          child: Text(lang, style: const TextStyle(fontSize: 14)),
                        );
                      }).toList(),
                      onChanged: (String? newValue) {
                        if (newValue != null) {
                          setState(() => _selectedLanguage = newValue);
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(content: Text('Language updated to $newValue')),
                          );
                        }
                      },
                    ),
                  ),
                  const Divider(),
                  ListTile(
                    leading: const Icon(Icons.layers, color: Colors.green),
                    title: const Text('Map View Type'),
                    trailing: DropdownButton<MapType>(
                      value: _selectedMapType,
                      underline: const SizedBox(),
                      icon: const Icon(Icons.arrow_drop_down),
                      items: const [
                        DropdownMenuItem(value: MapType.normal, child: Text('Default (Ola/Uber)', style: TextStyle(fontSize: 14))),
                        DropdownMenuItem(value: MapType.satellite, child: Text('Satellite View', style: TextStyle(fontSize: 14))),
                        DropdownMenuItem(value: MapType.terrain, child: Text('Terrain View', style: TextStyle(fontSize: 14))),
                        DropdownMenuItem(value: MapType.hybrid, child: Text('Hybrid View', style: TextStyle(fontSize: 14))),
                      ],
                      onChanged: (MapType? newValue) {
                        if (newValue != null) {
                          setState(() => _selectedMapType = newValue);
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Map View updated! Check the Live Map tab.')),
                          );
                        }
                      },
                    ),
                  ),
                ],
              ),
            ),
          ),"""

code = code.replace(old_profile_card, new_profile_card)

with open('lib/screens/parent_dashboard.dart', 'w', encoding='utf-8') as f:
    f.write(code)
