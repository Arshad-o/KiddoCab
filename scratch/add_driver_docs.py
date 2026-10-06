import re

def update_driver_reg():
    filepath = 'lib/screens/driver/driver_register_screen.dart'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add state variables
    old_vars = "  File? _vehiclePhoto;"
    new_vars = "  File? _vehiclePhoto;\n  File? _rcPhoto;\n  File? _licensePhoto;"
    content = content.replace(old_vars, new_vars)

    # 2. Add capture methods
    old_capture = """  Future<void> _captureVehiclePhoto() async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: ImageSource.camera, imageQuality: 80);
    if (pickedFile != null) {
      setState(() => _vehiclePhoto = File(pickedFile.path));
    }
  }"""
    new_capture = """  Future<void> _captureVehiclePhoto() async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: ImageSource.camera, imageQuality: 80);
    if (pickedFile != null) {
      setState(() => _vehiclePhoto = File(pickedFile.path));
    }
  }

  Future<void> _captureRcPhoto() async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: ImageSource.camera, imageQuality: 80);
    if (pickedFile != null) {
      setState(() => _rcPhoto = File(pickedFile.path));
    }
  }

  Future<void> _captureLicensePhoto() async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: ImageSource.camera, imageQuality: 80);
    if (pickedFile != null) {
      setState(() => _licensePhoto = File(pickedFile.path));
    }
  }"""
    content = content.replace(old_capture, new_capture)

    # 3. Add validation in _proceed
    old_val = """    if (_vehiclePhoto == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please capture a live photo of your vehicle!'), backgroundColor: Colors.red),
      );
      return;
    }"""
    new_val = """    if (_vehiclePhoto == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please capture a live photo of your vehicle!'), backgroundColor: Colors.red),
      );
      return;
    }
    
    if (_rcPhoto == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please capture a photo of the RC document!'), backgroundColor: Colors.red),
      );
      return;
    }
    
    if (_licensePhoto == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please capture a photo of your Driving License!'), backgroundColor: Colors.red),
      );
      return;
    }"""
    content = content.replace(old_val, new_val)

    # 4. Add UI elements below vehicle photo
    # We will search for the end of the vehicle photo block
    
    old_ui = """                const SizedBox(height: 32),
                
                ElevatedButton("""
    
    new_ui = """                const SizedBox(height: 24),
                
                Text('Document Uploads', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold, color: theme.colorScheme.secondary)),
                const Divider(),
                
                // RC Upload
                const Text('Registration Certificate (RC)', style: TextStyle(fontWeight: FontWeight.bold)),
                const Text('Capture a clear photo of the vehicle RC.', style: TextStyle(color: Colors.grey, fontSize: 13)),
                const SizedBox(height: 8),
                InkWell(
                  onTap: _captureRcPhoto,
                  child: Container(
                    height: 150,
                    decoration: BoxDecoration(
                      color: Colors.grey[200],
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: Colors.grey.withOpacity(0.5)),
                      image: _rcPhoto != null ? DecorationImage(image: FileImage(_rcPhoto!), fit: BoxFit.cover) : null,
                    ),
                    child: _rcPhoto == null 
                        ? const Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(Icons.description, size: 40, color: Colors.grey),
                              SizedBox(height: 8),
                              Text('Tap to capture RC', style: TextStyle(color: Colors.grey, fontWeight: FontWeight.bold)),
                            ],
                          )
                        : null,
                  ),
                ),
                
                const SizedBox(height: 16),
                
                // License Upload
                const Text('Driving License', style: TextStyle(fontWeight: FontWeight.bold)),
                const Text('Capture a clear photo of your valid driving license.', style: TextStyle(color: Colors.grey, fontSize: 13)),
                const SizedBox(height: 8),
                InkWell(
                  onTap: _captureLicensePhoto,
                  child: Container(
                    height: 150,
                    decoration: BoxDecoration(
                      color: Colors.grey[200],
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: Colors.grey.withOpacity(0.5)),
                      image: _licensePhoto != null ? DecorationImage(image: FileImage(_licensePhoto!), fit: BoxFit.cover) : null,
                    ),
                    child: _licensePhoto == null 
                        ? const Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(Icons.badge, size: 40, color: Colors.grey),
                              SizedBox(height: 8),
                              Text('Tap to capture License', style: TextStyle(color: Colors.grey, fontWeight: FontWeight.bold)),
                            ],
                          )
                        : null,
                  ),
                ),

                const SizedBox(height: 32),
                
                ElevatedButton("""
    
    if old_ui in content:
        content = content.replace(old_ui, new_ui)
    else:
        print("COULD NOT FIND UI BLOCK TO REPLACE")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

update_driver_reg()
print("Driver RC & License added!")
