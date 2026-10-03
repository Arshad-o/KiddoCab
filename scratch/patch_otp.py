with open('lib/screens/auth/otp_screen.dart', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('maxLength: 6,', 'maxLength: 10,')

with open('lib/screens/auth/otp_screen.dart', 'w', encoding='utf-8') as f:
    f.write(c)
