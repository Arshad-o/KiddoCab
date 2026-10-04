import 'package:flutter/material.dart';
import 'parent/parent_login_screen.dart';
import 'admin/admin_dashboard.dart';
import 'parent/parent_register_screen.dart';
import 'driver/driver_login_screen.dart';
import 'driver/driver_register_screen.dart';

class WelcomeScreen extends StatelessWidget {
  const WelcomeScreen({super.key});

  Widget _buildRoleCard(
    BuildContext context, {
    required String title,
    required IconData icon,
    required Color color,
    required VoidCallback onLogin,
    required VoidCallback onRegister,
  }) {
    final theme = Theme.of(context);
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          children: [
            CircleAvatar(
              radius: 40,
              backgroundColor: color.withOpacity(0.1),
              child: Icon(icon, size: 40, color: color),
            ),
            const SizedBox(height: 16),
            Text(
              title,
              style: theme.textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
                color: theme.colorScheme.primary,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton(
                    onPressed: onLogin,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: theme.colorScheme.primary,
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                    child: const Text('Login'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: OutlinedButton(
                    onPressed: onRegister,
                    style: OutlinedButton.styleFrom(
                      foregroundColor: theme.colorScheme.primary,
                      side: BorderSide(color: theme.colorScheme.primary),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                    child: const Text('Register'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      backgroundColor: theme.colorScheme.background,
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  'KiddoCab 🚐✨',
                  textAlign: TextAlign.center,
                  style: theme.textTheme.headlineLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: theme.colorScheme.primary,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Safe and reliable school transport',
                  textAlign: TextAlign.center,
                  style: theme.textTheme.titleMedium?.copyWith(
                    color: Colors.grey[700],
                  ),
                ),
                const SizedBox(height: 48),
                _buildRoleCard(
                  context,
                  title: 'I am a Parent',
                  icon: Icons.family_restroom,
                  color: Colors.blue,
                  onLogin: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => const ParentLoginScreen()),
                    );
                  },
                  onRegister: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => const ParentRegisterScreen()),
                    );
                  },
                ),
                const SizedBox(height: 24),
                _buildRoleCard(
                  context,
                  title: 'I am a Driver',
                  icon: Icons.directions_bus,
                  color: theme.colorScheme.secondary,
                  onLogin: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => const DriverLoginScreen()),
                    );
                  },
                  onRegister: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => const DriverRegisterScreen()),
                    );
                  },
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
