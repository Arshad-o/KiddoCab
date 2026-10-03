import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';
import '../auth/otp_screen.dart';
import '../parent_dashboard.dart';
import '../terms_and_conditions_screen.dart';

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
  
  // 2nd Parent
  final _name2Controller = TextEditingController();
  final _phone2Controller = TextEditingController();

  File? _profile1;
  File? _profile2;
  
  String? _location;
  bool _acceptedTerms = false;

  final List<Map<String, TextEditingController>> _children = [
    {
      'name': TextEditingController(),
      'school': TextEditingController(),
    }
  ];


  Future<void> _pickImage(int parentIndex) async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: ImageSource.gallery);
    if (pickedFile != null) {
      setState(() {
        if (parentIndex == 1) _profile1 = File(pickedFile.path);
        else _profile2 = File(pickedFile.path);
      });
    }
  }

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

    if ((await AuthService.checkUserExists(email)) || (await AuthService.checkUserExists(phone))) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('User already exists with this email or phone number!')),
      );
      return;
    }

    
    
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Sending OTP...')),
    );

    final success = await AuthService.sendOtp(email);

    if (!mounted) return;

    if (success) {
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => OtpScreen(
            email: email,
            // expectedOtp removed
            onSuccess: () {
              final firstChildName = _children[0]['name']!.text.trim();
              AuthService.registerUser(email, phone, 'parent', childName: firstChildName);
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
              Center(
                child: Image.asset(
                  'assets/images/parentimg.png',
                  height: 80,
                ),
              ),
              const SizedBox(height: 16),
              TextFormField(
                  controller: _nameController,
                  decoration: const InputDecoration(labelText: 'Parent 1 Name', border: OutlineInputBorder()),
                  validator: (value) => value == null || value.isEmpty ? 'Please enter Parent 1 name' : null,
                ),
                const SizedBox(height: 8),
                ElevatedButton.icon(
                  onPressed: () => _pickImage(1),
                  icon: const Icon(Icons.image),
                  label: Text(_profile1 == null ? 'Upload Parent 1 Photo' : 'Photo Selected'),
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _phoneController,
                  decoration: const InputDecoration(labelText: 'Parent 1 Phone Number', border: OutlineInputBorder()),
                  keyboardType: TextInputType.phone,
                  validator: (value) => value == null || value.isEmpty ? 'Please enter Parent 1 phone' : null,
                ),
                const SizedBox(height: 24),
                const Divider(),
                const Text('Parent 2 (Optional)', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                const SizedBox(height: 8),
                TextFormField(
                  controller: _name2Controller,
                  decoration: const InputDecoration(labelText: 'Parent 2 Name', border: OutlineInputBorder()),
                ),
                const SizedBox(height: 8),
                ElevatedButton.icon(
                  onPressed: () => _pickImage(2),
                  icon: const Icon(Icons.image),
                  label: Text(_profile2 == null ? 'Upload Parent 2 Photo' : 'Photo Selected'),
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _phone2Controller,
                  decoration: const InputDecoration(labelText: 'Parent 2 Phone Number', border: OutlineInputBorder()),
                  keyboardType: TextInputType.phone,
                ),
                const SizedBox(height: 24),
                const Divider(),
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
                onPressed: () async {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Requesting GPS permissions & fetching location...')),
                  );
                  
                  try {
                    bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
                    if (!serviceEnabled) {
                      throw Exception('Location services are disabled.');
                    }

                    LocationPermission permission = await Geolocator.checkPermission();
                    if (permission == LocationPermission.denied) {
                      permission = await Geolocator.requestPermission();
                      if (permission == LocationPermission.denied) {
                        throw Exception('Location permissions are denied');
                      }
                    }
                    
                    if (permission == LocationPermission.deniedForever) {
                      throw Exception('Location permissions are permanently denied.');
                    } 

                    final position = await Geolocator.getCurrentPosition();
                    
                    setState(() {
                      _location = 'Lat: ${position.latitude.toStringAsFixed(4)}, Lng: ${position.longitude.toStringAsFixed(4)}';
                    });
                    
                    if (context.mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Real location fetched successfully!')),
                      );
                    }
                  } catch (e) {
                    if (context.mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text('Failed to get location: $e')),
                      );
                    }
                  }
                },
                icon: const Icon(Icons.my_location),
                label: const Text('Fix Geo Location (Automated)'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: theme.colorScheme.tertiary,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
              ),
              if (_location != null) ...[
                const SizedBox(height: 8),
                Text(
                  'Saved Location: $_location',
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: Colors.green[700],
                    fontWeight: FontWeight.bold,
                  ),
                  textAlign: TextAlign.center,
                ),
              ],
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
              Row(
                children: [
                  Checkbox(
                    value: _acceptedTerms,
                    onChanged: (val) {
                      setState(() {
                        _acceptedTerms = val ?? false;
                      });
                    },
                  ),
                  Expanded(
                    child: GestureDetector(
                      onTap: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(builder: (_) => const TermsAndConditionsScreen()),
                        );
                      },
                      child: Text(
                        'I agree to the Terms and Conditions',
                        style: TextStyle(
                          color: theme.colorScheme.primary,
                          decoration: TextDecoration.underline,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ),
                ],
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
