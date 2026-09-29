import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'screens/welcome_screen.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
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
          seedColor: const Color(0xFF1E3A8A), // Deep Trust Blue
          primary: const Color(0xFF1E3A8A),
          secondary: const Color(0xFFF59E0B), // Warm Amber
          tertiary: const Color(0xFF10B981), // Mint Green
          background: const Color(0xFFF3F4F6), // Off-White
        ),
      ),
      home: const WelcomeScreen(),
    );
  }
}
