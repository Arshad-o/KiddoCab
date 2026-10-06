import re

def update_live_scanner():
    filepath = 'lib/screens/driver/live_frs_scanner_screen.dart'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    old_success = """          setState(() {
            _isVerified = true;
            _statusMessage = 'Identity Verified!';
          });
          // Stop stream and pop with success
          await _cameraController?.stopImageStream();
          await Future.delayed(const Duration(milliseconds: 1000)); // Let them see the success message
          if (mounted) Navigator.pop(context, true);"""
          
    new_success = """          setState(() {
            _isVerified = true;
            _statusMessage = 'Identity Verified!';
          });
          // Stop stream, take a photo, and pop with success
          await _cameraController?.stopImageStream();
          String? capturedPath;
          try {
            final XFile picture = await _cameraController!.takePicture();
            capturedPath = picture.path;
          } catch (e) {
            print("Could not capture high-res photo: $e");
            capturedPath = "success_no_image";
          }
          await Future.delayed(const Duration(milliseconds: 1000)); // Let them see the success message
          if (mounted) Navigator.pop(context, capturedPath);"""
          
    content = content.replace(old_success, new_success)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def update_driver_dashboard():
    filepath = 'lib/screens/driver_dashboard.dart'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    old_logic = """    // Within Geo-Fence: Run Live ML Kit FRS Scanner
    final verified = await Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => LiveFrsScannerScreen(studentName: studentName)),
    );

    if (verified == true) {"""
    
    new_logic = """    // Within Geo-Fence: Run Live ML Kit FRS Scanner
    final verifiedResult = await Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => LiveFrsScannerScreen(studentName: studentName)),
    );

    if (verifiedResult != null && verifiedResult != false) {"""
    
    content = content.replace(old_logic, new_logic)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def update_parent_register():
    filepath = 'lib/screens/parent/parent_register_screen.dart'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Import scanner
    if "import '../driver/live_frs_scanner_screen.dart';" not in content:
        content = content.replace("import 'package:image_picker/image_picker.dart';", "import 'package:image_picker/image_picker.dart';\nimport '../driver/live_frs_scanner_screen.dart';")

    old_scan = """  Future<void> _scanFrsPhoto(int childIndex) async {
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
  }"""
  
    new_scan = """  Future<void> _scanFrsPhoto(int childIndex) async {
    final childName = _children[childIndex]['name']!.text.trim();
    final resultPath = await Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => LiveFrsScannerScreen(studentName: childName.isNotEmpty ? childName : 'Child ${childIndex + 1}')),
    );
    
    if (resultPath != null && resultPath is String && resultPath != "success_no_image") {
      setState(() {
        _children[childIndex]['frs_photo'] = File(resultPath);
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('FRS Scan completed successfully!', style: TextStyle(color: Colors.white)), backgroundColor: Colors.green),
        );
      }
    }
  }"""
  
    if old_scan in content:
        content = content.replace(old_scan, new_scan)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Updated all files!")
    else:
        # try regex fallback
        pattern = r"Future<void> _scanFrsPhoto\(int childIndex\) async \{[\s\S]*?\}\s*\}"
        if re.search(pattern, content):
            content = re.sub(pattern, new_scan, content)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print("Updated via regex!")
        else:
            print("Failed to find parent scan function.")

update_live_scanner()
update_driver_dashboard()
update_parent_register()
