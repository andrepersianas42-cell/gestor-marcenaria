[app]
title = Gestor Marcenaria
package.name = gestormarcenaria
package.domain = org.andresystem
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0.2
requirements = python3,kivy,pillow,pyjnius
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
orientation = portrait
fullscreen = 0
icon.filename = icon.png
android.archs = arm64-v8a
android.allow_backup = True
android.api = 31
android.minapi = 21
android.enable_androidx = True
android.accept_sdk_license = True
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/ios-control/ios-deploy
ios.ios_deploy_branch = 1.10.0

[buildozer]
log_level = 2
warn_on_root = 0
