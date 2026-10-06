import 'package:flutter/material.dart';
import 'location_picker_screen.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:geolocator/geolocator.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';

import '../parent_dashboard.dart';
import '../terms_and_conditions_screen.dart';
import '../../services/auth_service.dart';
import '../auth/otp_screen.dart';

class ParentRegisterScreen extends StatefulWidget {
  const ParentRegisterScreen({super.key});

  @override
  State<ParentRegisterScreen> createState() => _ParentRegisterScreenState();
}

class _ParentRegisterScreenState extends State<ParentRegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  
  // Parent 1
  final _nameController = TextEditingController();
  final _phoneController = TextEditingController();
  File? _profile1;

  // Parent 2
  final _name2Controller = TextEditingController();
  final _phone2Controller = TextEditingController();
  File? _profile2;

  // Common
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _rePasswordController = TextEditingController();
  String _gender = 'male';
  String? _location;
  String? _dropLocation;
  bool _acceptedTerms = false;
  bool _isLoading = false;

  // Children
  final List<Map<String, dynamic>> _children = [
    {
      'name': TextEditingController(),
      'school': TextEditingController(),
      'frs_photo': null,
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

  Future<void> _scanFrsPhoto(int childIndex) async {
    final picker = ImagePicker();
    // Using camera for live FRS scan
    final pickedFile = await picker.pickImage(
      source: ImageSource.camera, 
      preferredCameraDevice: CameraDevice.front,
      imageQuality: 80,
    );
    if (pickedFile != null) {
      setState(() {
        _children[childIndex]['frs_photo'] = File(pickedFile.path);
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('FRS Scan completed successfully!', style: TextStyle(color: Colors.white)), backgroundColor: Colors.green),
        );
      }
    }
  }

  void _addChild() {
    setState(() {
      _children.add({
        'name': TextEditingController(),
        'school': TextEditingController(),
        'frs_photo': null,
      });
    });
  }

  void _removeChild(int index) {
    if (_children.length > 1) {
      setState(() {
        _children.removeAt(index);
      });
    }
  }

  Future<void> _proceed() async {
    if (!_formKey.currentState!.validate()) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please fill all highlighted fields in red'), backgroundColor: Colors.red),
      );
      return;
    }

    if (_location == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please set your precise pick-up location!'), backgroundColor: Colors.red),
      );
      return;
    }

    if (_dropLocation == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please set your precise drop-off (School) location!'), backgroundColor: Colors.red),
      );
      return;
    }

    if (!_acceptedTerms) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please accept the Terms and Conditions'), backgroundColor: Colors.red),
      );
      return;
    }

    // Verify all children have FRS scans
    for (int i = 0; i < _children.length; i++) {
      if (_children[i]['frs_photo'] == null) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Please complete the FRS Scan for Child ${i + 1}'), backgroundColor: Colors.red),
        );
        return;
      }
    }

    setState(() => _isLoading = true);

    final email = _emailController.text.trim();
    final phone = _phoneController.text.trim();

    // Check if user already exists
    final existingRoleEmail = await AuthService.getUserRole(email);
    if (existingRoleEmail != null) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('This EMAIL is already registered as a ${existingRoleEmail.toUpperCase()}!'),
            backgroundColor: Colors.red,
            duration: const Duration(seconds: 4),
          ),
        );
      }
      return;
    }

    final existingRolePhone = await AuthService.getUserRole(phone);
    if (existingRolePhone != null) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('This PHONE NUMBER is already registered as a ${existingRolePhone.toUpperCase()}!'),
            backgroundColor: Colors.red,
            duration: const Duration(seconds: 4),
          ),
        );
      }
      return;
    }

    final password = _passwordController.text.trim();
    final rePassword = _rePasswordController.text.trim();
    if (password != rePassword) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Passwords do not match!'), backgroundColor: Colors.red));
      }
      return;
    }

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Creating Account...')));
    }

    final errorMessage = await AuthService.registerUserWithPassword(email, password, phone, 'parent', _gender, childName: _children[0]['name']!.text.trim());

    setState(() => _isLoading = false);
    if (!mounted) return;

    if (errorMessage == null) {
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => OtpScreen(
            email: email,
            onSuccess: () {
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
        SnackBar(content: Text('Registration Failed: $errorMessage'), backgroundColor: Colors.red, duration: const Duration(seconds: 5)),
      );
    }
  }

  Widget _buildPhotoPicker(String label, File? photo, VoidCallback onPick) {
    return Column(
      children: [
        CircleAvatar(
          radius: 40,
          backgroundColor: Colors.grey[200],
          backgroundImage: photo != null ? FileImage(photo) : null,
          child: photo == null ? const Icon(Icons.person, size: 40, color: Colors.grey) : null,
        ),
        const SizedBox(height: 8),
        TextButton.icon(
          onPressed: onPick,
          icon: const Icon(Icons.camera_alt),
          label: Text(label),
        )
      ],
    );
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
      body: _isLoading 
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          autovalidateMode: AutovalidateMode.onUserInteraction, // Highlights red on error
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Center(
                child: Image.asset('assets/images/parentimg.png', height: 80),
              ),
              const SizedBox(height: 24),
              
              // Parent 1 Section
              Text('Parent 1 Details', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold, color: theme.colorScheme.primary)),
              const Divider(),
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    child: Column(
                      children: [
                        TextFormField(
                          controller: _nameController,
                          decoration: const InputDecoration(labelText: 'Name *', border: OutlineInputBorder()),
                          validator: (value) => value == null || value.isEmpty ? 'Required' : null,
                        ),
                        const SizedBox(height: 12),
                        TextFormField(
                          controller: _phoneController,
                          decoration: const InputDecoration(labelText: 'Phone *', border: OutlineInputBorder()),
                          keyboardType: TextInputType.phone,
                          validator: (value) => value == null || value.isEmpty ? 'Required' : null,
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 16),
                  _buildPhotoPicker('Add Photo', _profile1, () => _pickImage(1)),
                ],
              ),
              
              const SizedBox(height: 24),
              
              // Parent 2 Section
              Text('Parent 2 Details', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold, color: theme.colorScheme.primary)),
              const Divider(),
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    child: Column(
                      children: [
                        TextFormField(
                          controller: _name2Controller,
                          decoration: const InputDecoration(labelText: 'Name (Optional)', border: OutlineInputBorder()),
                        ),
                        const SizedBox(height: 12),
                        TextFormField(
                          controller: _phone2Controller,
                          decoration: const InputDecoration(labelText: 'Phone (Optional)', border: OutlineInputBorder()),
                          keyboardType: TextInputType.phone,
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 16),
                  _buildPhotoPicker('Add Photo', _profile2, () => _pickImage(2)),
                ],
              ),
              
              const SizedBox(height: 24),
              
              // Common Details
              Text('Account Details', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold, color: theme.colorScheme.primary)),
              const Divider(),
              TextFormField(
                controller: _emailController,
                decoration: const InputDecoration(labelText: 'Email Address *', border: OutlineInputBorder()),
                keyboardType: TextInputType.emailAddress,
                validator: (value) {
                  if (value == null || value.isEmpty) return 'Email is required';
                  if (!value.contains('@')) return 'Enter a valid email';
                  return null;
                },
              ),
              
              const SizedBox(height: 16),
              ElevatedButton.icon(
                onPressed: () async {
                  final LatLng? selectedLocation = await Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => const LocationPickerScreen()),
                  );
                  if (selectedLocation != null) {
                    setState(() {
                      _location = 'Lat: ${selectedLocation.latitude.toStringAsFixed(4)}, Lng: ${selectedLocation.longitude.toStringAsFixed(4)}';
                    });
                  }
                },
                icon: const Icon(Icons.map),
                label: const Text('Set Precise Pick-up Location *'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: _location == null ? theme.colorScheme.tertiary : Colors.green,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
              ),
              if (_location != null) ...[
                const SizedBox(height: 8),
                Text('Pick-up Location Saved!', style: theme.textTheme.bodyMedium?.copyWith(color: Colors.green, fontWeight: FontWeight.bold), textAlign: TextAlign.center),
              ],
              
              const SizedBox(height: 16),
              ElevatedButton.icon(
                onPressed: () async {
                  final LatLng? selectedLocation = await Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => const LocationPickerScreen()),
                  );
                  if (selectedLocation != null) {
                    setState(() {
                      _dropLocation = 'Lat: ${selectedLocation.latitude.toStringAsFixed(4)}, Lng: ${selectedLocation.longitude.toStringAsFixed(4)}';
                    });
                  }
                },
                icon: const Icon(Icons.school),
                label: const Text('Set Precise Drop-off (School) *'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: _dropLocation == null ? theme.colorScheme.tertiary : Colors.green,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
              ),
              if (_dropLocation != null) ...[
                const SizedBox(height: 8),
                Text('Drop-off Location Saved!', style: theme.textTheme.bodyMedium?.copyWith(color: Colors.green, fontWeight: FontWeight.bold), textAlign: TextAlign.center),
              ],
              
              const SizedBox(height: 24),

              // Children Section
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('Children Details', style: theme.textTheme.titleLarge?.copyWith(color: theme.colorScheme.primary, fontWeight: FontWeight.bold)),
                  IconButton(
                    onPressed: _addChild,
                    icon: const Icon(Icons.add_circle, color: Colors.green, size: 32),
                    tooltip: 'Add Child',
                  )
                ],
              ),
              const Divider(),
              ..._children.asMap().entries.map((entry) {
                int idx = entry.key;
                var child = entry.value;
                bool hasPhoto = child['frs_photo'] != null;

                return Card(
                  margin: const EdgeInsets.only(bottom: 16),
                  elevation: 2,
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text('Child ${idx + 1}', style: const TextStyle(fontWeight: FontWeight.bold)),
                            if (idx > 0)
                              IconButton(
                                icon: const Icon(Icons.delete, color: Colors.red),
                                onPressed: () => _removeChild(idx),
                              )
                          ],
                        ),
                        const SizedBox(height: 8),
                        TextFormField(
                          controller: child['name'],
                          decoration: const InputDecoration(labelText: 'Child Name *', border: OutlineInputBorder()),
                          validator: (value) => value == null || value.isEmpty ? 'Required' : null,
                        ),
                        const SizedBox(height: 12),
                        TextFormField(
                          controller: child['school'],
                          decoration: const InputDecoration(labelText: 'School Name *', border: OutlineInputBorder()),
                          validator: (value) => value == null || value.isEmpty ? 'Required' : null,
                        ),
                        const SizedBox(height: 16),
                        
                        // FRS Scan Button
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton.icon(
                            onPressed: () => _scanFrsPhoto(idx),
                            icon: Icon(hasPhoto ? Icons.check_circle : Icons.face_retouching_natural),
                            label: Text(hasPhoto ? 'FRS Scan Complete' : 'Live FRS Scan *'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: hasPhoto ? Colors.green : Colors.blueAccent,
                              foregroundColor: Colors.white,
                              padding: const EdgeInsets.symmetric(vertical: 16),
                            ),
                          ),
                        ),
                        if (!hasPhoto)
                          const Padding(
                            padding: EdgeInsets.only(top: 8.0),
                            child: Text('Live FRS face scan is required for future security/recognition.', style: TextStyle(fontSize: 12, color: Colors.red)),
                          ),
                      ],
                    ),
                  ),
                );
              }),

              
              const SizedBox(height: 24),
              Text('Gender', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold, color: theme.colorScheme.primary)),
                              Column(
                  children: [
                    RadioListTile<String>(
                      title: const Text('Male'),
                      value: 'male',
                      groupValue: _gender,
                      onChanged: (value) => setState(() => _gender = value!),
                      secondary: Image.asset('assets/images/male.jpg', width: 40, height: 40),
                    ),
                    RadioListTile<String>(
                      title: const Text('Female'),
                      value: 'female',
                      groupValue: _gender,
                      onChanged: (value) => setState(() => _gender = value!),
                      secondary: Image.asset('assets/images/female.jpg', width: 40, height: 40),
                    ),
                  ],
                ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _passwordController,
                decoration: const InputDecoration(labelText: 'Password *', border: OutlineInputBorder()),
                obscureText: true,
                validator: (value) => value == null || value.length < 6 ? 'Password must be at least 6 characters' : null,
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _rePasswordController,
                decoration: const InputDecoration(labelText: 'Re-enter Password *', border: OutlineInputBorder()),
                obscureText: true,
                validator: (value) => value == null || value.isEmpty ? 'Required' : null,
              ),
              const SizedBox(height: 24),
              Row(
                children: [
                  Checkbox(
                    value: _acceptedTerms,
                    onChanged: (val) => setState(() => _acceptedTerms = val ?? false),
                  ),
                  Expanded(
                    child: GestureDetector(
                      onTap: () {
                        Navigator.push(context, MaterialPageRoute(builder: (_) => const TermsAndConditionsScreen()));
                      },
                      child: const Text('I accept the Terms and Conditions', style: TextStyle(decoration: TextDecoration.underline, color: Colors.blue)),
                    ),
                  )
                ],
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: _proceed,
                style: ElevatedButton.styleFrom(
                  backgroundColor: theme.colorScheme.primary,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                child: const Text('Register & Verify', style: TextStyle(fontSize: 18)),
              ),
              const SizedBox(height: 32),
            ],
          ),
        ),
      ),
    );
  }
}
