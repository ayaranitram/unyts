# Plan: Android Application

> **Prerequisite**: The shared C++ core engine described in [PLAN_CPP_WINDOWS.md](PLAN_CPP_WINDOWS.md) must be completed (at minimum through Phase 4 — C API surface) before this plan begins.  The Android app reuses that engine with zero modifications.
>
> **Status**: The C++ core (Phases 0–6 of the Windows plan) is **fully complete** as of 2026-05-31.  The Android app can now begin.

---

## Progress Log

| Phase | Status | Date | Notes |
|-------|--------|------|-------|
| 0 — Prerequisites | ✅ Done | 2026-05-31 | Gradle 8.9 project scaffold; libs.versions.toml; CMakeLists.txt wired to `cpp/` core |
| 1 — JNI Bridge | ✅ Done | 2026-05-31 | `unyts_jni.cpp` (all C API entry points); `UnytsJNI.kt` (`external fun`); `UnytsService.kt` (coroutines + DataStore); `UnytsJNITest.kt` (10 instrumented tests) |
| 2 — Core UI | ✅ Done | 2026-05-31 | `ConvertViewModel`, `ConvertScreen` (autocomplete dropdown), `SettingsScreen`, `UnytsTheme`; bottom nav bar |
| 3 — Settings + Extras | ⏳ Partial | 2026-05-31 | FVF + timeout in `SettingsScreen` + DataStore; history screen placeholder only |
| 4 — Polish + Device Testing | ⬜ Not started | — | Real hardware, accessibility, adaptive icon |
| 5 — Google Play Submission | ⬜ Not started | — | AAB signing, store listing, rollout |

---

## 1. Overview

Build a native Android application for unyts using **Kotlin + Jetpack Compose** for the UI and the **shared C++ core library** for the conversion engine, integrated via the Android NDK and JNI.

The C++ library is compiled by CMake for each Android ABI (arm64-v8a, armeabi-v7a, x86_64) using the NDK toolchain.  A thin JNI bridge layer exposes the C API to Kotlin.

### Goals
- Android phone and tablet support
- Offline — all unit data embedded in the APK/AAB
- Google Play distribution
- Shared conversion engine with Windows and iOS apps (no logic duplication)

---

## 2. Architecture

```
┌───────────────────────────────────────────────────────┐
│            Kotlin + Jetpack Compose UI                │
│   MainActivity, ConvertScreen, SettingsScreen, etc.   │
└─────────────────────┬─────────────────────────────────┘
                      │ calls Kotlin class
┌─────────────────────▼─────────────────────────────────┐
│                Kotlin JNI Wrapper                     │
│              UnytsJNI.kt / UnytsService.kt            │
│   (Kotlin class declares `external` fun, loads .so)  │
└─────────────────────┬─────────────────────────────────┘
                      │ JNI (Java Native Interface)
┌─────────────────────▼─────────────────────────────────┐
│             JNI Bridge  (unyts_jni.cpp)               │
│   (C++ file implementing Java_*_* entry points)       │
└─────────────────────┬─────────────────────────────────┘
                      │ calls C API  (unyts_capi.h)
┌─────────────────────▼─────────────────────────────────┐
│        C++ Core Library (libunyts.so / .a)            │
│  (compiled for arm64-v8a, armeabi-v7a, x86_64 NDK)   │
│      same source as Windows/iOS core — zero changes   │
└───────────────────────────────────────────────────────┘
```

### Why JNI?
Android's runtime is the JVM (or ART).  Kotlin/Java code cannot call C++ directly.  JNI is the standard mechanism:
1. Kotlin declares `external fun` methods (native methods)
2. The `.so` library is loaded at runtime via `System.loadLibrary()`
3. The `.so` contains C++ functions with mangled JNI names that implement the `external fun` declarations

The C API (`unyts_capi.h`) keeps the JNI bridge thin — it calls `unyts_convert()` and friends, not the C++ classes directly.

---

## 3. Technology Stack

