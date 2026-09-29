import 'package:flutter/material.dart';
import '../auth/otp_screen.dart';
import '../parent_dashboard.dart';
import '../../services/email_service.dart';
import '../../services/auth_service.dart';

class ParentRegisterScreen extends StatefulWidget {
  const ParentRegisterScreen({super.key});

  @override
  State<ParentRegisterScreen> createState() => _ParentRegisterScreenState();
}

class _ParentRegisterScreenState extends State<ParentRegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  
  final _nameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _addressController = TextEditingController();
  final _emailController = TextEditingController();
  
  bool _acceptedTerms = false;

  final List<Map<String, TextEditingController>> _children = [
    {
      'name': TextEditingController(),
      'school': TextEditingController(),
    }
  ];

  void _addChild() {
    setState(() {
      _children.add({
        'name': TextEditingController(),
        'school': TextEditingController(),
      });
    });
  }

  Future<void> _proceed() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    if (!_acceptedTerms) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please accept the Terms and Conditions')),
      );
      return;
    }

    final email = _emailController.text.trim();
    final phone = _phoneController.text.trim();

    if (AuthService.checkUserExists(email) || AuthService.checkUserExists(phone)) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('User already exists with this email or phone number!')),
      );
      return;
    }

    final otp = EmailService.generateOTP();
    
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Sending OTP...')),
    );

    final success = await EmailService.sendOTP(email, otp);

    if (!mounted) return;

    if (success) {
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => OtpScreen(
            email: email,
            expectedOtp: otp,
            onSuccess: () {
              AuthService.registerUser(email, phone);
              Navigator.pushAndRemoveUntil(
                context,
                MaterialPageRoute(builder: (_) => const ParentDashboard()),
                (route) => false,
              );
            },
          ),
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Failed to send OTP. Please check your email or try again.')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(
        title: const Text('Parent Registration'),
        backgroundColor: theme.colorScheme.primary,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(
                  labelText: 'Parent Name',
                  border: OutlineInputBorder(),
                ),
                validator: (value) => value == null || value.isEmpty ? 'Please enter your name' : null,
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _phoneController,
                decoration: const InputDecoration(
                  labelText: 'Phone Number',
                  border: OutlineInputBorder(),
                ),
                keyboardType: TextInputType.phone,
                validator: (value) => value == null || value.isEmpty ? 'Please enter your phone number' : null,
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _addressController,
                decoration: const InputDecoration(
                  labelText: 'Address',
                  border: OutlineInputBorder(),
                ),
                validator: (value) => value == null || value.isEmpty ? 'Please enter your address' : null,
              ),
              const SizedBox(height: 16),
              ElevatedButton.icon(
                onPressed: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Fetching live location...')),
                  );
                },
                icon: const Icon(Icons.my_location),
                label: const Text('Fix Geo Location (Automated)'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: theme.colorScheme.tertiary,
                  foregroundColor: Colors.white,
                ),
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _emailController,
                decoration: const InputDecoration(
                  labelText: 'Email',
                  border: OutlineInputBorder(),
                ),
                keyboardType: TextInputType.emailAddress,
                validator: (value) {
                  if (value == null || value.isEmpty) return 'Please enter your email';
                  if (!value.contains('@')) return 'Please enter a valid email';
                  return null;
                },
              ),
              const SizedBox(height: 24),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Children Details',
                    style: theme.textTheme.titleLarge?.copyWith(
                      color: theme.colorScheme.primary,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  IconButton(
                    onPressed: _addChild,
                    icon: const Icon(Icons.add_circle, size: 32),
                    color: theme.colorScheme.secondary,
                  ),
                ],
              ),
              const SizedBox(height: 8),
              ..._children.asMap().entries.map((entry) {
                int idx = entry.key;
                var child = entry.value;
                return Card(
                  margin: const EdgeInsets.only(bottom: 16),
                  child: Padding(
                    padding: const EdgeInsets.all(12.0),
                    child: Column(
                      children: [
                        Text('Child ${idx + 1}', style: const TextStyle(fontWeight: FontWeight.bold)),
                        const SizedBox(height: 8),
                        TextFormField(
                          controller: child['name'],
                          decoration: const InputDecoration(
                            labelText: 'Child Name',
                            border: OutlineInputBorder(),
                          ),
                          validator: (value) => value == null || value.isEmpty ? 'Please enter child name' : null,
                        ),
                        const SizedBox(height: 8),
                        TextFormField(
                          controller: child['school'],
                          decoration: const InputDecoration(
                            labelText: 'School Name',
                            border: OutlineInputBorder(),
                          ),
                          validator: (value) => value == null || value.isEmpty ? 'Please enter school name' : null,
                        ),
                      ],
                    ),
                  ),
                );
              }).toList(),
              const SizedBox(height: 16),
              CheckboxListTile(
                value: _acceptedTerms,
                onChanged: (val) {
                  setState(() {
                    _acceptedTerms = val ?? false;
                  });
                },
                title: const Text('I agree to the Terms and Conditions'),
                controlAffinity: ListTileControlAffinity.leading,
                contentPadding: EdgeInsets.zero,
              ),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: _proceed,
                style: ElevatedButton.styleFrom(
                  backgroundColor: theme.colorScheme.primary,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: const Text('Proceed', style: TextStyle(fontSize: 18)),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
