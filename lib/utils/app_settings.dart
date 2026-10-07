import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class AppSettings extends ChangeNotifier {
  static final AppSettings instance = AppSettings._internal();
  AppSettings._internal();

  late SharedPreferences _prefs;

  ThemeMode _themeMode = ThemeMode.system;
  String _mapStyle = 'standard';
  int _driverReminderMinutes = 15;

  ThemeMode get themeMode => _themeMode;
  String get mapStyle => _mapStyle;
  int get driverReminderMinutes => _driverReminderMinutes;

  Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
    
    final themeStr = _prefs.getString('themeMode') ?? 'system';
    if (themeStr == 'light') _themeMode = ThemeMode.light;
    else if (themeStr == 'dark') _themeMode = ThemeMode.dark;
    else _themeMode = ThemeMode.system;

    _mapStyle = _prefs.getString('mapStyle') ?? 'standard';
    _driverReminderMinutes = _prefs.getInt('driverReminderMinutes') ?? 15;
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

  void setDriverReminderMinutes(int minutes) {
    _driverReminderMinutes = minutes;
    _prefs.setInt('driverReminderMinutes', minutes);
    notifyListeners();
  }
}