| Component | Choice | Rationale |
|---|---|---|
| UI framework | Jetpack Compose | Android's modern declarative UI; Material 3 out of the box |
| Language (UI) | Kotlin | Google's primary Android language; concise, coroutine-friendly |
| Native bridge | JNI + Android NDK | Standard Android native code integration |
| C++ standard | C++17 | Same as Windows/iOS core |
| Build system (core) | CMake + `externalNativeBuild` in Gradle | Gradle orchestrates CMake; NDK provides cross-compilation |
| Build system (app) | Gradle (Kotlin DSL) | Standard Android toolchain |
| Distribution | Google Play (AAB) | Standard Android distribution |
| Min Android version | API 26 (Android 8.0) | Covers ~95% of active Android devices; modern JNI features |

---

## 4. Project Structure

```
unyts_android/                        ← Android Studio project root
├── app/
│   ├── build.gradle.kts               ← declares externalNativeBuild + abiFilters
│   ├── CMakeLists.txt                 ← builds libunyts.so for Android
│   └── src/
│       └── main/
│           ├── AndroidManifest.xml
│           ├── cpp/
│           │   ├── unyts_jni.cpp      ← JNI bridge implementation
│           │   └── CMakeLists.txt     ← links against C++ core sources
│           ├── kotlin/com/unyts/app/
│           │   ├── MainActivity.kt
│           │   ├── jni/
│           │   │   ├── UnytsJNI.kt    ← declares `external` functions
│           │   │   └── UnytsService.kt← Kotlin coroutine wrapper
│           │   ├── ui/
│           │   │   ├── theme/
│           │   │   │   ├── Theme.kt
│           │   │   │   └── Color.kt
│           │   │   ├── ConvertScreen.kt
│           │   │   ├── SettingsScreen.kt
│           │   │   └── HistoryScreen.kt
│           │   └── viewmodel/
│           │       └── ConvertViewModel.kt
│           └── res/
│               ├── drawable/
│               │   └── ic_launcher.xml
│               └── values/
│                   └── strings.xml
├── core/                              ← symlink or submodule to shared C++ core
│   ├── include/unyts/unyts_capi.h
│   └── src/ (all .cpp files)
└── build.gradle.kts                   ← project-level
```

---

## 5. Building the C++ Core for Android

Android NDK cross-compilation is configured in `build.gradle.kts` and `CMakeLists.txt`:

```kotlin
// app/build.gradle.kts (relevant section)
android {
    defaultConfig {
        ndk {
            abiFilters += listOf("arm64-v8a", "armeabi-v7a", "x86_64")
        }
        externalNativeBuild {
            cmake {
                cppFlags += "-std=c++17"
                arguments += listOf(
                    "-DANDROID_STL=c++_shared",
                    "-DUNYTS_BUILD_CAPI=ON"
                )
            }
        }
    }
    externalNativeBuild {
        cmake {
            path = file("CMakeLists.txt")
            version = "3.22.1"
        }
    }
}
```

```cmake
# app/CMakeLists.txt
cmake_minimum_required(VERSION 3.22.1)
project(unyts_android)

# Include shared C++ core sources
add_subdirectory(../core unyts_core)

# JNI bridge library
add_library(unyts_jni SHARED src/main/cpp/unyts_jni.cpp)
target_link_libraries(unyts_jni
    unyts_core          # C++ core
    android             # Android NDK
    log                 # Android logging
)
```

Gradle triggers CMake automatically during the build.  No manual invocation needed.

---

## 6. JNI Bridge

