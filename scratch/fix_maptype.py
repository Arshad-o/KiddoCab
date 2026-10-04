import os
import glob

def fix_maptype():
    for filepath in glob.glob('lib/**/*.dart', recursive=True):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "import 'package:supabase_flutter/supabase_flutter.dart';" in content:
            print(f"Fixing MapType in {filepath}")
            content = content.replace(
                "import 'package:supabase_flutter/supabase_flutter.dart';",
                "import 'package:supabase_flutter/supabase_flutter.dart' hide MapType;"
            )
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

fix_maptype()
