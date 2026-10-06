import re

def update_driver_dashboard():
    filepath = 'lib/screens/driver_dashboard.dart'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Import the new screen
    if "import 'driver/live_frs_scanner_screen.dart';" not in content:
        content = content.replace("import 'package:image_picker/image_picker.dart';", "import 'package:image_picker/image_picker.dart';\nimport 'driver/live_frs_scanner_screen.dart';")

    old_logic = """    // Within Geo-Fence: Run Camera
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: ImageSource.camera, preferredCameraDevice: CameraDevice.front);
    if (pickedFile != null) {"""

    new_logic = """    // Within Geo-Fence: Run Live ML Kit FRS Scanner
    final verified = await Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => LiveFrsScannerScreen(studentName: studentName)),
    );

    if (verified == true) {"""

    content = content.replace(old_logic, new_logic)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        
update_driver_dashboard()
