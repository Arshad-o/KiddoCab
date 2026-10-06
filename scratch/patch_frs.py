import re

def patch_frs():
    filepath = 'lib/screens/driver/live_frs_scanner_screen.dart'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Add foundation import
    if "import 'package:flutter/foundation.dart';" not in content:
        content = content.replace("import 'package:flutter/material.dart';", "import 'package:flutter/material.dart';\nimport 'package:flutter/foundation.dart';")

    # Fix rotation and format
    old_rotation = "final imageRotation = InputImageRotationValue.fromRawValue(camera.sensorOrientation) ?? InputImageRotationValue.rotation0deg;"
    new_rotation = """final imageRotation = InputImageRotation.values.firstWhere(
        (r) => r.rawValue == camera.sensorOrientation,
        orElse: () => InputImageRotation.rotation0deg,
      );"""
      
    old_format = "final inputImageFormat = InputImageFormatValue.fromRawValue(image.format.raw) ?? InputImageFormatValue.nv21;"
    new_format = """final inputImageFormat = InputImageFormat.values.firstWhere(
        (f) => f.rawValue == image.format.raw,
        orElse: () => InputImageFormat.nv21,
      );"""

    content = content.replace(old_rotation, new_rotation)
    content = content.replace(old_format, new_format)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        
patch_frs()
