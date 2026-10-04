import re

with open('lib/screens/parent_dashboard.dart', 'r', encoding='utf-8') as f:
    code = f.read()

# Add a RealtimeChannel for alerts
state_vars = """  RealtimeChannel? _locationsChannel;
  RealtimeChannel? _alertsChannel;"""

code = code.replace("  RealtimeChannel? _locationsChannel;", state_vars)

# Add listener in initState
init_state_old = """  @override
  void initState() {
    super.initState();
    _listenToDriverStatus();
    _determinePosition();
  }"""

init_state_new = """  @override
  void initState() {
    super.initState();
    _listenToDriverStatus();
    _listenToSecurityAlerts();
    _determinePosition();
  }

  void _listenToSecurityAlerts() {
    _alertsChannel = _supabase.channel('public:alerts').onPostgresChanges(
      event: PostgresChangeEvent.insert,
      schema: 'public',
      table: 'alerts',
      callback: (payload) {
        final newRecord = payload.newRecord;
        
        // If the alert is for THIS parent's child
        if (newRecord['child_name'] == (AuthService.currentChildName ?? 'Emma Smith')) {
          // Trigger high-priority mobile push notification
          NotificationService.showNotification(
            id: 999,
            title: '🚨 SECURITY ALERT',
            body: newRecord['message'] ?? 'Driver missed the FRS scan for your child!',
          );
          
          // Also show a massive red dialog on screen if app is open
          if (mounted) {
            showDialog(
              context: context,
              barrierDismissible: false,
              builder: (ctx) => AlertDialog(
                backgroundColor: Colors.red[900],
                title: const Row(children: [Icon(Icons.warning_amber, color: Colors.white, size: 32), SizedBox(width: 8), Text('CRITICAL ALERT', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold))]),
                content: Text(
                  newRecord['message'] ?? 'The driver has left the Geo-fence without scanning your childs face via FRS! Please contact the driver immediately.',
                  style: const TextStyle(color: Colors.white, fontSize: 16),
                ),
                actions: [
                  ElevatedButton(
                    onPressed: () => Navigator.pop(ctx),
                    style: ElevatedButton.styleFrom(backgroundColor: Colors.white, foregroundColor: Colors.red[900]),
                    child: const Text('Dismiss & Call Driver'),
                  )
                ],
              )
            );
          }
        }
      },
    ).subscribe();
  }"""

code = code.replace(init_state_old, init_state_new)

# Add unsubscribe
dispose_old = """  @override
  void dispose() {
    _locationsChannel?.unsubscribe();
    super.dispose();
  }"""

dispose_new = """  @override
  void dispose() {
    _locationsChannel?.unsubscribe();
    _alertsChannel?.unsubscribe();
    super.dispose();
  }"""

code = code.replace(dispose_old, dispose_new)

with open('lib/screens/parent_dashboard.dart', 'w', encoding='utf-8') as f:
    f.write(code)
