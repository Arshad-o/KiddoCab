import re

# Add const constructor to ParentDashboard
with open('lib/screens/parent_dashboard.dart', 'r', encoding='utf-8') as f:
    content = f.read()

if "const ParentDashboard({super.key});" not in content:
    content = content.replace("class ParentDashboard extends StatefulWidget {\n", "class ParentDashboard extends StatefulWidget {\n  const ParentDashboard({super.key});\n")

with open('lib/screens/parent_dashboard.dart', 'w', encoding='utf-8') as f:
    f.write(content)

# Fix parent_login_screen.dart (remove const just in case)
with open('lib/screens/parent/parent_login_screen.dart', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace("const ParentDashboard()", "ParentDashboard()")
with open('lib/screens/parent/parent_login_screen.dart', 'w', encoding='utf-8') as f:
    f.write(c)

# Fix parent_register_screen.dart (remove const just in case)
with open('lib/screens/parent/parent_register_screen.dart', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace("const ParentDashboard()", "ParentDashboard()")
with open('lib/screens/parent/parent_register_screen.dart', 'w', encoding='utf-8') as f:
    f.write(c)

