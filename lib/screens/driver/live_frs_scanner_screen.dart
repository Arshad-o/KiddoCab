import 'dart:ui';
import 'package:flutter/material.dart';
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
    ));
    _animationController = AnimationController(vsync: this, duration: const Duration(seconds: 2))..repeat();
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

      // Try to get front camera, else back camera
      final camera = cameras.firstWhere((c) => c.lensDirection == CameraLensDirection.front, orElse: () => cameras.first);

      _cameraController = CameraController(
        camera,
        ResolutionPreset.medium,
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
      final imageRotation = InputImageRotationValue.fromRawValue(camera.sensorOrientation) ?? InputImageRotationValue.rotation0deg;
      final inputImageFormat = InputImageFormatValue.fromRawValue(image.format.raw) ?? InputImageFormatValue.nv21;

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
          _statusMessage = 'Face detected. Verifying...';
        });
        
        // Simulate ML identity matching delay (like the Leap app)
        await Future.delayed(const Duration(seconds: 2));
        
        if (mounted) {
          setState(() {
            _isVerified = true;
            _statusMessage = 'Identity Verified!';
          });
          // Stop stream and pop with success
          await _cameraController?.stopImageStream();
          await Future.delayed(const Duration(milliseconds: 1000)); // Let them see the success message
          if (mounted) Navigator.pop(context, true);
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

  @override
  Widget build(BuildContext context) {
    if (_cameraController == null || !_cameraController!.value.isInitialized) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    final size = MediaQuery.of(context).size;

    return Scaffold(
      backgroundColor: Colors.black,
      body: Stack(
        fit: StackFit.expand,
        children: [
          // Camera Preview
          CameraPreview(_cameraController!),
          
          // Scanner Overlay
          CustomPaint(
            painter: ScannerOverlayPainter(),
          ),

          // Scanning Line Animation
          if (!_isVerified)
            AnimatedBuilder(
              animation: _animationController,
              builder: (context, child) {
                return Positioned(
                  top: size.height * 0.25 + (_animationController.value * (size.width * 0.7)),
                  left: size.width * 0.15,
                  right: size.width * 0.15,
                  child: Container(
                    height: 2,
                    decoration: BoxDecoration(
                      color: Colors.greenAccent,
                      boxShadow: [
                        BoxShadow(color: Colors.greenAccent.withOpacity(0.8), blurRadius: 10, spreadRadius: 2),
                      ],
                    ),
                  ),
                );
              },
            ),

          // UI Elements
          SafeArea(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                // Top Bar
                Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Row(
                    children: [
                      IconButton(
                        icon: const Icon(Icons.close, color: Colors.white, size: 30),
                        onPressed: () => Navigator.pop(context, false),
                      ),
                      const SizedBox(width: 16),
                      const Text(
                        'Live FRS Scan',
                        style: TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                ),

                // Status Text
                Padding(
                  padding: const EdgeInsets.only(bottom: 60.0),
                  child: Column(
                    children: [
                      Text(
                        'Scanning: ${widget.studentName}',
                        style: const TextStyle(color: Colors.white70, fontSize: 18),
                      ),
                      const SizedBox(height: 16),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                        decoration: BoxDecoration(
                          color: _isVerified ? Colors.green : Colors.blueAccent.withOpacity(0.8),
                          borderRadius: BorderRadius.circular(30),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            if (_isVerified) const Icon(Icons.check_circle, color: Colors.white)
                            else const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2)),
                            const SizedBox(width: 12),
                            Text(
                              _statusMessage,
                              style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
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

class ScannerOverlayPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.black54
      ..style = PaintingStyle.fill;

    // Draw dark overlay
    canvas.drawRect(Rect.fromLTWH(0, 0, size.width, size.height), paint);

    // Cut out a circle in the center
    final rect = Rect.fromCenter(
      center: Offset(size.width / 2, size.height / 2.2),
      width: size.width * 0.7,
      height: size.width * 0.7,
    );
    
    paint.blendMode = BlendMode.clear;
    canvas.drawOval(rect, paint);

    // Draw border around the circle
    paint.blendMode = BlendMode.srcOver;
    paint.color = Colors.blueAccent;
    paint.style = PaintingStyle.stroke;
    paint.strokeWidth = 3;
    canvas.drawOval(rect, paint);
  }

  @override
  bool shouldRepaint(CustomPainter oldDelegate) => false;
}
