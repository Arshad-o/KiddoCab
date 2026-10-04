package com.example.kiddo_cab

import android.os.Bundle
import android.view.WindowManager
import io.flutter.embedding.android.FlutterActivity

class MainActivity: FlutterActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // SECURITY: Blocks screenshots, screen recording, and hides app preview in recent apps menu
        window.addFlags(WindowManager.LayoutParams.FLAG_SECURE)
    }
}
