import re

def fix_ml_feed():
    filepath = 'lib/screens/driver/live_frs_scanner_screen.dart'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Change Resolution and Format Group
    old_camera = """      _cameraController = CameraController(
        camera,
        ResolutionPreset.high, // Higher resolution helps detection logic
        enableAudio: false,
        imageFormatGroup: Platform.isAndroid ? ImageFormatGroup.yuv420 : ImageFormatGroup.bgra8888,
      );"""
      
    new_camera = """      _cameraController = CameraController(
        camera,
        ResolutionPreset.low, // Low resolution is crucial on Android to prevent YUV byte stride corruption
        enableAudio: false,
        imageFormatGroup: Platform.isAndroid ? ImageFormatGroup.nv21 : ImageFormatGroup.bgra8888,
      );"""
    content = content.replace(old_camera, new_camera)
    
    # Force NV21 parsing on Android
    old_format = """      final inputImageFormat = InputImageFormat.values.firstWhere(
        (f) => f.rawValue == image.format.raw,
        orElse: () => Platform.isAndroid ? InputImageFormat.yuv420 : InputImageFormat.bgra8888,
      );"""
      
    new_format = """      final inputImageFormat = Platform.isAndroid ? InputImageFormat.nv21 : InputImageFormat.bgra8888;"""
    content = content.replace(old_format, new_format)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

fix_ml_feed()
