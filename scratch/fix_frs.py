import re

def fix_frs_scanner():
    filepath = 'lib/screens/driver/live_frs_scanner_screen.dart'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Change Camera Initialization
    old_camera = """      _cameraController = CameraController(
        camera,
        ResolutionPreset.low, // Low resolution is crucial on Android to prevent YUV byte stride corruption
        enableAudio: false,
        imageFormatGroup: Platform.isAndroid ? ImageFormatGroup.nv21 : ImageFormatGroup.bgra8888,
      );"""
    
    new_camera = """      _cameraController = CameraController(
        camera,
        ResolutionPreset.high, // High resolution for accurate ML Kit Face Detection (Leap app structure)
        enableAudio: false,
        imageFormatGroup: Platform.isAndroid ? ImageFormatGroup.yuv420 : ImageFormatGroup.bgra8888,
      );"""
      
    if "ResolutionPreset.low" in content:
        content = content.replace(old_camera, new_camera)
        
    # 2. Fix the image rotation and formats
    old_process = """      final inputImageData = InputImageMetadata(
        size: imageSize,
        rotation: imageRotation,
        format: inputImageFormat,
        bytesPerRow: image.planes.first.bytesPerRow,
      );"""
      
    # Leap app rotation logic handles specific Android quirks
    new_process = """      // Leap app structure for accurate orientation
      final sensorOrientation = camera.sensorOrientation;
      InputImageRotation? rotation;
      if (Platform.isIOS) {
        rotation = InputImageRotation.values.firstWhere(
          (r) => r.rawValue == sensorOrientation,
          orElse: () => InputImageRotation.rotation0deg,
        );
      } else if (Platform.isAndroid) {
        var rotationCompensation = sensorOrientation;
        if (camera.lensDirection == CameraLensDirection.front) {
          // front-facing
          rotationCompensation = (sensorOrientation + 0) % 360;
        } else {
          // back-facing
          rotationCompensation = (sensorOrientation - 0 + 360) % 360;
        }
        rotation = InputImageRotation.values.firstWhere(
          (r) => r.rawValue == rotationCompensation,
          orElse: () => InputImageRotation.rotation0deg,
        );
      }
      
      final inputImageData = InputImageMetadata(
        size: imageSize,
        rotation: rotation ?? InputImageRotation.rotation0deg,
        format: inputImageFormat,
        bytesPerRow: image.planes.first.bytesPerRow,
      );"""
      
    # Replace rotation logic
    if "final inputImageData = InputImageMetadata(" in content:
        content = re.sub(
            r'(\s*final inputImageData = InputImageMetadata\([\s\S]*?bytesPerRow: image\.planes\.first\.bytesPerRow,\n\s*\);)',
            new_process,
            content
        )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

fix_frs_scanner()
