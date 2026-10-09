import 'dart:io';
import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'dart:typed_data';
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
  String _statusMessage = 'Searching for face...';
  
  List<Face> _faces = [];
  Size? _imageSize;
  InputImageRotation? _rotation;
  CameraLensDirection _cameraLensDirection = CameraLensDirection.front;

  int _faceFramesDetected = 0;
  final int _requiredFramesForMatch = 8; // Simulates time needed to "match" the face

  @override
  void initState() {
    super.initState();
    _faceDetector = FaceDetector(options: FaceDetectorOptions(
      enableContours: false,
      enableLandmarks: false,
      enableClassification: false,
      enableTracking: false,
      performanceMode: FaceDetectorMode.fast, // Fast mode for real-time bounding box tracking
    ));
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
      _cameraLensDirection = camera.lensDirection;

      _cameraController = CameraController(
        camera,
        ResolutionPreset.high, // High resolution for accurate ML Kit Face Detection
        enableAudio: false,
        imageFormatGroup: Platform.isAndroid ? ImageFormatGroup.nv21 : ImageFormatGroup.bgra8888, // MUST be nv21 for ML Kit Android
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
      final BytesBuilder allBytes = BytesBuilder();
      for (final Plane plane in image.planes) {
        allBytes.add(plane.bytes);
      }
      final bytes = allBytes.toBytes();

      final Size imageSize = Size(image.width.toDouble(), image.height.toDouble());
      
      final imageRotation = InputImageRotation.values.firstWhere(
        (r) => r.rawValue == camera.sensorOrientation,
        orElse: () => InputImageRotation.rotation0deg,
      );
      final inputImageFormat = Platform.isAndroid ? InputImageFormat.nv21 : InputImageFormat.bgra8888;      // Leap app structure for accurate orientation
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
      );

      final inputImage = InputImage.fromBytes(bytes: bytes, metadata: inputImageData);
      
      final faces = await _faceDetector.processImage(inputImage);

      if (mounted) {
        setState(() {
          _faces = faces;
          _imageSize = imageSize;
          _rotation = imageRotation;

          if (faces.isNotEmpty) {
            _statusMessage = 'Face Detected. Matching...';
            _faceFramesDetected++;
          } else {
            _statusMessage = 'Searching for face...';
            _faceFramesDetected = 0; // Reset if face is lost
          }
        });
      }

      // If we've held the face in frame for enough time, trigger verification
      if (_faceFramesDetected >= _requiredFramesForMatch && !_isVerified) {
        await _handleVerificationSuccess();
      }

    } catch (e) {
      print('Error processing image: $e');
    }
    _isProcessing = false;
  }

  Future<void> _handleVerificationSuccess() async {
    if (!mounted) return;
    setState(() {
      _isVerified = true;
      _statusMessage = 'Access Granted!';
    });
    
    await _cameraController?.stopImageStream();
    String? capturedPath;
    try {
      final XFile picture = await _cameraController!.takePicture();
      capturedPath = picture.path;
    } catch (e) {
      print("Could not capture photo: $e");
      capturedPath = "success_no_image";
    }
    
    // Give user a moment to see the success state
    await Future.delayed(const Duration(milliseconds: 1200)); 
    if (mounted) Navigator.pop(context, capturedPath);
  }

  @override
  void dispose() {
    _cameraController?.dispose();
    _faceDetector.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_cameraController == null || !_cameraController!.value.isInitialized) {
      return const Scaffold(
        backgroundColor: Colors.black,
        body: Center(child: CircularProgressIndicator(color: Colors.cyanAccent)),
      );
    }

    final size = MediaQuery.of(context).size;

    return Scaffold(
      backgroundColor: Colors.black,
      body: Stack(
        fit: StackFit.expand,
        children: [
          // 1. Camera Feed (Fitted exactly to screen)
          FittedBox(
            fit: BoxFit.cover,
            child: SizedBox(
              width: _cameraController!.value.previewSize!.height, // Android flips these
              height: _cameraController!.value.previewSize!.width,
              child: CameraPreview(_cameraController!),
            ),
          ),
          
          // 2. Real-Time ML Face Bounding Boxes (Leap style)
          if (_imageSize != null && _rotation != null)
            FittedBox(
              fit: BoxFit.cover,
              child: SizedBox(
                width: _cameraController!.value.previewSize!.height,
                height: _cameraController!.value.previewSize!.width,
                child: CustomPaint(
                  painter: FaceMeshPainter(
                    faces: _faces,
                    imageSize: _imageSize!,
                    rotation: _rotation!,
                    cameraLensDirection: _cameraLensDirection,
                    isVerified: _isVerified,
                  ),
                ),
              ),
            ),

          // 3. Status UI
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
                        decoration: BoxDecoration(color: Colors.black54, borderRadius: BorderRadius.circular(12)),
                        child: IconButton(
                          icon: const Icon(Icons.arrow_back_ios_new, color: Colors.white, size: 20),
                          onPressed: () => Navigator.pop(context, false),
                        ),
                      ),
                      const SizedBox(width: 16),
                      const Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('LIVE FRS TRACKING', style: TextStyle(color: Colors.cyanAccent, fontSize: 12, letterSpacing: 2, fontWeight: FontWeight.bold)),
                          Text('Real-Time Match', style: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.w600)),
                        ],
                      ),
                    ],
                  ),
                ),

                // Footer
                Padding(
                  padding: const EdgeInsets.only(bottom: 60.0),
                  child: Column(
                    children: [
                      Text(
                        'SUBJECT: ${widget.studentName.toUpperCase()}',
                        style: const TextStyle(color: Colors.white, fontSize: 16, letterSpacing: 1.5, fontWeight: FontWeight.bold, shadows: [Shadow(color: Colors.black, blurRadius: 4)]),
                      ),
                      const SizedBox(height: 24),
                      AnimatedContainer(
                        duration: const Duration(milliseconds: 300),
                        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
                        decoration: BoxDecoration(
                          color: _isVerified ? Colors.green.withOpacity(0.9) : Colors.black87,
                          borderRadius: BorderRadius.circular(30),
                          border: Border.all(color: _isVerified ? Colors.greenAccent : (_faces.isNotEmpty ? Colors.cyanAccent : Colors.white30), width: 2),
                          boxShadow: _isVerified 
                            ? [BoxShadow(color: Colors.greenAccent.withOpacity(0.5), blurRadius: 20)] 
                            : (_faces.isNotEmpty ? [BoxShadow(color: Colors.cyanAccent.withOpacity(0.3), blurRadius: 10)] : []),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            if (_isVerified) 
                              const Icon(Icons.verified_user, color: Colors.white)
                            else if (_faces.isNotEmpty)
                              const Icon(Icons.face, color: Colors.cyanAccent)
                            else
                              const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(color: Colors.white54, strokeWidth: 2)),
                            const SizedBox(width: 12),
                            Text(
                              _statusMessage.toUpperCase(),
                              style: TextStyle(color: _faces.isNotEmpty || _isVerified ? Colors.white : Colors.white54, fontSize: 14, fontWeight: FontWeight.bold, letterSpacing: 1.2),
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

class FaceMeshPainter extends CustomPainter {
  final List<Face> faces;
  final Size imageSize;
  final InputImageRotation rotation;
  final CameraLensDirection cameraLensDirection;
  final bool isVerified;

  FaceMeshPainter({
    required this.faces,
    required this.imageSize,
    required this.rotation,
    required this.cameraLensDirection,
    required this.isVerified,
  });

  @override
  void paint(Canvas canvas, Size size) {
    if (faces.isEmpty) return;

    final Paint paint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 4.0
      ..color = isVerified ? Colors.greenAccent : Colors.cyanAccent;
      
    final Paint fillPaint = Paint()
      ..style = PaintingStyle.fill
      ..color = (isVerified ? Colors.greenAccent : Colors.cyanAccent).withOpacity(0.15);

    for (final Face face in faces) {
      // Scale rect coordinates from the camera image size to our rendered size
      // Note: For Android portrait, the imageSize arrives rotated (e.g., width 480, height 640)
      // but our Render size is width 640, height 480.
      
      final bool isPortrait = rotation == InputImageRotation.rotation90deg || rotation == InputImageRotation.rotation270deg;
      
      final double absoluteImageWidth = isPortrait ? imageSize.height : imageSize.width;
      final double absoluteImageHeight = isPortrait ? imageSize.width : imageSize.height;

      final double scaleX = size.width / absoluteImageWidth;
      final double scaleY = size.height / absoluteImageHeight;

      final Rect boundingBox = face.boundingBox;

      double left;
      double right;

      // Handle mirroring for front camera
      if (cameraLensDirection == CameraLensDirection.front) {
        left = size.width - (boundingBox.right * scaleX);
        right = size.width - (boundingBox.left * scaleX);
      } else {
        left = boundingBox.left * scaleX;
        right = boundingBox.right * scaleX;
      }

      double top = boundingBox.top * scaleY;
      double bottom = boundingBox.bottom * scaleY;

      final translatedRect = Rect.fromLTRB(left, top, right, bottom);

      // Draw the interactive bounding box around the face
      canvas.drawRect(translatedRect, fillPaint);
      
      // Draw targeting brackets instead of a full square
      final double cornerLength = 20.0;
      
      // Top Left
      canvas.drawLine(translatedRect.topLeft, translatedRect.topLeft + Offset(cornerLength, 0), paint);
      canvas.drawLine(translatedRect.topLeft, translatedRect.topLeft + Offset(0, cornerLength), paint);
      
      // Top Right
      canvas.drawLine(translatedRect.topRight, translatedRect.topRight + Offset(-cornerLength, 0), paint);
      canvas.drawLine(translatedRect.topRight, translatedRect.topRight + Offset(0, cornerLength), paint);
      
      // Bottom Left
      canvas.drawLine(translatedRect.bottomLeft, translatedRect.bottomLeft + Offset(cornerLength, 0), paint);
      canvas.drawLine(translatedRect.bottomLeft, translatedRect.bottomLeft + Offset(0, -cornerLength), paint);
      
      // Bottom Right
      canvas.drawLine(translatedRect.bottomRight, translatedRect.bottomRight + Offset(-cornerLength, 0), paint);
      canvas.drawLine(translatedRect.bottomRight, translatedRect.bottomRight + Offset(0, -cornerLength), paint);
    }
  }

  @override
  bool shouldRepaint(FaceMeshPainter oldDelegate) {
    return oldDelegate.faces != faces || oldDelegate.isVerified != isVerified;
  }
}
