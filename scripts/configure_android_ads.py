#!/usr/bin/env python3
"""Apply the app ID to generated Capacitor Android, and enforce target/min SDK.
Requires `npx cap add android` and `npx cap sync android` to have completed.
"""
import os, re
from pathlib import Path
root=Path('android')
app_id = os.environ.get('ADMOB_APP_ID') or 'ca-app-pub-6081700970691881~6352526941'
if not re.fullmatch(r'ca-app-pub-\d+~\d+',app_id):
    raise SystemExit('Invalid ADMOB_APP_ID: expected ca-app-pub-NUMBERS~NUMBERS')
manifest=root/'app/src/main/AndroidManifest.xml'
xml=manifest.read_text()
if 'com.google.android.gms.ads.APPLICATION_ID' not in xml:
    xml=xml.replace('<application', '<application', 1)
    match=re.search(r'<application\b[^>]*>',xml,re.S)
    if not match: raise SystemExit('Application manifest node not found')
    xml=xml[:match.end()]+'\n        <meta-data android:name="com.google.android.gms.ads.APPLICATION_ID" android:value="@string/admob_app_id" />'+xml[match.end():]
manifest.write_text(xml)
strings=root/'app/src/main/res/values/strings.xml'
data=strings.read_text()
if '<string name="admob_app_id">' not in data:
    data=data.replace('</resources>', '    <string name="admob_app_id">'+app_id+'</string>\n</resources>')
else:
    data=re.sub(r'(<string name="admob_app_id">).*?(</string>)',lambda m:m.group(1)+app_id+m.group(2),data)
strings.write_text(data)
vars=root/'variables.gradle'
v=vars.read_text()
for key,num in [('minSdkVersion',24),('compileSdkVersion',36),('targetSdkVersion',36)]:
    if not re.search(r'\b'+key+r'\s*=',v): raise SystemExit(key+' not found in variables.gradle')
    v=re.sub(r'(\b'+key+r'\s*=\s*)\d+',lambda m:m.group(1)+str(num),v)
vars.write_text(v)
print('AndroidManifest AdMob app ID configured; compile/target=36 min=24')
