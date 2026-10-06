import os
import re

# 1. Create AppSettings
app_settings_code = """import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class AppSettings extends ChangeNotifier {
  static final AppSettings instance = AppSettings._internal();
  AppSettings._internal();

  late SharedPreferences _prefs;

  ThemeMode _themeMode = ThemeMode.system;
  String _mapStyle = 'standard';

  ThemeMode get themeMode => _themeMode;
  String get mapStyle => _mapStyle;

  Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
    
    final themeStr = _prefs.getString('themeMode') ?? 'system';
    if (themeStr == 'light') _themeMode = ThemeMode.light;
    else if (themeStr == 'dark') _themeMode = ThemeMode.dark;
    else _themeMode = ThemeMode.system;

    _mapStyle = _prefs.getString('mapStyle') ?? 'standard';
    notifyListeners();
  }

  void setThemeMode(ThemeMode mode) {
    _themeMode = mode;
    _prefs.setString('themeMode', mode.name);
    notifyListeners();
  }

  void setMapStyle(String style) {
    _mapStyle = style;
    _prefs.setString('mapStyle', style);
    notifyListeners();
  }
}
"""
os.makedirs('lib/utils', exist_ok=True)
with open('lib/utils/app_settings.dart', 'w', encoding='utf-8') as f:
    f.write(app_settings_code)