```cpp
// src/main/cpp/unyts_jni.cpp
#include <jni.h>
#include <android/log.h>
#include "unyts_capi.h"

#define LOG_TAG "UnytsJNI"
#define LOGD(...)  __android_log_print(ANDROID_LOG_DEBUG, LOG_TAG, __VA_ARGS__)

// Singleton context (created once, lives for app lifetime)
static UnytsContext* g_ctx = nullptr;

extern "C" {

JNIEXPORT void JNICALL
Java_com_unyts_app_jni_UnytsJNI_nativeInit(JNIEnv*, jobject) {
    if (!g_ctx) g_ctx = unyts_create();
}

JNIEXPORT void JNICALL
Java_com_unyts_app_jni_UnytsJNI_nativeDestroy(JNIEnv*, jobject) {
    if (g_ctx) { unyts_destroy(g_ctx); g_ctx = nullptr; }
}

JNIEXPORT jdoubleArray JNICALL
Java_com_unyts_app_jni_UnytsJNI_nativeConvert(
        JNIEnv* env, jobject,
        jdouble value, jstring fromUnit, jstring toUnit)
{
    const char* from = env->GetStringUTFChars(fromUnit, nullptr);
    const char* to   = env->GetStringUTFChars(toUnit,   nullptr);
    double out = 0.0;
    char path[512] = {};
    int rc = unyts_convert(g_ctx, value, from, to, &out, path, sizeof(path));
    env->ReleaseStringUTFChars(fromUnit, from);
    env->ReleaseStringUTFChars(toUnit,   to);

    // Return [status_code, result_value] as double array;
    // caller reads path via a separate nativeLastPath() call
    jdoubleArray arr = env->NewDoubleArray(2);
    jdouble buf[2] = { (jdouble)rc, out };
    env->SetDoubleArrayRegion(arr, 0, 2, buf);
    return arr;
}

JNIEXPORT jstring JNICALL
Java_com_unyts_app_jni_UnytsJNI_nativeLastPath(JNIEnv* env, jobject) {
    // Simplified: in production, store last path in a thread_local
    return env->NewStringUTF("");
}

JNIEXPORT jboolean JNICALL
Java_com_unyts_app_jni_UnytsJNI_nativeConvertible(
        JNIEnv* env, jobject, jstring fromUnit, jstring toUnit)
{
    const char* from = env->GetStringUTFChars(fromUnit, nullptr);
    const char* to   = env->GetStringUTFChars(toUnit,   nullptr);
    int rc = unyts_convertible(g_ctx, from, to);
    env->ReleaseStringUTFChars(fromUnit, from);
    env->ReleaseStringUTFChars(toUnit,   to);
    return (jboolean)(rc != 0);
}

JNIEXPORT jobjectArray JNICALL
Java_com_unyts_app_jni_UnytsJNI_nativeAllUnits(JNIEnv* env, jobject) {
    char buf[1 << 20]; // 1 MB buffer; units are newline-delimited
    unyts_all_units(g_ctx, buf, sizeof(buf));
    // split buf by '\n' and build a String[] — see full implementation
    return nullptr; // placeholder
}

JNIEXPORT void JNICALL
Java_com_unyts_app_jni_UnytsJNI_nativeSetFvf(JNIEnv*, jobject, jdouble fvf) {
    unyts_set_fvf(g_ctx, fvf);
}

} // extern "C"
```

---

## 7. Kotlin JNI Wrapper and Service

```kotlin
// UnytsJNI.kt
package com.unyts.app.jni

object UnytsJNI {
    init { System.loadLibrary("unyts_jni") }

    external fun nativeInit()
    external fun nativeDestroy()
    external fun nativeConvert(value: Double, fromUnit: String, toUnit: String): DoubleArray
    external fun nativeLastPath(): String
    external fun nativeConvertible(fromUnit: String, toUnit: String): Boolean
    external fun nativeAllUnits(): Array<String>
    external fun nativeSetFvf(fvf: Double)
    external fun nativeGetFvf(): Double
}
```

```kotlin
// UnytsService.kt
package com.unyts.app.jni

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class UnytsService {
    init { UnytsJNI.nativeInit() }

    val allUnits: List<String> by lazy {
        UnytsJNI.nativeAllUnits().toList()
    }

    suspend fun convert(value: Double, from: String, to: String)
        : Result<Pair<Double, String>> = withContext(Dispatchers.Default)
    {
        runCatching {
            val arr = UnytsJNI.nativeConvert(value, from, to)
            val status = arr[0].toInt()
            if (status != 0) error("Conversion failed: $from → $to")
            val path = UnytsJNI.nativeLastPath()
            Pair(arr[1], path)
        }
    }

    fun isConvertible(from: String, to: String): Boolean =
        UnytsJNI.nativeConvertible(from, to)

    fun setFvf(fvf: Double) = UnytsJNI.nativeSetFvf(fvf)
    fun getFvf(): Double    = UnytsJNI.nativeGetFvf()
}
```

---

## 8. Jetpack Compose UI

