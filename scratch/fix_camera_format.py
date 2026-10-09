import re

def fix_camera_format():
    filepath = 'lib/screens/driver/live_frs_scanner_screen.dart'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    old_camera = """      _cameraController = CameraController(
        camera,
        ResolutionPreset.high, // High resolution for accurate ML Kit Face Detection (Leap app structure)
        enableAudio: false,
        imageFormatGroup: Platform.isAndroid ? ImageFormatGroup.yuv420 : ImageFormatGroup.bgra8888,
      );"""
      
    new_camera = """      _cameraController = CameraController(
        camera,
        ResolutionPreset.high, // High resolution for accurate ML Kit Face Detection
        enableAudio: false,
        imageFormatGroup: Platform.isAndroid ? ImageFormatGroup.nv21 : ImageFormatGroup.bgra8888, // MUST be nv21 for ML Kit Android
      );"""

    content = content.replace(old_camera, new_camera)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

fix_camera_format()
