import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_jailbreak_detection/flutter_jailbreak_detection.dart';
import 'package:supabase_flutter/supabase_flutter.dart' hide MapType;
import 'screens/welcome_screen.dart';
import 'services/notification_service.dart';
import 'dart:io';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
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
    return MaterialApp(
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
      home: const SecurityCheckScreen(),
    );
  }
}

class SecurityCheckScreen extends StatefulWidget {
  const SecurityCheckScreen({super.key});

  @override
  State<SecurityCheckScreen> createState() => _SecurityCheckScreenState();
}

class _SecurityCheckScreenState extends State<SecurityCheckScreen> {
  bool _isChecking = true;
  bool _isCompromised = false;

  @override
  void initState() {
    super.initState();
    _runSecurityAudit();
  }

  Future<void> _runSecurityAudit() async {
    bool jailbroken = false;
    
    try {
      // Scans hardware for rooted Androids (Magisk, SuperSU) or jailbroken iOS (Cydia)
      jailbroken = await FlutterJailbreakDetection.jailbroken;
      // We can also check developer mode, but we will leave it out for testing environments.
      // bool developerMode = await FlutterJailbreakDetection.developerMode;
    } on PlatformException {
      jailbroken = true;
    }

    if (mounted) {
      if (jailbroken) {
        setState(() {
          _isCompromised = true;
          _isChecking = false;
        });
      } else {
        // Safe device, proceed to app!
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (_) => const WelcomeScreen()),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isChecking) {
      return const Scaffold(
        backgroundColor: Color(0xFF1E3A8A),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              CircularProgressIndicator(color: Colors.white),
              SizedBox(height: 24),
              Text(
                'Running Security Audit...',
                style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
              )
            ],
          ),
        ),
      );
    }

    // COMPROMISED SCREEN (RED)
    return Scaffold(
      backgroundColor: Colors.red[900],
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(32.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.gpp_bad, color: Colors.white, size: 100),
              const SizedBox(height: 24),
              const Text(
                'SECURITY BREACH DETECTED',
                style: TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
              const Text(
                'KiddoCab has detected that this device is Rooted or Jailbroken. '
                'To protect the location data of children, this app cannot be run on compromised hardware.',
                style: TextStyle(color: Colors.white70, fontSize: 16, height: 1.5),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 40),
              ElevatedButton.icon(
                onPressed: () => exit(0), // Instantly kill the app
                icon: const Icon(Icons.exit_to_app),
                label: const Text('Exit Application'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.white,
                  foregroundColor: Colors.red[900],
                  padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
                ),
              )
            ],
          ),
        ),
      ),
    );
  }
}
