import re

def fix_ml_build():
    filepath = 'lib/screens/driver/live_frs_scanner_screen.dart'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if "import 'dart:typed_data';" not in content:
        content = content.replace("import 'package:flutter/foundation.dart';", "import 'package:flutter/foundation.dart';\nimport 'dart:typed_data';")

    old_buffer = """      final WriteBuffer allBytes = WriteBuffer();
      for (final Plane plane in image.planes) {
        allBytes.putUint8List(plane.bytes);
      }
      final bytes = allBytes.done().buffer.asUint8List();"""
      
    new_buffer = """      final BytesBuilder allBytes = BytesBuilder();
      for (final Plane plane in image.planes) {
        allBytes.add(plane.bytes);
      }
      final bytes = allBytes.toBytes();"""
      
    if old_buffer in content:
        content = content.replace(old_buffer, new_buffer)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

fix_ml_build()
print("Fixed WriteBuffer to BytesBuilder")
