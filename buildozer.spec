[app]
title = Gestor Marcenaria
package.name = gestormarcenaria
package.domain = org.andresystem
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0.1
requirements = python3,kivy==2.3.1,matplotlib,numpy,pillow
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
orientation = portrait
fullscreen = 0
icon.filename = icon.png
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.api = 33
android.minapi = 21
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/ios-control/ios-deploy
ios.ios_deploy_branch = 1.10.0

[buildozer]
log_level = 2
warn_on_root = 1
