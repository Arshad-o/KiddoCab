import re
import os

# 1. Generate Location Data map
os.makedirs('lib/utils', exist_ok=True)
location_data_code = """class LocationData {
  static const Map<String, Map<String, List<String>>> indiaRegions = {
    'Telangana': {
      'Hyderabad': ['Ameerpet', 'Banjara Hills', 'Jubilee Hills', 'Khairatabad', 'Secunderabad', 'Madhapur', 'Gachibowli'],
      'Rangareddy': ['Serilingampally', 'Rajendranagar', 'Saroornagar', 'Shamshabad', 'Ibrahimpatnam'],
      'Medchal-Malkajgiri': ['Medchal', 'Malkajgiri', 'Kukatpally', 'Quthbullapur', 'Uppal'],
      'Warangal': ['Warangal', 'Hanamkonda', 'Kazipet'],
      'Nizamabad': ['Nizamabad South', 'Nizamabad North', 'Armoor', 'Bodhan'],
    },
    'Andhra Pradesh': {
      'Visakhapatnam': ['Bheemunipatnam', 'Anandapuram', 'Padmanabham', 'Pendurthi'],
      'Vijayawada (NTR)': ['Vijayawada Rural', 'Vijayawada Urban', 'Ibrahimpatnam', 'Mylavaram'],
      'Guntur': ['Guntur East', 'Guntur West', 'Mangalagiri', 'Tenali'],
    },
    'Karnataka': {
      'Bengaluru Urban': ['Bengaluru North', 'Bengaluru South', 'Bengaluru East', 'Anekal'],
      'Mysuru': ['Mysuru', 'Nanjangud', 'T. Narasipura'],
    }
  };

  static List<String> getStates() => indiaRegions.keys.toList();
  static List<String> getDistricts(String state) => indiaRegions[state]?.keys.toList() ?? [];
  static List<String> getMandals(String state, String district) => indiaRegions[state]?[district] ?? [];
}
"""
with open('lib/utils/location_data.dart', 'w', encoding='utf-8') as f:
    f.write(location_data_code)

# 2. Update AuthService
auth_service_path = 'lib/services/auth_service.dart'
with open(auth_service_path, 'r', encoding='utf-8') as f:
    auth_content = f.read()

old_auth_sig = "static Future<String?> registerUserWithPassword(String email, String password, String phone, String role, String gender, {String? childName, String? vehicleType}) async {"
new_auth_sig = "static Future<String?> registerUserWithPassword(String email, String password, String phone, String role, String gender, {String? childName, String? vehicleType, String? state, String? district, String? mandal, String? pincode}) async {"

old_data_insert = """      if (childName != null) data['child_name'] = childName;
      if (vehicleType != null) data['vehicle_type'] = vehicleType;

      await supabase.from('users').insert(data);"""

new_data_insert = """      if (childName != null) data['child_name'] = childName;
      if (vehicleType != null) data['vehicle_type'] = vehicleType;
      if (state != null) data['state'] = state;
      if (district != null) data['district'] = district;
      if (mandal != null) data['mandal'] = mandal;
      if (pincode != null) data['pincode'] = pincode;

      await supabase.from('users').insert(data);"""

auth_content = auth_content.replace(old_auth_sig, new_auth_sig).replace(old_data_insert, new_data_insert)
with open(auth_service_path, 'w', encoding='utf-8') as f:
    f.write(auth_content)

