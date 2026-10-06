import re

def inject_settings_ui(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Import dependencies
    if "import '../utils/app_settings.dart';" not in content:
        content = content.replace("import 'package:flutter/material.dart';", "import 'package:flutter/material.dart';\nimport '../utils/app_settings.dart';\nimport '../utils/map_styles.dart';")

    # The settings UI Card
    settings_ui = """            const SizedBox(height: 24),
            Text('App Preferences', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold, color: theme.colorScheme.primary)),
            const SizedBox(height: 16),
            Card(
              elevation: 2,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: ListenableBuilder(
                  listenable: AppSettings.instance,
                  builder: (context, _) {
                    return Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Theme Switcher
                        const Text('App Theme', style: TextStyle(fontWeight: FontWeight.bold)),
                        const SizedBox(height: 8),
                        SegmentedButton<ThemeMode>(
                          segments: const [
                            ButtonSegment(value: ThemeMode.light, icon: Icon(Icons.light_mode), label: Text('Light')),
                            ButtonSegment(value: ThemeMode.dark, icon: Icon(Icons.dark_mode), label: Text('Dark')),
                            ButtonSegment(value: ThemeMode.system, icon: Icon(Icons.settings_system_daydream), label: Text('System')),
                          ],
                          selected: {AppSettings.instance.themeMode},
                          onSelectionChanged: (Set<ThemeMode> newSelection) {
                            AppSettings.instance.setThemeMode(newSelection.first);
                          },
                        ),
                        
                        const Divider(height: 32),
                        
                        // Map Style Selector
                        const Text('Map Style (Navigation View)', style: TextStyle(fontWeight: FontWeight.bold)),
                        const SizedBox(height: 8),
                        DropdownButtonFormField<String>(
                          value: AppSettings.instance.mapStyle,
                          decoration: const InputDecoration(border: OutlineInputBorder(), prefixIcon: Icon(Icons.map)),
                          items: const [
                            DropdownMenuItem(value: 'standard', child: Text('Standard Google Map')),
                            DropdownMenuItem(value: 'uber', child: Text('Uber Style (Dark & Stealth)')),
                            DropdownMenuItem(value: 'ola', child: Text('Ola Style (Green & Yellow)')),
                            DropdownMenuItem(value: 'rapido', child: Text('Rapido Style (Vibrant Yellow)')),
                          ],
                          onChanged: (val) {
                            if (val != null) {
                              AppSettings.instance.setMapStyle(val);
                            }
                          },
                        ),
                      ],
                    );
                  }
                ),
              ),
            ),
            const SizedBox(height: 24),"""

    # Inject into Profile view
    if "Text('App Preferences'" not in content:
        # Find where the Logout button is, and put this right above it
        logout_button = """            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon("""
        if logout_button in content:
            content = content.replace(logout_button, settings_ui + "\n" + logout_button)
    
    # Inject Map Styles into GoogleMap
    google_map_str = "        onMapCreated: (GoogleMapController controller) {"
    new_google_map_str = """        onMapCreated: (GoogleMapController controller) {
          final isDark = Theme.of(context).brightness == Brightness.dark;
          controller.setMapStyle(MapStyles.getStyle(AppSettings.instance.mapStyle, isDark));"""
          
    if google_map_str in content and "controller.setMapStyle" not in content:
        content = content.replace(google_map_str, new_google_map_str)

    # Add ListenableBuilder around the Map view to hot-reload map style if needed?
    # Actually, `setMapStyle` only applies dynamically if we call it on the controller when the setting changes.
    # To do that, we can just use `ListenableBuilder` inside `_buildLiveMap` / `_buildLiveTracking`
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

inject_settings_ui('lib/screens/parent_dashboard.dart')
inject_settings_ui('lib/screens/driver_dashboard.dart')
print("Injected Settings UI and Map Styles")
