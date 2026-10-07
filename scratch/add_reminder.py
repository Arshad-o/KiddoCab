import re

def add_reminder_setting():
    filepath = 'lib/utils/app_settings.dart'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if 'driverReminderMinutes' not in content:
        old_decl = """  ThemeMode _themeMode = ThemeMode.system;
  String _mapStyle = 'standard';"""
        new_decl = """  ThemeMode _themeMode = ThemeMode.system;
  String _mapStyle = 'standard';
  int _driverReminderMinutes = 15;"""
        content = content.replace(old_decl, new_decl)
        
        old_getters = """  ThemeMode get themeMode => _themeMode;
  String get mapStyle => _mapStyle;"""
        new_getters = """  ThemeMode get themeMode => _themeMode;
  String get mapStyle => _mapStyle;
  int get driverReminderMinutes => _driverReminderMinutes;"""
        content = content.replace(old_getters, new_getters)
        
        old_init = """    _mapStyle = _prefs.getString('mapStyle') ?? 'standard';
    notifyListeners();"""
        new_init = """    _mapStyle = _prefs.getString('mapStyle') ?? 'standard';
    _driverReminderMinutes = _prefs.getInt('driverReminderMinutes') ?? 15;
    notifyListeners();"""
        content = content.replace(old_init, new_init)
        
        old_methods = """  void setMapStyle(String style) {
    _mapStyle = style;
    _prefs.setString('mapStyle', style);
    notifyListeners();
  }
}"""
        new_methods = """  void setMapStyle(String style) {
    _mapStyle = style;
    _prefs.setString('mapStyle', style);
    notifyListeners();
  }

  void setDriverReminderMinutes(int minutes) {
    _driverReminderMinutes = minutes;
    _prefs.setInt('driverReminderMinutes', minutes);
    notifyListeners();
  }
}"""
        content = content.replace(old_methods, new_methods)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

add_reminder_setting()
