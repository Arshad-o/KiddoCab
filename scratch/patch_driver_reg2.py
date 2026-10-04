import re

with open('lib/screens/driver/driver_register_screen.dart', 'r', encoding='utf-8') as f:
    code = f.read()

# ADD IMPORTS
if "import 'dart:io';" not in code:
    code = code.replace("import 'package:flutter/material.dart';", "import 'package:flutter/material.dart';\nimport 'dart:io';\nimport 'package:image_picker/image_picker.dart';")

# ADD STATE VAR
state_vars = """  String _selectedVehicle = 'Auto Rickshaw';
  File? _vehiclePhoto;
"""
code = code.replace("  String _selectedVehicle = 'Auto Rickshaw';", state_vars)

# ADD PICKER METHOD
picker_method = """  Future<void> _captureVehiclePhoto() async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: ImageSource.camera, imageQuality: 80);
    if (pickedFile != null) {
      setState(() => _vehiclePhoto = File(pickedFile.path));
    }
  }

  Future<void> _proceed() async {"""
code = code.replace("  Future<void> _proceed() async {", picker_method)

# ADD VALIDATION
val_code = """    if (!_formKey.currentState!.validate()) return;

    if (_vehiclePhoto == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please capture a live photo of your vehicle!'), backgroundColor: Colors.red),
      );
      return;
    }"""
code = code.replace("    if (!_formKey.currentState!.validate()) return;", val_code)

# ADD UI
ui_code = """              ),

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
              Row("""
code = code.replace("              ),\n\n              const SizedBox(height: 32),\n              Row(", ui_code)

with open('lib/screens/driver/driver_register_screen.dart', 'w', encoding='utf-8') as f:
    f.write(code)