# 2. Create MapStyles
map_styles_code = """import 'package:flutter/material.dart';

class MapStyles {
  static const String uberStyle = '''[
    {"elementType": "geometry", "stylers": [{"color": "#212121"}]},
    {"elementType": "labels.icon", "stylers": [{"visibility": "off"}]},
    {"elementType": "labels.text.fill", "stylers": [{"color": "#757575"}]},
    {"elementType": "labels.text.stroke", "stylers": [{"color": "#212121"}]},
    {"featureType": "administrative", "elementType": "geometry", "stylers": [{"color": "#757575"}]},
    {"featureType": "administrative.country", "elementType": "labels.text.fill", "stylers": [{"color": "#9e9e9e"}]},
    {"featureType": "administrative.land_parcel", "stylers": [{"visibility": "off"}]},
    {"featureType": "administrative.locality", "elementType": "labels.text.fill", "stylers": [{"color": "#bdbdbd"}]},
    {"featureType": "poi", "elementType": "labels.text.fill", "stylers": [{"color": "#757575"}]},
    {"featureType": "poi.park", "elementType": "geometry", "stylers": [{"color": "#181818"}]},
    {"featureType": "poi.park", "elementType": "labels.text.fill", "stylers": [{"color": "#616161"}]},
    {"featureType": "poi.park", "elementType": "labels.text.stroke", "stylers": [{"color": "#1b1b1b"}]},
    {"featureType": "road", "elementType": "geometry.fill", "stylers": [{"color": "#2c2c2c"}]},
    {"featureType": "road", "elementType": "labels.text.fill", "stylers": [{"color": "#8a8a8a"}]},
    {"featureType": "road.arterial", "elementType": "geometry", "stylers": [{"color": "#373737"}]},
    {"featureType": "road.highway", "elementType": "geometry", "stylers": [{"color": "#3c3c3c"}]},
    {"featureType": "road.highway.controlled_access", "elementType": "geometry", "stylers": [{"color": "#4e4e4e"}]},
    {"featureType": "road.local", "elementType": "labels.text.fill", "stylers": [{"color": "#616161"}]},
    {"featureType": "transit", "elementType": "labels.text.fill", "stylers": [{"color": "#757575"}]},
    {"featureType": "water", "elementType": "geometry", "stylers": [{"color": "#000000"}]},
    {"featureType": "water", "elementType": "labels.text.fill", "stylers": [{"color": "#3d3d3d"}]}
  ]''';

  static const String olaStyle = '''[
    {"featureType": "landscape.man_made", "elementType": "geometry.fill", "stylers": [{"color": "#f1f6f1"}]},
    {"featureType": "poi", "elementType": "geometry.fill", "stylers": [{"color": "#dcedd9"}]},
    {"featureType": "road.highway", "elementType": "geometry.fill", "stylers": [{"color": "#f8c967"}]},
    {"featureType": "road.highway", "elementType": "geometry.stroke", "stylers": [{"color": "#e9a326"}]},
    {"featureType": "road.arterial", "elementType": "geometry.fill", "stylers": [{"color": "#fdfdfd"}]},
    {"featureType": "water", "elementType": "geometry.fill", "stylers": [{"color": "#b2dff0"}]}
  ]''';

  static const String rapidoStyle = '''[
    {"elementType": "geometry", "stylers": [{"color": "#ebe3cd"}]},
    {"elementType": "labels.text.fill", "stylers": [{"color": "#523735"}]},
    {"elementType": "labels.text.stroke", "stylers": [{"color": "#f5f1e6"}]},
    {"featureType": "administrative", "elementType": "geometry.stroke", "stylers": [{"color": "#c9b2a6"}]},
    {"featureType": "administrative.land_parcel", "elementType": "geometry.stroke", "stylers": [{"color": "#dcd2be"}]},
    {"featureType": "administrative.land_parcel", "elementType": "labels.text.fill", "stylers": [{"color": "#ae9e90"}]},
    {"featureType": "landscape.natural", "elementType": "geometry", "stylers": [{"color": "#dfd2ae"}]},
    {"featureType": "poi", "elementType": "geometry", "stylers": [{"color": "#dfd2ae"}]},
    {"featureType": "poi", "elementType": "labels.text.fill", "stylers": [{"color": "#93817c"}]},
    {"featureType": "poi.park", "elementType": "geometry.fill", "stylers": [{"color": "#a5b076"}]},
    {"featureType": "poi.park", "elementType": "labels.text.fill", "stylers": [{"color": "#447530"}]},
    {"featureType": "road", "elementType": "geometry", "stylers": [{"color": "#f5f1e6"}]},
    {"featureType": "road.arterial", "elementType": "geometry", "stylers": [{"color": "#fdfcf8"}]},
    {"featureType": "road.highway", "elementType": "geometry", "stylers": [{"color": "#f8c967"}]},
    {"featureType": "road.highway", "elementType": "geometry.stroke", "stylers": [{"color": "#e9a326"}]},
    {"featureType": "road.highway.controlled_access", "elementType": "geometry", "stylers": [{"color": "#e98d58"}]},
    {"featureType": "road.highway.controlled_access", "elementType": "geometry.stroke", "stylers": [{"color": "#db8555"}]},
    {"featureType": "road.local", "elementType": "labels.text.fill", "stylers": [{"color": "#806b63"}]},
    {"featureType": "transit.line", "elementType": "geometry", "stylers": [{"color": "#dfd2ae"}]},
    {"featureType": "transit.line", "elementType": "labels.text.fill", "stylers": [{"color": "#8f7d77"}]},
    {"featureType": "transit.line", "elementType": "labels.text.stroke", "stylers": [{"color": "#ebe3cd"}]},
    {"featureType": "transit.station", "elementType": "geometry", "stylers": [{"color": "#dfd2ae"}]},
    {"featureType": "water", "elementType": "geometry.fill", "stylers": [{"color": "#b9d3c2"}]},
    {"featureType": "water", "elementType": "labels.text.fill", "stylers": [{"color": "#92998d"}]}
  ]''';

  static const String darkStyle = '''[
    {"elementType": "geometry", "stylers": [{"color": "#242f3e"}]},
    {"elementType": "labels.text.fill", "stylers": [{"color": "#746855"}]},
    {"elementType": "labels.text.stroke", "stylers": [{"color": "#242f3e"}]},
    {"featureType": "administrative.locality", "elementType": "labels.text.fill", "stylers": [{"color": "#d59563"}]},
    {"featureType": "poi", "elementType": "labels.text.fill", "stylers": [{"color": "#d59563"}]},
    {"featureType": "poi.park", "elementType": "geometry", "stylers": [{"color": "#263c3f"}]},
    {"featureType": "poi.park", "elementType": "labels.text.fill", "stylers": [{"color": "#6b9a76"}]},
    {"featureType": "road", "elementType": "geometry", "stylers": [{"color": "#38414e"}]},
    {"featureType": "road", "elementType": "geometry.stroke", "stylers": [{"color": "#212a37"}]},
    {"featureType": "road", "elementType": "labels.text.fill", "stylers": [{"color": "#9ca5b3"}]},
    {"featureType": "road.highway", "elementType": "geometry", "stylers": [{"color": "#746855"}]},
    {"featureType": "road.highway", "elementType": "geometry.stroke", "stylers": [{"color": "#1f2835"}]},
    {"featureType": "road.highway", "elementType": "labels.text.fill", "stylers": [{"color": "#f3d19c"}]},
    {"featureType": "transit", "elementType": "geometry", "stylers": [{"color": "#2f3948"}]},
    {"featureType": "transit.station", "elementType": "labels.text.fill", "stylers": [{"color": "#d59563"}]},
    {"featureType": "water", "elementType": "geometry", "stylers": [{"color": "#17263c"}]},
    {"featureType": "water", "elementType": "labels.text.fill", "stylers": [{"color": "#515c6d"}]},
    {"featureType": "water", "elementType": "labels.text.stroke", "stylers": [{"color": "#17263c"}]}
  ]''';

  static String? getStyle(String styleKey, bool isDarkMode) {
    switch (styleKey) {
      case 'uber': return uberStyle;
      case 'ola': return olaStyle;
      case 'rapido': return rapidoStyle;
      case 'standard': return isDarkMode ? darkStyle : null;
      default: return isDarkMode ? darkStyle : null;
    }
  }
}
"""
with open('lib/utils/map_styles.dart', 'w', encoding='utf-8') as f:
    f.write(map_styles_code)

