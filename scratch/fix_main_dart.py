import re

def fix_main_dart():
    filepath = 'lib/main.dart'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix initialization
    old_main = """Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  await NotificationService.init();"""
    new_main = """Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  await AppSettings.instance.init();
  await NotificationService.init();"""
    if "await AppSettings.instance.init();" not in content:
        content = content.replace(old_main, new_main)

    # Fix MaterialApp wrapping
    old_app = """    return MaterialApp(
      title: 'KiddoCab',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF1E3A8A), 
          primary: const Color(0xFF1E3A8A),
          secondary: const Color(0xFFF59E0B), 
          tertiary: const Color(0xFF10B981), 
          surface: const Color(0xFFF3F4F6), 
        ),
      ),
      home: const AuthWrapper(),
    );"""
    
    new_app = """    return ListenableBuilder(
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
    
    if "ListenableBuilder(" not in content:
        content = content.replace(old_app, new_app)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

fix_main_dart()