```kotlin
// ConvertScreen.kt (simplified)
@Composable
fun ConvertScreen(viewModel: ConvertViewModel) {
    val state by viewModel.uiState.collectAsState()

    Column(modifier = Modifier.padding(16.dp).fillMaxSize()) {
        Text("Unyts Converter",
             style = MaterialTheme.typography.headlineMedium)
        Spacer(Modifier.height(16.dp))

        // From section
        UnitAutoCompleteField(
            label     = "From unit",
            value     = state.fromUnit,
            onChange  = viewModel::onFromUnitChange,
            allUnits  = state.allUnits
        )
        OutlinedTextField(
            value    = state.fromValue,
            onValueChange = viewModel::onFromValueChange,
            label    = { Text("Value") },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
            modifier = Modifier.fillMaxWidth()
        )
        Spacer(Modifier.height(8.dp))

        // To section
        UnitAutoCompleteField(
            label    = "To unit",
            value    = state.toUnit,
            onChange = viewModel::onToUnitChange,
            allUnits = state.allUnits
        )
        OutlinedTextField(
            value         = state.toValue,
            onValueChange = {},
            label         = { Text("Result") },
            readOnly      = true,
            modifier      = Modifier.fillMaxWidth()
        )
        Spacer(Modifier.height(12.dp))

        Button(onClick   = viewModel::onConvert,
               modifier  = Modifier.fillMaxWidth()) {
            Text("Convert")
        }

        if (state.pathString.isNotEmpty()) {
            Text(state.pathString,
                 style    = MaterialTheme.typography.bodySmall,
                 color    = MaterialTheme.colorScheme.onSurfaceVariant,
                 modifier = Modifier.padding(top = 8.dp))
        }
        if (state.errorMessage.isNotEmpty()) {
            Text(state.errorMessage,
                 color    = MaterialTheme.colorScheme.error,
                 modifier = Modifier.padding(top = 4.dp))
        }
    }
}
```

`UnitAutoCompleteField` is a custom composable wrapping `OutlinedTextField` + a `DropdownMenu` that shows filtered suggestions as the user types.

Additional screens:
- `SettingsScreen` — FVF input, algorithm selector, timeout
- `HistoryScreen` — optional list of recent conversions using Room or `DataStore`

---

## 9. Phased Delivery Plan

### Phase 0 — Prerequisites (parallel with C++ core Phase 1–3)
- Install Android Studio (Flamingo or later), NDK 25+, CMake 3.22+
- Verify NDK cross-compilation of a hello-world C++ JNI library for arm64-v8a
- Create Android Studio project with `externalNativeBuild` wired to CMake
- Set up Google Play developer account ($25 one-time fee)

### Phase 1 — JNI Bridge (1–2 weeks)
- Write `unyts_jni.cpp` implementing all JNI entry points
- Write `UnytsJNI.kt` with `external fun` declarations
- Write Android instrumented tests calling `UnytsService.convert()`
- **Milestone**: `convert(1.0, "meter", "foot")` returns `3.28084` in a JUnit test on emulator

### Phase 2 — Core UI (2–3 weeks)
- Implement `ConvertScreen` with unit fields, value fields, convert button
- Implement `UnitAutoCompleteField` with real-time filtering
- `ConvertViewModel` with `StateFlow` for reactive UI updates
- Handle keyboard management, input validation, error display
- Phone layout + tablet adaptive layout (WindowSizeClass)
- **Milestone**: basic conversion works on emulator (Pixel 6 API 33)

### Phase 3 — Settings + Extras (1–2 weeks)
- `SettingsScreen`: FVF, algorithm picker, timeout, print-path toggle
- Persist settings via `DataStore<Preferences>`
- Optional `HistoryScreen` using Room database
- Material 3 dynamic colour theming (Android 12+)
- **Milestone**: settings survive app restart; FVF-dependent conversions work

### Phase 4 — Polish + Device Testing (1–2 weeks)
- Test on real Android hardware (Samsung, Pixel, different API levels)
- Accessibility audit (content descriptions on all interactive elements)
- Adaptive icon (foreground + background layers)
- Handle system back gesture, lifecycle events (rotation, backgrounding)
- ProGuard/R8 rules for the JNI `external fun` declarations

### Phase 5 — Google Play Submission (1 week)
- Build release AAB: `./gradlew bundleRelease`
- Sign with a keystore (`keytool` + `signingConfigs` in Gradle)
- Google Play Console: upload AAB, store listing, screenshots (phone + tablet)
- Internal test → Closed testing → Production rollout

