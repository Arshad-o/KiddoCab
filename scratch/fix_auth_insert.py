import re

def fix_auth_insert():
    filepath = 'lib/services/auth_service.dart'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Change upsert to insert to avoid RLS Update policy failures during registration
    old_code = "await supabase.from('users').upsert(data);"
    new_code = "await supabase.from('users').insert(data);"
    
    if old_code in content:
        content = content.replace(old_code, new_code)
    else:
        print("Couldn't find upsert code")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

fix_auth_insert()
