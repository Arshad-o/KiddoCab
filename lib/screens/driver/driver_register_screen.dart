import 'package:flutter/material.dart';
import 'dart:io';
import 'package:image_picker/image_picker.dart';
import '../auth/otp_screen.dart';
import '../driver_dashboard.dart';
import '../terms_and_conditions_screen.dart';
import '../../services/auth_service.dart';

class DriverRegisterScreen extends StatefulWidget {
  const DriverRegisterScreen({super.key});

  @override
  State<DriverRegisterScreen> createState() => _DriverRegisterScreenState();
}

class _DriverRegisterScreenState extends State<DriverRegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  
  final _nameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _emailController = TextEditingController();
  
  bool _acceptedTerms = false;
  bool _isLoading = false;

  String _selectedVehicle = 'Auto Rickshaw';
  File? _vehiclePhoto;


  final List<Map<String, dynamic>> _vehicleTypes = [
    {'name': 'Auto Rickshaw', 'image': 'assets/images/autoimg.jpg', 'color': Colors.amber},
    {'name': 'Large Auto', 'image': 'assets/images/big_auto_img.jpg', 'color': Colors.deepOrange},
    {'name': 'Tata Magic', 'image': 'assets/images/tata_magic.png', 'color': Colors.blue},
    {'name': 'Cab', 'image': 'assets/images/cab.avif', 'color': Colors.grey},
  ];

  Future<void> _captureVehiclePhoto() async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: ImageSource.camera, imageQuality: 80);
    if (pickedFile != null) {
      setState(() => _vehiclePhoto = File(pickedFile.path));
    }
  }

  Future<void> _proceed() async {
    if (!_formKey.currentState!.validate()) return;

    if (_vehiclePhoto == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please capture a live photo of your vehicle!'), backgroundColor: Colors.red),
      );
      return;
    }

    if (!_acceptedTerms) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please accept the Terms and Conditions', style: TextStyle(color: Colors.white)), backgroundColor: Colors.red),
      );
      return;
    }

    final email = _emailController.text.trim();
    final phone = _phoneController.text.trim();

    setState(() => _isLoading = true);

    final existingRoleEmail = await AuthService.getUserRole(email);
      final existingRolePhone = await AuthService.getUserRole(phone);
      if (existingRoleEmail != null || existingRolePhone != null) {
        final role = existingRoleEmail ?? existingRolePhone;
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('This email or phone is already registered as a ${role?.toUpperCase()}!'), backgroundColor: Colors.red),
        );
      }
      return;
    }

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Sending OTP...')),
      );
    }

    final success = await AuthService.sendOtp(email);

    setState(() => _isLoading = false);
    if (!mounted) return;

    if (success) {
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => OtpScreen(
            email: email,
            onSuccess: () {
              // Pass the selected vehicle type to the backend
              AuthService.registerUser(
                email, 
                phone, 
                'driver', 
                vehicleType: _selectedVehicle,
              );
              Navigator.pushAndRemoveUntil(
                context,
                MaterialPageRoute(builder: (_) => const DriverDashboard()),
                (route) => false,
              );
            },
          ),
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Failed to send OTP. Please check your email.'), backgroundColor: Colors.red),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('Driver Registration'),
        backgroundColor: theme.colorScheme.secondary,
        foregroundColor: Colors.white,
      ),
      body: _isLoading 
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Form(
          key: _formKey,
          autovalidateMode: AutovalidateMode.onUserInteraction,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Center(
                child: Image.asset(
                  'assets/images/driverimg.webp',
                  height: 100,
                  errorBuilder: (context, error, stackTrace) => const Icon(Icons.drive_eta, size: 80, color: Colors.amber),
                ),
              ),
              const SizedBox(height: 32),
              
              Text('Personal Details', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold, color: theme.colorScheme.secondary)),
              const Divider(),
              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(labelText: 'Full Name *', border: OutlineInputBorder()),
                validator: (value) => value == null || value.isEmpty ? 'Required' : null,
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _phoneController,
                decoration: const InputDecoration(labelText: 'Phone Number *', border: OutlineInputBorder()),
                keyboardType: TextInputType.phone,
                validator: (value) => value == null || value.isEmpty ? 'Required' : null,
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _emailController,
                decoration: const InputDecoration(labelText: 'Email Address *', border: OutlineInputBorder()),
                keyboardType: TextInputType.emailAddress,
                validator: (value) {
                  if (value == null || value.isEmpty) return 'Required';
                  if (!value.contains('@')) return 'Invalid email';
                  return null;
                },
              ),
              const SizedBox(height: 32),
              
              Text('Vehicle Selection', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold, color: theme.colorScheme.secondary)),
              const Text('Select the vehicle type you will be driving. Parents will see this on their app.', style: TextStyle(color: Colors.grey, fontSize: 13)),
              const Divider(),
              
              GridView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 2,
                  crossAxisSpacing: 12,
                  mainAxisSpacing: 12,
                  childAspectRatio: 1.1,
                ),
                itemCount: _vehicleTypes.length,
                itemBuilder: (context, index) {
                  final vehicle = _vehicleTypes[index];
                  final isSelected = _selectedVehicle == vehicle['name'];
                  
                  return GestureDetector(
                    onTap: () {
                      setState(() {
                        _selectedVehicle = vehicle['name'];
                      });
                    },
                    child: Container(
                      decoration: BoxDecoration(
                        color: isSelected ? vehicle['color'].withOpacity(0.1) : Colors.white,
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(
                          color: isSelected ? vehicle['color'] : Colors.grey.withOpacity(0.3),
                          width: isSelected ? 3 : 1,
                        ),
                      ),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Expanded(
                            child: Padding(
                              padding: const EdgeInsets.all(8.0),
                              child: Image.asset(vehicle['image'], fit: BoxFit.contain),
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            vehicle['name'],
                            style: TextStyle(
                              fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                              color: isSelected ? vehicle['color'] : Colors.black87,
                            ),
                          ),
                          if (isSelected)
                            const Padding(
                              padding: EdgeInsets.only(top: 4.0),
                              child: Icon(Icons.check_circle, color: Colors.green, size: 18),
                            )
                        ],
                      ),
                    ),
                  );
                },
              ),

              const SizedBox(height: 24),
              Text('Live Vehicle Photo *', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold, color: theme.colorScheme.secondary)),
              const Text('Capture a clear photo of your actual vehicle showing the license plate.', style: TextStyle(color: Colors.grey, fontSize: 13)),
              const SizedBox(height: 12),
              InkWell(
                onTap: _captureVehiclePhoto,
                child: Container(
                  height: 150,
                  decoration: BoxDecoration(
                    color: Colors.grey[200],
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: Colors.grey.withOpacity(0.5), style: BorderStyle.solid),
                    image: _vehiclePhoto != null ? DecorationImage(image: FileImage(_vehiclePhoto!), fit: BoxFit.cover) : null,
                  ),
                  child: _vehiclePhoto == null 
                      ? const Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.camera_alt, size: 48, color: Colors.grey),
                            SizedBox(height: 8),
                            Text('Tap to Capture Vehicle Photo', style: TextStyle(color: Colors.grey, fontWeight: FontWeight.bold)),
                          ],
                        )
                      : Align(
                          alignment: Alignment.bottomRight,
                          child: Padding(
                            padding: const EdgeInsets.all(8.0),
                            child: CircleAvatar(
                              backgroundColor: Colors.white,
                              child: IconButton(
                                icon: const Icon(Icons.edit, color: Colors.blue),
                                onPressed: _captureVehiclePhoto,
                              ),
                            ),
                          ),
                        ),
                ),
              ),

              const SizedBox(height: 32),
              Row(
                children: [
                  Checkbox(
                    value: _acceptedTerms,
                    onChanged: (val) => setState(() => _acceptedTerms = val ?? false),
                    activeColor: theme.colorScheme.secondary,
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
                  backgroundColor: theme.colorScheme.secondary,
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