---

## 10. Effort Estimate

| Phase | Duration |
|---|---|
| 0 — Prerequisites | 3–5 days |
| 1 — JNI bridge | 1–2 weeks |
| 2 — Core UI | 2–3 weeks |
| 3 — Settings + extras | 1–2 weeks |
| 4 — Polish + device testing | 1–2 weeks |
| 5 — Google Play submission | 1 week |
| **Total (after C++ core done)** | **~2–2.5 months** |

> **Dependency**: The C++ core (Phases 1–4 of [PLAN_CPP_WINDOWS.md]) must be complete before Phase 1 of this plan can begin.  
> **iOS + Android in parallel**: Because the UI work is independent after the C++ core is done, the iOS and Android UIs can be developed simultaneously by two developers, reducing total mobile delivery time to ~2.5 months after the core is complete.

---

## 11. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| NDK ABI fragmentation (arm64-v8a vs armeabi-v7a) | Low | Medium | Build all ABIs in `abiFilters`; test on arm64 device primarily |
| JNI memory leaks (failing to `ReleaseStringUTFChars`, `DeleteLocalRef`) | Medium | Medium | Code review every JNI function; use RAII wrappers for JNI strings |
| C++ exceptions not propagated through JNI | High (by default) | High | Wrap every JNI function body in `try/catch`; convert to error codes before returning to Java |
| NDK version / STL incompatibility | Low | Medium | Pin to `c++_shared` STL; document NDK version in README |
| Large `.so` file increasing APK size | Low | Low | Enable LTO in release build; strip debug symbols |
| Google Play review rejection | Low | Low | Unyts is a benign utility app; no unusual permissions required |
| ProGuard stripping JNI bridge Kotlin class | Medium | Medium | Add `-keep class com.unyts.app.jni.UnytsJNI { *; }` to `proguard-rules.pro` |

---

## 12. Prerequisites / Tools Required

| Tool | Notes |
|---|---|
| Android Studio (Flamingo+) | Official Android IDE; includes emulator |
| Android NDK 25+ | Cross-compilation toolchain for C++ |
| CMake 3.22+ | Bundled with Android Studio via SDK Manager |
| Google Play developer account | $25 one-time registration fee |
| Physical Android device (optional) | arm64-v8a; test early for JNI issues |
| C++ core built (Phases 1–4 of Windows plan) | The `.cpp` sources are added as `add_subdirectory` |

---

## 13. Code Shared with iOS

The sharing strategy with iOS is identical to what is shared with Windows:

| Component | Shared? |
|---|---|
| C++ core engine (`core/`) | **100%** — compiled with NDK toolchain |
| C API (`unyts_capi.h`) | **100%** — same header, same semantics |
| JNI bridge (`unyts_jni.cpp`) | **0%** — Android-specific JNI entry points |
| Kotlin UI | **0%** — Android only |

The iOS Objective-C++ bridge (`UnytsWrapper.mm`) and the Android JNI bridge (`unyts_jni.cpp`) are both calling the same `unyts_capi.h` functions.  They are the smallest components of their respective apps — typically a few hundred lines each.

---

## 14. Cross-Platform Summary

```
┌──────────────────────────────────────────────────────────────────────┐
│                 Shared C++ Core  (core/)                             │
│  graph, search, registry, converter, parameters, database, capi      │
│  ~3,000–4,000 lines C++17 — compiled once per target platform        │
└──────────┬──────────────────────┬──────────────────────┬─────────────┘
           │                      │                      │
  ┌────────▼─────────┐   ┌────────▼─────────┐  ┌────────▼──────────┐
  │  Qt 6 Windows    │   │  iOS (Swift)      │  │  Android (Kotlin) │
  │  gui_windows/    │   │  bridge_ios/      │  │  bridge_android/  │
  │  Qt Widgets      │   │  Obj-C++ + SwiftUI│  │  JNI + Compose    │
  │  ~1,000 lines    │   │  ~600 lines bridge│  │  ~500 lines bridge│
  │  + CMake/WiX     │   │  + ~800 lines UI  │  │  + ~800 lines UI  │
  └──────────────────┘   └───────────────────┘  └───────────────────┘
```

The C++ core is the single most valuable investment — once built and tested, it powers all three platforms at no additional cost.
