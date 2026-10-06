import re

def optimize_frs():
    filepath = 'lib/screens/driver/live_frs_scanner_screen.dart'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Optimize FaceDetectorOptions for maximum recognition reliability
    old_options = """    _faceDetector = FaceDetector(options: FaceDetectorOptions(
      enableContours: true,
      enableLandmarks: true,
      enableClassification: false,
      enableTracking: true,
      performanceMode: FaceDetectorMode.fast,"""
      
    new_options = """    _faceDetector = FaceDetector(options: FaceDetectorOptions(
      enableContours: false,
      enableLandmarks: false,
      enableClassification: false,
      enableTracking: false,
      performanceMode: FaceDetectorMode.fast,"""
    content = content.replace(old_options, new_options)

    # 2. Change image format and resolution to be universally compatible
    old_camera = """      _cameraController = CameraController(
        camera,
        ResolutionPreset.medium, // Medium resolution is better for real-time ML processing speed
        enableAudio: false,
        imageFormatGroup: Platform.isAndroid ? ImageFormatGroup.nv21 : ImageFormatGroup.bgra8888,
      );"""
      
    new_camera = """      _cameraController = CameraController(
        camera,
        ResolutionPreset.high, // Higher resolution helps detection logic
        enableAudio: false,
        imageFormatGroup: Platform.isAndroid ? ImageFormatGroup.yuv420 : ImageFormatGroup.bgra8888,
      );"""
    content = content.replace(old_camera, new_camera)
    
    # 3. Ensure the format parsing explicitly defaults to yuv420 if raw fails
    old_format = """      final inputImageFormat = InputImageFormat.values.firstWhere(
        (f) => f.rawValue == image.format.raw,
        orElse: () => InputImageFormat.nv21,
      );"""
      
    new_format = """      final inputImageFormat = InputImageFormat.values.firstWhere(
        (f) => f.rawValue == image.format.raw,
        orElse: () => Platform.isAndroid ? InputImageFormat.yuv420 : InputImageFormat.bgra8888,
      );"""
    content = content.replace(old_format, new_format)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

optimize_frs()
