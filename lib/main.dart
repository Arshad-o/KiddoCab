import 'package:flutter/material.dart';
import 'utils/app_settings.dart';
import 'package:flutter/services.dart';
import 'package:supabase_flutter/supabase_flutter.dart' hide MapType;
import 'screens/welcome_screen.dart';
import 'screens/parent_dashboard.dart';
import 'screens/driver_dashboard.dart';
import 'services/notification_service.dart';
import 'services/auth_service.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  await AppSettings.instance.init();
  await NotificationService.init();

  await Supabase.initialize(
    url: 'https://ydspzbkbggpljeajjjwz.supabase.co',
    anonKey: 'sb_publishable_KLbqZOu5vri7br9jdGlmgA_iIDzf6X6',
  );
  
  runApp(const KiddoCabApp());
}

class KiddoCabApp extends StatelessWidget {
  const KiddoCabApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
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
    );
  }
}

class AuthWrapper extends StatefulWidget {
  const AuthWrapper({super.key});

  @override
  State<AuthWrapper> createState() => _AuthWrapperState();
}

class _AuthWrapperState extends State<AuthWrapper> {
  @override
  void initState() {
    super.initState();
    _checkAuth();
  }

  Future<void> _checkAuth() async {
    // Delay execution until after the first frame is rendered
    // to safely use Navigator context.
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      final session = Supabase.instance.client.auth.currentSession;
      if (session == null) {
        if (!mounted) return;
        Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const WelcomeScreen()));
        return;
      }
      
      // User is logged in, fetch their role
      final email = session.user.email;
      if (email != null) {
        final role = await AuthService.getUserRole(email);
        if (!mounted) return;
        
        if (role == 'parent') {
          Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const ParentDashboard()));
        } else if (role == 'driver') {
          Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const DriverDashboard()));
        } else {
          Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const WelcomeScreen()));
        }
      } else {
        if (!mounted) return;
        Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const WelcomeScreen()));
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      backgroundColor: Color(0xFF1E3A8A),
      body: Center(
        child: CircularProgressIndicator(color: Colors.white),
      ),
    );
  }
}