# 3. Helper to update Registration Screens
def update_registration_screen(filepath, role):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if "import '../../utils/location_data.dart';" not in content and "import '../utils/location_data.dart';" not in content:
        import_path = "import '../../utils/location_data.dart';" if "driver" in filepath or "parent" in filepath else "import '../utils/location_data.dart';"
        content = content.replace("import 'package:flutter/material.dart';", f"import 'package:flutter/material.dart';\n{import_path}")

    # Add state variables
    state_vars = """  String _gender = 'male';
  String? _selectedState;
  String? _selectedDistrict;
  String? _selectedMandal;
  final TextEditingController _pincodeController = TextEditingController();"""
    content = re.sub(r'String _gender = \'male\';', state_vars, content)

    # Add UI fields
    dropdown_ui = """                const SizedBox(height: 24),
                Text('Regional Information', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold, color: theme.colorScheme.primary)),
                const SizedBox(height: 16),
                
                DropdownButtonFormField<String>(
                  decoration: const InputDecoration(labelText: 'State *', border: OutlineInputBorder(), prefixIcon: Icon(Icons.map)),
                  value: _selectedState,
                  items: LocationData.getStates().map((s) => DropdownMenuItem(value: s, child: Text(s))).toList(),
                  onChanged: (val) {
                    setState(() {
                      _selectedState = val;
                      _selectedDistrict = null;
                      _selectedMandal = null;
                    });
                  },
                  validator: (val) => val == null ? 'Required' : null,
                ),
                const SizedBox(height: 16),
                
                DropdownButtonFormField<String>(
                  decoration: const InputDecoration(labelText: 'District *', border: OutlineInputBorder(), prefixIcon: Icon(Icons.location_city)),
                  value: _selectedDistrict,
                  items: _selectedState == null ? [] : LocationData.getDistricts(_selectedState!).map((d) => DropdownMenuItem(value: d, child: Text(d))).toList(),
                  onChanged: (val) {
                    setState(() {
                      _selectedDistrict = val;
                      _selectedMandal = null;
                    });
                  },
                  validator: (val) => val == null ? 'Required' : null,
                ),
                const SizedBox(height: 16),

                DropdownButtonFormField<String>(
                  decoration: const InputDecoration(labelText: 'Mandal / Zone *', border: OutlineInputBorder(), prefixIcon: Icon(Icons.my_location)),
                  value: _selectedMandal,
                  items: _selectedDistrict == null ? [] : LocationData.getMandals(_selectedState!, _selectedDistrict!).map((m) => DropdownMenuItem(value: m, child: Text(m))).toList(),
                  onChanged: (val) {
                    setState(() {
                      _selectedMandal = val;
                    });
                  },
                  validator: (val) => val == null ? 'Required' : null,
                ),
                const SizedBox(height: 16),

                TextFormField(
                  controller: _pincodeController,
                  decoration: const InputDecoration(labelText: 'Pincode *', border: OutlineInputBorder(), prefixIcon: Icon(Icons.pin_drop)),
                  keyboardType: TextInputType.number,
                  maxLength: 6,
                  validator: (value) => value == null || value.length != 6 ? 'Enter valid 6-digit Pincode' : null,
                ),
                const SizedBox(height: 24),"""

    # Inject UI before "const SizedBox(height: 24)," followed by "SizedBox(\n                  width: double.infinity,"
    button_regex = r'(const SizedBox\(height: 24\);\s+SizedBox\(\s+width: double\.infinity,\s+child: ElevatedButton)'
    content = re.sub(button_regex, dropdown_ui + r'\n                \1', content)

    # Fix auth call
    if role == 'parent':
        old_call = "final errorMessage = await AuthService.registerUserWithPassword(email, password, phone, 'parent', _gender, childName: _children[0]['name']!.text.trim());"
        new_call = "final errorMessage = await AuthService.registerUserWithPassword(email, password, phone, 'parent', _gender, childName: _children[0]['name']!.text.trim(), state: _selectedState, district: _selectedDistrict, mandal: _selectedMandal, pincode: _pincodeController.text.trim());"
        content = content.replace(old_call, new_call)
    elif role == 'driver':
        old_call = "final errorMessage = await AuthService.registerUserWithPassword(email, password, phone, 'driver', _gender, vehicleType: _selectedVehicle);"
        new_call = "final errorMessage = await AuthService.registerUserWithPassword(email, password, phone, 'driver', _gender, vehicleType: _selectedVehicle, state: _selectedState, district: _selectedDistrict, mandal: _selectedMandal, pincode: _pincodeController.text.trim());"
        content = content.replace(old_call, new_call)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

update_registration_screen('lib/screens/parent/parent_register_screen.dart', 'parent')
update_registration_screen('lib/screens/driver/driver_register_screen.dart', 'driver')
print("Regional Data added to UI and Auth Service")
