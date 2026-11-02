#!/usr/bin/env python3
"""Enable Gradle release signing only when GitHub Secrets provide a real keystore."""
import os,re,base64
from pathlib import Path
names=['ANDROID_KEYSTORE_BASE64','ANDROID_KEYSTORE_PASSWORD','ANDROID_KEY_ALIAS','ANDROID_KEY_PASSWORD']
secrets=[os.environ.get(n,'') for n in names]
if not all(secrets):
    Path('www/signing-status.txt').write_text('UNSIGNED AAB - configure all Android signing secrets before publishing\n')
    print('Unsigned release AAB. Set all Android signing secrets for Play Store release.')
    raise SystemExit(0)
blob=base64.b64decode(secrets[0],validate=True)
if len(blob)<64: raise SystemExit('Keystore secret is too short')
key=Path('android/arrow-release.keystore')
key.write_bytes(blob)
app=Path('android/app/build.gradle')
gradle=app.read_text()
if 'signingConfigs {' in gradle:
    raise SystemExit('Existing signingConfigs found; review before enabling automated signing')
# The generated Capacitor app has `buildTypes { release { ... } }`.
if not re.search(r'\bbuildTypes\s*\{\s*release\s*\{',gradle):
    raise SystemExit('Cannot find expected release Gradle buildTypes block')
gradle=re.sub(r'(\bbuildTypes\s*\{\s*release\s*\{)', """signingConfigs {
        release {
            storeFile file('../arrow-release.keystore')
            storePassword System.getenv('ANDROID_KEYSTORE_PASSWORD')
            keyAlias System.getenv('ANDROID_KEY_ALIAS')
            keyPassword System.getenv('ANDROID_KEY_PASSWORD')
        }
    }
    buildTypes {
        release {
            signingConfig signingConfigs.release""",gradle,count=1)
app.write_text(gradle)
Path('www/signing-status.txt').write_text('SIGNED RELEASE AAB - verify Play App Signing enrollment and upload key\n')
print('Gradle release signing configured from environment; keystore is not committed')