# 3. Update main.dart
main_path = 'lib/main.dart'
with open(main_path, 'r', encoding='utf-8') as f:
    main_content = f.read()

if 'AppSettings.init()' not in main_content:
    main_content = main_content.replace(
        "import 'package:flutter/material.dart';",
        "import 'package:flutter/material.dart';\nimport 'utils/app_settings.dart';"
    )
    main_content = main_content.replace(
        "void main() async {",
        "void main() async {\n  WidgetsFlutterBinding.ensureInitialized();\n  await AppSettings.instance.init();"
    )
    
    # Wrap MaterialApp with ListenableBuilder
    material_app_str = """    return MaterialApp(
      title: 'KiddoCab',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF1E3A8A), 
          primary: const Color(0xFF1E3A8A),
          secondary: const Color(0xFFF59E0B), 
          tertiary: const Color(0xFF10B981), 
          background: const Color(0xFFF3F4F6), 
        ),
      ),
      home: const AuthWrapper(),
    );"""
    
    new_material_app = """    return ListenableBuilder(
      listenable: AppSettings.instance,
      builder: (context, _) {
        return MaterialApp(
          title: 'KiddoCab',
          debugShowCheckedModeBanner: false,
          themeMode: AppSettings.instance.themeMode,
          theme: ThemeData(
            useMaterial3: true,
            colorScheme: ColorScheme.fromSeed(
              brightness: Brightness.light,
              seedColor: const Color(0xFF1E3A8A), 
              primary: const Color(0xFF1E3A8A),
              secondary: const Color(0xFFF59E0B), 
              tertiary: const Color(0xFF10B981), 
              surface: const Color(0xFFF3F4F6), 
            ),
          ),
          darkTheme: ThemeData(
            useMaterial3: true,
            colorScheme: ColorScheme.fromSeed(
              brightness: Brightness.dark,
              seedColor: const Color(0xFF1E3A8A), 
              primary: const Color(0xFF60A5FA),
              secondary: const Color(0xFFFBBF24), 
              tertiary: const Color(0xFF34D399), 
              surface: const Color(0xFF111827), 
            ),
          ),
          home: const AuthWrapper(),
        );
      }
    );"""
    
    # Replace background with surface (deprecated check)
    main_content = main_content.replace('background: const Color(0xFFF3F4F6),', 'surface: const Color(0xFFF3F4F6),')
    main_content = main_content.replace(material_app_str, new_material_app)
    
    with open(main_path, 'w', encoding='utf-8') as f:
        f.write(main_content)

print("Setup main app settings architecture completed.")
