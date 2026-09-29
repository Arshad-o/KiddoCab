import 'package:flutter/material.dart';

class TermsAndConditionsScreen extends StatelessWidget {
  const TermsAndConditionsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Terms and Conditions'),
        backgroundColor: Theme.of(context).colorScheme.primary,
        foregroundColor: Colors.white,
      ),
      body: const SingleChildScrollView(
        padding: EdgeInsets.all(24.0),
        child: Text(
          'Welcome to KiddoCab!\n\n'
          'By using this application, you agree to the following terms:\n\n'
          '1. Safety and Security\n'
          'All drivers and parents must ensure the safety of children during transit. GPS tracking is provided for peace of mind but should not be solely relied upon in emergency situations.\n\n'
          '2. Privacy\n'
          'We collect location data and personal details strictly for the purpose of facilitating school transport. We do not sell your data to third parties.\n\n'
          '3. Driver Responsibilities\n'
          'Drivers must maintain valid licenses, follow traffic rules, and ensure their vehicles are safe and registered.\n\n'
          '4. Parent Responsibilities\n'
          'Parents must ensure children are ready at the designated pickup locations on time.\n\n'
          '5. Liability\n'
          'KiddoCab acts as a technology platform and is not liable for indirect damages or delays caused by traffic or unforeseen circumstances.\n\n'
          'If you have any questions, please contact kiddocabspace@gmail.com.',
          style: TextStyle(fontSize: 16, height: 1.6),
        ),
      ),
    );
  }
}
