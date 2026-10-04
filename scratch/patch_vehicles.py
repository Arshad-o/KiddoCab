import re

with open('lib/screens/driver/driver_register_screen.dart', 'r', encoding='utf-8') as f:
    code = f.read()

old_vars = """  String _selectedVehicle = 'School Bus';

  final List<Map<String, dynamic>> _vehicleTypes = [
    {'name': 'School Bus', 'icon': Icons.directions_bus, 'color': Colors.amber},
    {'name': 'Mini Van', 'icon': Icons.airport_shuttle, 'color': Colors.blue},
    {'name': 'SUV', 'icon': Icons.directions_car, 'color': Colors.grey},
    {'name': 'Sedan', 'icon': Icons.local_taxi, 'color': Colors.black87},
  ];"""

new_vars = """  String _selectedVehicle = 'Auto Rickshaw';

  final List<Map<String, dynamic>> _vehicleTypes = [
    {'name': 'Auto Rickshaw', 'image': 'assets/images/autoimg.jpg', 'color': Colors.amber},
    {'name': 'Large Auto', 'image': 'assets/images/big_auto_img.jpg', 'color': Colors.deepOrange},
    {'name': 'Tata Magic', 'image': 'assets/images/tata_magic.png', 'color': Colors.blue},
    {'name': 'Cab', 'image': 'assets/images/cab.avif', 'color': Colors.grey},
  ];"""

code = code.replace(old_vars, new_vars)

old_grid = """                          Icon(vehicle['icon'], size: 48, color: vehicle['color']),
                          const SizedBox(height: 12),
                          Text(
                            vehicle['name'],"""

new_grid = """                          Expanded(
                            child: Padding(
                              padding: const EdgeInsets.all(8.0),
                              child: Image.asset(vehicle['image'], fit: BoxFit.contain),
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            vehicle['name'],"""

code = code.replace(old_grid, new_grid)

with open('lib/screens/driver/driver_register_screen.dart', 'w', encoding='utf-8') as f:
    f.write(code)
