import re

with open('lib/screens/parent/parent_register_screen.dart', 'r', encoding='utf-8') as f:
    content = f.read()

# Add image picker import
content = content.replace("import 'package:geolocator/geolocator.dart';", "import 'package:geolocator/geolocator.dart';\nimport 'package:image_picker/image_picker.dart';\nimport 'dart:io';")

# Add controllers and variables
state_vars = """
  final _nameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _addressController = TextEditingController();
  final _emailController = TextEditingController();
  
  // 2nd Parent
  final _name2Controller = TextEditingController();
  final _phone2Controller = TextEditingController();

  File? _profile1;
  File? _profile2;
"""
content = re.sub(r'final _nameController = TextEditingController\(\);[\s\S]*?final _emailController = TextEditingController\(\);', state_vars.strip(), content)

pick_image_fn = """
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
"""
content = content.replace("  void _addChild() {", pick_image_fn)


parent2_fields = """
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
"""

content = re.sub(
    r"TextFormField\(\s*controller: _nameController,[\s\S]*?TextFormField\(\s*controller: _phoneController,[\s\S]*?validator: .*?,\s*\),",
    parent2_fields.strip(),
    content, count=1
)

with open('lib/screens/parent/parent_register_screen.dart', 'w', encoding='utf-8') as f:
    f.write(content)
