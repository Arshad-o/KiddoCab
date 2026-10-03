import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import '../services/auth_service.dart';
import 'parent/cab_selection_screen.dart';

import 'package:supabase_flutter/supabase_flutter.dart';
import '../services/notification_service.dart';

class ParentDashboard extends StatefulWidget {
  
  @override
  State<ParentDashboard> createState() => _ParentDashboardState();
}

class _ParentDashboardState extends State<ParentDashboard> {

    final _supabase = Supabase.instance.client;
  RealtimeChannel? _locationsChannel;

  @override
  void initState() {
    super.initState();
    _listenToDriverStatus();
  }

  void _listenToDriverStatus() {
    // Listen for incoming live tracking updates from the Driver!
    _locationsChannel = _supabase.channel('public:locations').onPostgresChanges(
      event: PostgresChangeEvent.insert,
      schema: 'public',
      table: 'locations',
      callback: (payload) {
        // Trigger a push notification to the parent's phone!
        NotificationService.showNotification(
          id: 1,
          title: '🚐 Trip Started!',
          body: 'Your KiddoCab has started broadcasting its live location.',
        );
        
        // Simulating the "2 stops away" notification shortly after
        Future.delayed(const Duration(seconds: 15), () {
          NotificationService.showNotification(
            id: 2,
            title: '📍 Almost There!',
            body: 'The KiddoCab is 2 stops away. Please get ready.',
          );
        });
      },
    ).subscribe();
  }

  @override
  void dispose() {
    _locationsChannel?.unsubscribe();
    super.dispose();
  }

  Widget _buildGlassContainer({required Widget child, double opacity = 0.75, double radius = 24}) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(radius),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
        child: Container(
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(opacity),
            borderRadius: BorderRadius.circular(radius),
            border: Border.all(color: Colors.white.withOpacity(0.2)),
          ),
          child: child,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Scaffold(
      extendBodyBehindAppBar: true,
      body: Stack(
        children: [
          // 1. Full Screen Map
          const GoogleMap(
            initialCameraPosition: CameraPosition(
              target: LatLng(28.6139, 77.2090),
              zoom: 14.0,
            ),
            myLocationEnabled: true,
            zoomControlsEnabled: false,
          ),
          
          // 2. Floating Top Banner
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
              child: _buildGlassContainer(
                opacity: 0.85,
                radius: 20,
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Row(
                    children: [
                      CircleAvatar(
                        radius: 24,
                        backgroundImage: const AssetImage('assets/images/parentimg.png'),
                        backgroundColor: theme.colorScheme.primary.withOpacity(0.1),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Text('Good Morning, Parent', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                            const SizedBox(height: 4),
                            Text(
                              'Driver Michael is 5 mins away',
                              style: TextStyle(color: theme.colorScheme.tertiary, fontWeight: FontWeight.bold),
                            ),
                          ],
                        ),
                      ),
                      IconButton(
                        icon: Icon(Icons.notifications_active, color: theme.colorScheme.secondary),
                        onPressed: () {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Push Notifications Enabled!')),
                          );
                        },
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
          
          // 3. Floating Bottom Panel
          DraggableScrollableSheet(
            initialChildSize: 0.35,
            minChildSize: 0.2,
            maxChildSize: 0.8,
            builder: (BuildContext context, ScrollController scrollController) {
              return _buildGlassContainer(
                opacity: 0.90,
                radius: 32,
                child: ListView(
                  controller: scrollController,
                  padding: const EdgeInsets.all(20.0),
                  children: [
                    // Drag Handle
                    Center(
                      child: Container(
                        width: 40,
                        height: 5,
                        margin: const EdgeInsets.only(bottom: 20),
                        decoration: BoxDecoration(
                          color: Colors.grey[400],
                          borderRadius: BorderRadius.circular(10),
                        ),
                      ),
                    ),
                    
                    // Child Status Card
                    Text(
                      'Live Child Status',
                      style: theme.textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: theme.colorScheme.primary,
                      ),
                    ),
                    const SizedBox(height: 12),
                    Container(
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.5),
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: Colors.white),
                      ),
                      child: ListTile(
                        leading: CircleAvatar(
                          backgroundColor: theme.colorScheme.secondary.withOpacity(0.2),
                          child: Icon(Icons.person, color: theme.colorScheme.secondary),
                        ),
                        title: Text(AuthService.currentChildName ?? 'Emma Smith', style: const TextStyle(fontWeight: FontWeight.bold)),
                        subtitle: const Text('In Transit - Heading to School'),
                        trailing: Chip(
                          label: const Text('Boarded'),
                          backgroundColor: theme.colorScheme.tertiary.withOpacity(0.2),
                          labelStyle: TextStyle(color: theme.colorScheme.tertiary, fontWeight: FontWeight.bold),
                          side: BorderSide.none,
                        ),
                      ),
                    ),
                    
                    const SizedBox(height: 24),
                    
                    // Assign New Cab Button
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton.icon(
                        onPressed: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(builder: (_) => const CabSelectionScreen()),
                          );
                        },
                        icon: const Icon(Icons.search),
                        label: const Text('Find & Assign Another Trip', style: TextStyle(fontSize: 16)),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: theme.colorScheme.secondary,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                          elevation: 0,
                        ),
                      ),
                    ),
                    
                    const SizedBox(height: 16),
                    
                    // Facial Recognition / AI Sensor Banner
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: theme.colorScheme.primary.withOpacity(0.05),
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: theme.colorScheme.primary.withOpacity(0.1)),
                      ),
                      child: Row(
                        children: [
                          Icon(Icons.face, color: theme.colorScheme.primary, size: 32),
                          const SizedBox(width: 16),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text('AI Check-in Active', style: TextStyle(fontWeight: FontWeight.bold, color: theme.colorScheme.primary)),
                                const SizedBox(height: 4),
                                const Text('Facial recognition confirmed boarding at 07:35 AM.', style: TextStyle(fontSize: 12)),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              );
            },
          ),
        ],
      ),
    );
  }
}
