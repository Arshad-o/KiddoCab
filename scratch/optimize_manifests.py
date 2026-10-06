import os
import re

def optimize_android_manifest():
    manifest_path = 'android/app/src/main/AndroidManifest.xml'
    with open(manifest_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Add missing production permissions
    permissions_to_add = """    <uses-permission android:name="android.permission.CAMERA" />
    <uses-permission android:name="android.permission.ACCESS_BACKGROUND_LOCATION" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" android:maxSdkVersion="32" />
    <uses-permission android:name="android.permission.READ_MEDIA_IMAGES" />
    <uses-feature android:name="android.hardware.camera" android:required="false" />
    <uses-feature android:name="android.hardware.camera.front" android:required="false" />"""

    if "android.permission.CAMERA" not in content:
        content = content.replace(
            '<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />',
            '<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />\n' + permissions_to_add
        )

    # Change label
    content = content.replace('android:label="kiddo_cab"', 'android:label="KiddoCab"')

    with open(manifest_path, 'w', encoding='utf-8') as f:
        f.write(content)

def optimize_ios_plist():
    plist_path = 'ios/Runner/Info.plist'
    with open(plist_path, 'r', encoding='utf-8') as f:
        content = f.read()

    privacy_keys = """	<key>NSCameraUsageDescription</key>
	<string>KiddoCab requires camera access to perform live facial recognition (FRS) matching for student security and to capture document photos.</string>
	<key>NSPhotoLibraryUsageDescription</key>
	<string>KiddoCab needs photo library access so drivers can upload their license and vehicle registration documents.</string>
	<key>NSLocationWhenInUseUsageDescription</key>
	<string>KiddoCab requires your location to track rides, coordinate pickups, and display your position on the live map.</string>
	<key>NSLocationAlwaysAndWhenInUseUsageDescription</key>
	<string>KiddoCab requires background location tracking so parents can securely monitor the live position of the cab during a ride, even when the app is minimized.</string>"""

    if "NSCameraUsageDescription" not in content:
        content = content.replace(
            '<dict>\n',
            '<dict>\n' + privacy_keys + '\n'
        )

    with open(plist_path, 'w', encoding='utf-8') as f:
        f.write(content)

optimize_android_manifest()
optimize_ios_plist()
print("Production Manifest and Plist optimization complete.")
