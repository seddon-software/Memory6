package com.example.memorygame

import android.annotation.SuppressLint
import android.os.Bundle
import android.webkit.WebChromeClient
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        webView = WebView(this)
        setContentView(webView)

        val settings = webView.settings

        // 🔥 Enable JavaScript (required)
        settings.javaScriptEnabled = true

        // 🔥 Allow local files (needed for your HTML/CSS/images)
        settings.allowFileAccess = true
        settings.allowContentAccess = true

        // 🔥 Important for AJAX replacement / local loading
        settings.allowUniversalAccessFromFileURLs = true
        settings.allowFileAccessFromFileURLs = true

        // Optional but useful
        settings.domStorageEnabled = true

        // Prevent opening external browser
        webView.webViewClient = WebViewClient()

        // Enable console logs, alerts, etc.
        webView.webChromeClient = WebChromeClient()

        // 🔗 Connect Kotlin ↔ JavaScript
        webView.addJavascriptInterface(GameBridge(this), "Android")

        // 🐞 Debugging (use Chrome: chrome://inspect)
        WebView.setWebContentsDebuggingEnabled(true)

        // 📂 Load your HTML from assets
        webView.loadUrl("file:///android_asset/memory6.html")
    }

    // 🔙 Handle back button inside WebView
    override fun onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack()
        } else {
            super.onBackPressed()
        }
    }
}