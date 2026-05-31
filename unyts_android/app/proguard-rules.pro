# Keep JNI bridge so R8 does not strip the native method declarations.
-keep class com.unyts.app.jni.UnytsJNI { *; }

# Keep all app classes reachable from the JNI bridge.
-keep class com.unyts.app.** { *; }
