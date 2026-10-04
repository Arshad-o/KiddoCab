import re

# 1. Update Parent Dashboard
with open('lib/screens/parent_dashboard.dart', 'r', encoding='utf-8') as f:
    parent_code = f.read()

if "import 'chat_screen.dart';" not in parent_code:
    parent_code = parent_code.replace("import 'parent/parent_login_screen.dart';", "import 'parent/parent_login_screen.dart';\nimport 'chat_screen.dart';")

old_parent_scaffold = """      body: TabBarView(
        physics: const NeverScrollableScrollPhysics(),
        children: [
          _buildChildrenProfiles(theme),
          _buildLiveMap(theme),
          _buildProfile(theme),
        ],
      ),"""

new_parent_scaffold = """      body: TabBarView(
        physics: const NeverScrollableScrollPhysics(),
        children: [
          _buildChildrenProfiles(theme),
          _buildLiveMap(theme),
          _buildProfile(theme),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => const ChatScreen(
                otherUserId: 'driver-placeholder-id', // MVP mapping
                otherUserName: 'Driver Michael',
              )
            ),
          );
        },
        backgroundColor: theme.colorScheme.secondary,
        child: const Icon(Icons.chat, color: Colors.white),
      ),"""
parent_code = parent_code.replace(old_parent_scaffold, new_parent_scaffold)

with open('lib/screens/parent_dashboard.dart', 'w', encoding='utf-8') as f:
    f.write(parent_code)


# 2. Update Driver Dashboard
with open('lib/screens/driver_dashboard.dart', 'r', encoding='utf-8') as f:
    driver_code = f.read()

if "import 'chat_screen.dart';" not in driver_code:
    driver_code = driver_code.replace("import 'driver/driver_login_screen.dart';", "import 'driver/driver_login_screen.dart';\nimport 'chat_screen.dart';")

old_driver_scaffold = """        body: TabBarView(
          physics: const NeverScrollableScrollPhysics(),
          children: [
            _buildManifest(theme),
            _buildLiveMap(theme),
            _buildProfile(theme),
          ],
        ),"""

new_driver_scaffold = """        body: TabBarView(
          physics: const NeverScrollableScrollPhysics(),
          children: [
            _buildManifest(theme),
            _buildLiveMap(theme),
            _buildProfile(theme),
          ],
        ),
        floatingActionButton: FloatingActionButton(
          onPressed: () {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => const ChatScreen(
                  otherUserId: 'parent-placeholder-id', // MVP mapping
                  otherUserName: 'Parent (Noah)',
                )
              ),
            );
          },
          backgroundColor: theme.colorScheme.secondary,
          child: const Icon(Icons.chat, color: Colors.white),
        ),"""
driver_code = driver_code.replace(old_driver_scaffold, new_driver_scaffold)

with open('lib/screens/driver_dashboard.dart', 'w', encoding='utf-8') as f:
    f.write(driver_code)
