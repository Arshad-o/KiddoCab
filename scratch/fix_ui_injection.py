import re

def fix_injection(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    regional_ui = """                const SizedBox(height: 24),
                Text('Regional Information', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold, color: Theme.of(context).colorScheme.primary)),
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
"""

    if "Regional Information" not in content:
        # For Parent Screen
        anchor = """const SizedBox(height: 24),
                ElevatedButton(
                  onPressed: _proceed,"""
        
        # For Driver Screen
        anchor2 = """const SizedBox(height: 24),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _proceed,"""

        if anchor in content:
            content = content.replace(anchor, regional_ui + anchor)
        elif anchor2 in content:
            content = content.replace(anchor2, regional_ui + anchor2)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

fix_injection('lib/screens/parent/parent_register_screen.dart')
fix_injection('lib/screens/driver/driver_register_screen.dart')
print("Fixed regional UI injection")
