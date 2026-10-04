import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
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
      home: const WelcomeScreen(),
    );
  }
}
