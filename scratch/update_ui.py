import re

def fix_parent_gender():
    filepath = 'lib/screens/parent/parent_register_screen.dart'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the row containing gender
    old_row = """                Row(
                  children: [
                    Expanded(
                      child: RadioListTile<String>(
                        title: const Text('Male'),
                        value: 'male',
                        groupValue: _gender,
                        onChanged: (value) => setState(() => _gender = value!),
                        secondary: Image.asset('assets/images/male.jpg', width: 40, height: 40),
                      ),
                    ),
                    Expanded(
                      child: RadioListTile<String>(
                        title: const Text('Female'),
                        value: 'female',
                        groupValue: _gender,
                        onChanged: (value) => setState(() => _gender = value!),
                        secondary: Image.asset('assets/images/female.jpg', width: 40, height: 40),
                      ),
                    ),
                  ],
                ),"""
    
    new_col = """                Column(
                  children: [
                    RadioListTile<String>(
                      title: const Text('Male'),
                      value: 'male',
                      groupValue: _gender,
                      onChanged: (value) => setState(() => _gender = value!),
                      secondary: Image.asset('assets/images/male.jpg', width: 40, height: 40),
                    ),
                    RadioListTile<String>(
                      title: const Text('Female'),
                      value: 'female',
                      groupValue: _gender,
                      onChanged: (value) => setState(() => _gender = value!),
                      secondary: Image.asset('assets/images/female.jpg', width: 40, height: 40),
                    ),
                  ],
                ),"""

    if old_row in content:
        content = content.replace(old_row, new_col)
    else:
        # Fallback if exact match fails
        content = re.sub(
            r"Row\(\s*children: \[\s*Expanded\(\s*child: RadioListTile<String>\([\s\S]*?Female[\s\S]*?\),\s*\),\s*\],\s*\),",
            new_col,
            content
        )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def fix_driver_fields():
    filepath = 'lib/screens/driver/driver_register_screen.dart'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We need to insert Password, re-password, and Gender right after Email Address
    old_email_field = """              TextFormField(
                controller: _emailController,
                decoration: const InputDecoration(labelText: 'Email Address *', border: OutlineInputBorder()),
                keyboardType: TextInputType.emailAddress,
                validator: (value) {
                  if (value == null || value.isEmpty) return 'Required';
                  if (!value.contains('@')) return 'Invalid email';
                  return null;
                },
              ),
              const SizedBox(height: 32),"""

    new_fields = """              TextFormField(
                controller: _emailController,
                decoration: const InputDecoration(labelText: 'Email Address *', border: OutlineInputBorder()),
                keyboardType: TextInputType.emailAddress,
                validator: (value) {
                  if (value == null || value.isEmpty) return 'Required';
                  if (!value.contains('@')) return 'Invalid email';
                  return null;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _passwordController,
                decoration: const InputDecoration(labelText: 'Password *', border: OutlineInputBorder()),
                obscureText: true,
                validator: (value) => value == null || value.length < 6 ? 'Password must be at least 6 characters' : null,
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _rePasswordController,
                decoration: const InputDecoration(labelText: 'Re-enter Password *', border: OutlineInputBorder()),
                obscureText: true,
                validator: (value) => value == null || value.isEmpty ? 'Required' : null,
              ),
              const SizedBox(height: 24),
              Text('Gender', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold, color: theme.colorScheme.secondary)),
              Column(
                children: [
                  RadioListTile<String>(
                    title: const Text('Male'),
                    value: 'male',
                    groupValue: _gender,
                    onChanged: (value) => setState(() => _gender = value!),
                    secondary: Image.asset('assets/images/male.jpg', width: 40, height: 40),
                  ),
                  RadioListTile<String>(
                    title: const Text('Female'),
                    value: 'female',
                    groupValue: _gender,
                    onChanged: (value) => setState(() => _gender = value!),
                    secondary: Image.asset('assets/images/female.jpg', width: 40, height: 40),
                  ),
                ],
              ),
              const SizedBox(height: 32),"""

    if old_email_field in content:
        content = content.replace(old_email_field, new_fields)
    else:
        # regex
        pattern = r"TextFormField\(\s*controller: _emailController,[\s\S]*?return null;\s*\},\s*\),\s*const SizedBox\(height: 32\),"
        content = re.sub(pattern, new_fields, content)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

fix_parent_gender()
fix_driver_fields()
print("Fixed!")
