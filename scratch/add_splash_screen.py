import re

def modify_main():
    with open('lib/main.dart', 'r', encoding='utf-8') as f:
        content = f.read()

    # Modify _checkAuth to add a slight delay for the splash screen effect
    old_check_auth = """  Future<void> _checkAuth() async {
    // Delay execution until after the first frame is rendered
    // to safely use Navigator context.
    WidgetsBinding.instance.addPostFrameCallback((_) async {"""
    
    new_check_auth = """  Future<void> _checkAuth() async {
    // Delay execution until after the first frame is rendered
    // to safely use Navigator context.
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      // Artificial delay to show the beautiful splash screen
      await Future.delayed(const Duration(seconds: 2));
      """
    
    if "await Future.delayed(const Duration(seconds: 2));" not in content:
        content = content.replace(old_check_auth, new_check_auth)

    # Modify the build method to show the logo and loading bar
    old_build = """  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      backgroundColor: Color(0xFF1E3A8A),
      body: Center(
        child: CircularProgressIndicator(color: Colors.white),
      ),
    );
  }"""

    new_build = """  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      backgroundColor: theme.colorScheme.primary, // Dark Blue
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // App Icon
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.white,
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.2),
                    blurRadius: 20,
                    offset: const Offset(0, 10),
                  ),
                ],
              ),
              child: Image.asset(
                'assets/images/logo_transparent.png',
                width: 120,
                height: 120,
                fit: BoxFit.contain,
              ),
            ),
            const SizedBox(height: 32),
            // App Name
            const Text(
              'KiddoCab',
              style: TextStyle(
                fontSize: 36,
                fontWeight: FontWeight.bold,
                color: Colors.white,
                letterSpacing: 1.5,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Safe & Smart School Rides',
              style: TextStyle(
                fontSize: 16,
                color: Colors.white70,
                letterSpacing: 0.5,
              ),
            ),
            const SizedBox(height: 48),
            // Beautiful Loading Bar
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 60.0),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(10),
                child: const LinearProgressIndicator(
                  minHeight: 8,
                  backgroundColor: Colors.white24,
                  valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                ),
              ),
            ),
            const SizedBox(height: 16),
            const Text(
              'Initializing Engine...',
              style: TextStyle(color: Colors.white70, fontSize: 14),
            )
          ],
        ),
      ),
    );
  }"""

    content = content.replace(old_build, new_build)

    with open('lib/main.dart', 'w', encoding='utf-8') as f:
        f.write(content)

modify_main()
