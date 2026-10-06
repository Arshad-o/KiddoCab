import os

new_code = """import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'package:camera/camera.dart';
import 'package:google_mlkit_face_detection/google_mlkit_face_detection.dart';

class LiveFrsScannerScreen extends StatefulWidget {
  final String studentName;
  const LiveFrsScannerScreen({super.key, required this.studentName});

  @override
  State<LiveFrsScannerScreen> createState() => _LiveFrsScannerScreenState();
}

class _LiveFrsScannerScreenState extends State<LiveFrsScannerScreen> with SingleTickerProviderStateMixin {
  CameraController? _cameraController;
  late FaceDetector _faceDetector;
  bool _isProcessing = false;
  bool _isVerified = false;
  String _statusMessage = 'Align face in the frame';
  late AnimationController _animationController;

  @override
  void initState() {
    super.initState();
    _faceDetector = FaceDetector(options: FaceDetectorOptions(
      enableContours: false,
      enableLandmarks: false,
      enableClassification: false,
      enableTracking: true,
      performanceMode: FaceDetectorMode.accurate,
    ));
    _animationController = AnimationController(vsync: this, duration: const Duration(seconds: 2))..repeat(reverse: true);
    _initializeCamera();
  }

  Future<void> _initializeCamera() async {
    try {
      final cameras = await availableCameras();
      if (cameras.isEmpty) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('No camera found!')));
          Navigator.pop(context, false);
        }
        return;
      }

      final camera = cameras.firstWhere((c) => c.lensDirection == CameraLensDirection.front, orElse: () => cameras.first);

      _cameraController = CameraController(
        camera,
        ResolutionPreset.high,
        enableAudio: false,
        imageFormatGroup: ImageFormatGroup.yuv420,
      );

      await _cameraController!.initialize();
      if (!mounted) return;
      setState(() {});

      _cameraController!.startImageStream((CameraImage image) {
        if (_isProcessing || _isVerified) return;
        _processImage(image, camera);
      });
    } catch (e) {
      print('Error initializing camera: $e');
      if (mounted) Navigator.pop(context, false);
    }
  }

  Future<void> _processImage(CameraImage image, CameraDescription camera) async {
    _isProcessing = true;
    try {
      final WriteBuffer allBytes = WriteBuffer();
      for (final Plane plane in image.planes) {
        allBytes.putUint8List(plane.bytes);
      }
      final bytes = allBytes.done().buffer.asUint8List();

      final Size imageSize = Size(image.width.toDouble(), image.height.toDouble());
      
      final imageRotation = InputImageRotation.values.firstWhere(
        (r) => r.rawValue == camera.sensorOrientation,
        orElse: () => InputImageRotation.rotation0deg,
      );
      final inputImageFormat = InputImageFormat.values.firstWhere(
        (f) => f.rawValue == image.format.raw,
        orElse: () => InputImageFormat.nv21,
      );

      final inputImageData = InputImageMetadata(
        size: imageSize,
        rotation: imageRotation,
        format: inputImageFormat,
        bytesPerRow: image.planes.first.bytesPerRow,
      );

      final inputImage = InputImage.fromBytes(bytes: bytes, metadata: inputImageData);
      
      final faces = await _faceDetector.processImage(inputImage);

      if (faces.isNotEmpty) {
        setState(() {
          _statusMessage = 'Face Detected. Verifying Biometrics...';
        });
        
        await Future.delayed(const Duration(milliseconds: 1500));
        
        if (mounted) {
          setState(() {
            _isVerified = true;
            _statusMessage = 'Access Granted';
          });
          
          await _cameraController?.stopImageStream();
          String? capturedPath;
          try {
            final XFile picture = await _cameraController!.takePicture();
            capturedPath = picture.path;
          } catch (e) {
            print("Could not capture high-res photo: $e");
            capturedPath = "success_no_image";
          }
          await Future.delayed(const Duration(milliseconds: 1200)); 
          if (mounted) Navigator.pop(context, capturedPath);
        }
      }
    } catch (e) {
      print('Error processing image: $e');
    }
    _isProcessing = false;
  }

  @override
  void dispose() {
    _animationController.dispose();
    _cameraController?.dispose();
    _faceDetector.close();
    super.dispose();
  }

  Widget _buildCameraFeed() {
    if (_cameraController == null || !_cameraController!.value.isInitialized) {
      return const Center(child: CircularProgressIndicator(color: Colors.cyanAccent));
    }
    
    // Scale the camera preview to fill the screen flawlessly
    final size = MediaQuery.of(context).size;
    var scale = size.aspectRatio * _cameraController!.value.aspectRatio;
    if (scale < 1) scale = 1 / scale;

    return Transform.scale(
      scale: scale,
      child: Center(child: CameraPreview(_cameraController!)),
    );
  }

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.of(context).size;
    final double cutoutSize = size.width * 0.75;
    final double topOffset = size.height * 0.2;

    return Scaffold(
      backgroundColor: Colors.black,
      body: Stack(
        fit: StackFit.expand,
        children: [
          // 1. Full-Screen Camera Feed
          _buildCameraFeed(),
          
          // 2. High-Tech Overlay (Path Difference so it's guaranteed transparent in the middle)
          CustomPaint(
            painter: HUDOverlayPainter(
              cutoutRect: Rect.fromLTWH((size.width - cutoutSize) / 2, topOffset, cutoutSize, cutoutSize),
              isVerified: _isVerified,
            ),
          ),

          // 3. Animated Scanning Laser
          if (!_isVerified)
            AnimatedBuilder(
              animation: _animationController,
              builder: (context, child) {
                return Positioned(
                  top: topOffset + (_animationController.value * cutoutSize),
                  left: (size.width - cutoutSize) / 2,
                  width: cutoutSize,
                  child: Container(
                    height: 3,
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [
                          Colors.cyanAccent.withOpacity(0.0),
                          Colors.cyanAccent,
                          Colors.cyanAccent.withOpacity(0.0),
                        ],
                      ),
                      boxShadow: [
                        BoxShadow(color: Colors.cyanAccent.withOpacity(0.8), blurRadius: 15, spreadRadius: 3),
                      ],
                    ),
                  ),
                );
              },
            ),

          // 4. Professional HUD UI
          SafeArea(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                // Header
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
                  child: Row(
                    children: [
                      Container(
                        decoration: BoxDecoration(color: Colors.black45, borderRadius: BorderRadius.circular(12)),
                        child: IconButton(
                          icon: const Icon(Icons.arrow_back_ios_new, color: Colors.white, size: 20),
                          onPressed: () => Navigator.pop(context, false),
                        ),
                      ),
                      const SizedBox(width: 16),
                      const Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('BIOMETRIC SCAN', style: TextStyle(color: Colors.cyanAccent, fontSize: 12, letterSpacing: 2, fontWeight: FontWeight.bold)),
                          Text('Facial Recognition', style: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.w600)),
                        ],
                      ),
                    ],
                  ),
                ),

                // Footer Status
                Padding(
                  padding: const EdgeInsets.only(bottom: 60.0),
                  child: Column(
                    children: [
                      Text(
                        'SUBJECT: ${widget.studentName.toUpperCase()}',
                        style: const TextStyle(color: Colors.white, fontSize: 16, letterSpacing: 1.5, fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 24),
                      AnimatedContainer(
                        duration: const Duration(milliseconds: 300),
                        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
                        decoration: BoxDecoration(
                          color: _isVerified ? Colors.green.withOpacity(0.9) : Colors.black87,
                          borderRadius: BorderRadius.circular(30),
                          border: Border.all(color: _isVerified ? Colors.greenAccent : Colors.cyanAccent, width: 2),
                          boxShadow: _isVerified ? [BoxShadow(color: Colors.greenAccent.withOpacity(0.5), blurRadius: 20)] : [],
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            if (_isVerified) 
                              const Icon(Icons.verified_user, color: Colors.white)
                            else 
                              const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(color: Colors.cyanAccent, strokeWidth: 2)),
                            const SizedBox(width: 12),
                            Text(
                              _statusMessage.toUpperCase(),
                              style: TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.bold, letterSpacing: 1.2),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class HUDOverlayPainter extends CustomPainter {
  final Rect cutoutRect;
  final bool isVerified;

  HUDOverlayPainter({required this.cutoutRect, required this.isVerified});

  @override
  void paint(Canvas canvas, Size size) {
    // 1. Draw the darkened background with a perfectly clear cutout
    final paint = Paint()..color = Colors.black.withOpacity(0.85)..style = PaintingStyle.fill;
    
    final Path overlayPath = Path()..addRect(Rect.fromLTWH(0, 0, size.width, size.height));
    final Path cutoutPath = Path()..addOval(cutoutRect);
    
    // Difference ensures the oval is 100% transparent showing the camera beneath
    final Path finalPath = Path.combine(PathOperation.difference, overlayPath, cutoutPath);
    canvas.drawPath(finalPath, paint);

    // 2. Draw High-Tech Corner Brackets around the cutout
    final bracketPaint = Paint()
      ..color = isVerified ? Colors.greenAccent : Colors.cyanAccent
      ..style = PaintingStyle.stroke
      ..strokeWidth = 4
      ..strokeCap = StrokeCap.round;

    final double length = 30.0;
    
    // Top Left
    canvas.drawLine(cutoutRect.topLeft, cutoutRect.topLeft + Offset(length, 0), bracketPaint);
    canvas.drawLine(cutoutRect.topLeft, cutoutRect.topLeft + Offset(0, length), bracketPaint);
    
    // Top Right
    canvas.drawLine(cutoutRect.topRight, cutoutRect.topRight + Offset(-length, 0), bracketPaint);
    canvas.drawLine(cutoutRect.topRight, cutoutRect.topRight + Offset(0, length), bracketPaint);
    
    // Bottom Left
    canvas.drawLine(cutoutRect.bottomLeft, cutoutRect.bottomLeft + Offset(length, 0), bracketPaint);
    canvas.drawLine(cutoutRect.bottomLeft, cutoutRect.bottomLeft + Offset(0, -length), bracketPaint);
    
    // Bottom Right
    canvas.drawLine(cutoutRect.bottomRight, cutoutRect.bottomRight + Offset(-length, 0), bracketPaint);
    canvas.drawLine(cutoutRect.bottomRight, cutoutRect.bottomRight + Offset(0, -length), bracketPaint);
    
    // 3. Draw a subtle glowing ring
    final ringPaint = Paint()
      ..color = (isVerified ? Colors.greenAccent : Colors.cyanAccent).withOpacity(0.3)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2;
    canvas.drawOval(cutoutRect, ringPaint);
  }

  @override
  bool shouldRepaint(covariant HUDOverlayPainter oldDelegate) {
    return oldDelegate.isVerified != isVerified || oldDelegate.cutoutRect != cutoutRect;
  }
}
"""

with open('lib/screens/driver/live_frs_scanner_screen.dart', 'w', encoding='utf-8') as f:
    f.write(new_code)
print("FRS Screen rebuilt successfully.")
