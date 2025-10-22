[app]

# (str) Title of your application
title = Kv Game

# (str) Package name (must be lowercase, no spaces)
package.name = kvgame

# (str) Package domain (reverse-DNS style)
package.domain = org.test

# (str) Source code directory (where main.py is located)
source.dir = .

# (list) File types to include when packaging your app
source.include_exts = py,png,jpg,kv,atlas,ogg,wav,mp3,ttf,json,txt,xml,ini

# (str) Version number
version = 0.1

# (list) Application requirements
# Do NOT specify Python version explicitly; use python3
requirements = python3,kivy

# (list) Garden requirements (optional)
# garden_requirements = 

# (str) Presplash screen (optional)
# presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon for the app (optional)
# icon.filename = %(source.dir)s/data/icon.png

# (list) Supported screen orientations
orientation = portrait

# (bool) Fullscreen mode (1 for fullscreen)
fullscreen = 0

# (bool) Disable signing for testing (no Apple ID required)
ios.codesign.allowed = false

# (bool) Hide the status bar
# android.hide_statusbar = 1

# (bool) Enable keyboard mode on focus
# keyboard_mode = docked

# (str) Custom entry point (usually main.py)
# entrypoint = main.py

# (bool) Enable storage access
# android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (str) Application category (for iOS App Store metadata)
# ios.category = Games

# (str) Author details
author = John Developer
author.email = johndev@example.com

# (str) Description
description = A simple Kivy-based game built for Android and iOS.


#
# ANDROID CONFIGURATION
#
[android]

# (int) Target Android API (use latest you have installed)
android.api = 31

# (int) Minimum Android API your APK will support
android.minapi = 21

# (str) Android SDK path (auto-downloaded if empty)
android.sdk_path = /home/ngugi/.buildozer/android/platform/android-sdk

# (str) Android NDK path (auto-downloaded if empty)
android.ndk_path = /home/ngugi/.buildozer/android/platform/android-ndk-r25b

# (str) NDK version
android.ndk = 25b

# (int) NDK API version (usually matches minapi)
android.ndk_api = 21

# (list) Supported CPU architectures
android.archs = arm64-v8a, armeabi-v7a

# (bool) Copy Python libraries directly into the APK
android.copy_libs = 1

# (bool) Enable AndroidX
android.enable_androidx = True

# (bool) Allow auto backup
android.allow_backup = True

# (bool) Enable the use of the Android logcat
android.logcat_filters = *:S python:D

# (str) Debug artifact format (apk or aab)
android.debug_artifact = apk

# (str) Release artifact format
android.release_artifact = aab

# (bool) Automatically accept SDK licenses
android.accept_sdk_license = True

# (bool) Skip SDK updates (speeds up subsequent builds)
# android.skip_update = True

# (str) Fix PyJNIus compatibility
recipe.versions.pyjnius = 1.5.0

# (list) Permissions (add if needed)
# android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (str) Keystore for release signing
# android.release_keystore = my-release-key.keystore
# android.release_keyalias = myalias
# android.release_keyalias_passwd = mypassword
# android.release_keystore_passwd = mykeystorepassword

# (bool) Add ARMv7a fallback for compatibility
android.add_libs_armeabi_v7a = True


#
# iOS CONFIGURATION
#
[ios]

# (str) Kivy-iOS repository
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master

# (str) iOS-deploy (for testing on device)
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.10.0

# (str) Minimum supported iOS version
ios.min_version = 12.0

# (list) Supported architectures (modern iPhones use arm64)
ios.archs = arm64

# (bool) Include debug symbols
ios.debug_symbols = True

# (bool) Disable signing for testing (no Apple ID required)
#ios.codesign.allowed = false

# (str) Team ID for App Store submission (if applicable)
# ios.codesign.team_id = YOUR_TEAM_ID

# (str) Provisioning profile for App Store
# ios.codesign.provisioning_profile = your_profile.mobileprovision

# (bool) Enable verbose Xcode build logs
ios.verbose = 1

# (str) Extra system frameworks (if required)
# ios.extra_frameworks = Metal,AVFoundation

# (bool) Enable simulator build
# ios.simulator = True


#
# BUILDOZER CONFIGURATION
#
[buildozer]

# (int) Log verbosity (0 = errors only, 1 = info, 2 = debug)
log_level = 2

# (int) Warn if run as root (1 = yes)
warn_on_root = 1

# (str) Directory where build artifacts are stored
build_dir = .buildozer

# (str) Directory where .apk/.aab/.ipa output files go
bin_dir = bin

# (bool) Accept Android SDK licenses automatically
android.accept_sdk_license = True

# (bool) Use system Python (recommended: False)
use_system_python = False

# (bool) Clean build before packaging
# clean_build = True

# (str) Default command to run (optional)
# cmd_default = android debug deploy run

# (bool) Hide Buildozer’s virtualenv activation notice
# quiet = True

# (bool) Auto-restart on code changes (development use)
# watch = True

