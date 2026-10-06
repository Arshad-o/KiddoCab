import re

def insert_docs():
    filepath = 'lib/screens/driver/driver_register_screen.dart'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    old_ui = """              const SizedBox(height: 32),
              Row(
                children: [
                  Checkbox("""

    new_ui = """              const SizedBox(height: 24),
              
              Text('Document Uploads', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold, color: theme.colorScheme.secondary)),
              const Divider(),
              
              const Text('Registration Certificate (RC)', style: TextStyle(fontWeight: FontWeight.bold)),
              const Text('Capture a clear photo of the vehicle RC.', style: TextStyle(color: Colors.grey, fontSize: 13)),
              const SizedBox(height: 8),
              InkWell(
                onTap: _captureRcPhoto,
                child: Container(
                  height: 150,
                  decoration: BoxDecoration(
                    color: Colors.grey[200],
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: Colors.grey.withOpacity(0.5)),
                    image: _rcPhoto != null ? DecorationImage(image: FileImage(_rcPhoto!), fit: BoxFit.cover) : null,
                  ),
                  child: _rcPhoto == null 
                      ? const Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.description, size: 40, color: Colors.grey),
                            SizedBox(height: 8),
                            Text('Tap to capture RC', style: TextStyle(color: Colors.grey, fontWeight: FontWeight.bold)),
                          ],
                        )
                      : null,
                ),
              ),
              
              const SizedBox(height: 16),
              
              const Text('Driving License', style: TextStyle(fontWeight: FontWeight.bold)),
              const Text('Capture a clear photo of your valid driving license.', style: TextStyle(color: Colors.grey, fontSize: 13)),
              const SizedBox(height: 8),
              InkWell(
                onTap: _captureLicensePhoto,
                child: Container(
                  height: 150,
                  decoration: BoxDecoration(
                    color: Colors.grey[200],
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: Colors.grey.withOpacity(0.5)),
                    image: _licensePhoto != null ? DecorationImage(image: FileImage(_licensePhoto!), fit: BoxFit.cover) : null,
                  ),
                  child: _licensePhoto == null 
                      ? const Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.badge, size: 40, color: Colors.grey),
                            SizedBox(height: 8),
                            Text('Tap to capture License', style: TextStyle(color: Colors.grey, fontWeight: FontWeight.bold)),
                          ],
                        )
                      : null,
                ),
              ),

              const SizedBox(height: 32),
              Row(
                children: [
                  Checkbox("""

    if old_ui in content:
        content = content.replace(old_ui, new_ui)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Success!")
    else:
        print("Could not find block.")

insert_docs()
