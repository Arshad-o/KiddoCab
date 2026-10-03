import 'package:flutter/material.dart';
import '../../services/auth_service.dart';

class OtpScreen extends StatefulWidget {
  final String email;
  // expectedOtp removed for Supabase Auth
  final VoidCallback onSuccess;

  const OtpScreen({
    super.key,
    required this.email,
    // required this.expectedOtp,
    required this.onSuccess,
  });

  @override
  State<OtpScreen> createState() => _OtpScreenState();
}

class _OtpScreenState extends State<OtpScreen> {
  final _otpController = TextEditingController();

  Future<void> _verifyOtp() async {
    final isValid = await AuthService.verifyOtp(widget.email, _otpController.text.trim());
    if (isValid) {
      widget.onSuccess();
    } else {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Invalid OTP! Please try again.'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(
        title: const Text('OTP Verification'),
        backgroundColor: theme.colorScheme.primary,
        foregroundColor: Colors.white,
      ),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Icon(
              Icons.mark_email_read,
              size: 80,
              color: Colors.green,
            ),
            const SizedBox(height: 24),
            Text(
              'OTP Sent!',
              textAlign: TextAlign.center,
              style: theme.textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
                color: theme.colorScheme.primary,
              ),
            ),
            const SizedBox(height: 12),
            Text(
              'Please enter the OTP sent to:\n${widget.email}',
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 16),
            ),
            const SizedBox(height: 32),
            TextField(
              controller: _otpController,
              decoration: const InputDecoration(
                labelText: 'Enter OTP',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.security),
              ),
              keyboardType: TextInputType.number,
              textAlign: TextAlign.center,
              maxLength: 10,
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: _verifyOtp,
              style: ElevatedButton.styleFrom(
                backgroundColor: theme.colorScheme.primary,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              child: const Text('Verify & Proceed', style: TextStyle(fontSize: 18)),
            ),
            const SizedBox(height: 16),
            TextButton(
              onPressed: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Resending OTP...')),
                );
              },
              child: const Text('Resend OTP'),
            )
          ],
        ),
      ),
    );
  }
}
