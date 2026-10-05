import re

def fix_gps_silence(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix serviceEnabled
    old_service = r"serviceEnabled = await Geolocator\.isLocationServiceEnabled\(\);\s*if \(!serviceEnabled\) return;"
    new_service = """serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please enable GPS Location Services!'), backgroundColor: Colors.red));
      return;
    }"""
    content = re.sub(old_service, new_service, content)

    # Fix denied
    old_denied = r"permission = await Geolocator\.requestPermission\(\);\s*if \(permission == LocationPermission\.denied\) return;"
    new_denied = """permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) {
        if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Location permissions denied!'), backgroundColor: Colors.red));
        return;
      }"""
    content = re.sub(old_denied, new_denied, content)

    # Fix deniedForever
    old_forever = r"if \(permission == LocationPermission\.deniedForever\) return;"
    new_forever = """if (permission == LocationPermission.deniedForever) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Location permissions are permanently denied, please enable in settings.'), backgroundColor: Colors.red));
      return;
    }"""
    content = re.sub(old_forever, new_forever, content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

fix_gps_silence('lib/screens/parent_dashboard.dart')
fix_gps_silence('lib/screens/driver_dashboard.dart')
