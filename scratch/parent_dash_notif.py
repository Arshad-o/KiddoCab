import re

with open('lib/screens/parent_dashboard.dart', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("class ParentDashboard extends StatelessWidget {", """import 'package:supabase_flutter/supabase_flutter.dart';
import '../services/notification_service.dart';

class ParentDashboard extends StatefulWidget {
  const ParentDashboard({super.key});
  
  @override
  State<ParentDashboard> createState() => _ParentDashboardState();
}

class _ParentDashboardState extends State<ParentDashboard> {""")

content = content.replace("  const ParentDashboard({super.key});\n", "")

init_state = """  final _supabase = Supabase.instance.client;
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
"""

content = content.replace("Widget _buildGlassContainer", init_state + "\n  Widget _buildGlassContainer")

with open('lib/screens/parent_dashboard.dart', 'w', encoding='utf-8') as f:
    f.write(content)
