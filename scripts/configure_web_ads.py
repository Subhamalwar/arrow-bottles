#!/usr/bin/env python3
"""Build ad configuration. Production ads require ADMOB_PRODUCTION=true.
Live formats can be enabled independently. Unconfigured production formats stay off.
"""
import json, os, re
from pathlib import Path

APP_ID = 'ca-app-pub-6081700970691881~6352526941'
BANNER_ID = 'ca-app-pub-6081700970691881/7399061483'
DEMO_IDS = {
    'rewarded': 'ca-app-pub-3940256099942544/5224354917',
    'interstitial': 'ca-app-pub-3940256099942544/1033173712',
    'banner': 'ca-app-pub-3940256099942544/6300978111'
}
app_id=os.environ.get('ADMOB_APP_ID') or APP_ID
if not re.fullmatch(r'ca-app-pub-\d+~\d+',app_id):
    raise SystemExit('Invalid AdMob app ID')
production=os.environ.get('ADMOB_PRODUCTION','').strip().lower()=='true'
source_ids={
    'rewarded': os.environ.get('ADMOB_REWARDED_UNIT_ID') or '',
    'interstitial': os.environ.get('ADMOB_INTERSTITIAL_UNIT_ID') or '',
    'banner': os.environ.get('ADMOB_BANNER_UNIT_ID') or BANNER_ID
}
config={'isTesting': not production}
active=[]
for kind in ('rewarded','interstitial','banner'):
    id=source_ids[kind]
    if id and not re.fullmatch(r'ca-app-pub-\d+/\d+',id):
        raise SystemExit('Invalid '+kind+' ad unit ID')
    live=production and bool(id)
    config[kind+'Id']=id if live else ('' if production else DEMO_IDS[kind])
    config[kind+'Testing']=not live
    if live: active.append(kind)
Path('www/ad-config.js').write_text('window.ARROW_AD_CONFIG = '+json.dumps(config,separators=(',',':'))+';\n')
status=('PRODUCTION ADS: '+(', '.join(active) if active else 'NO ENABLED FORMATS')+'; others disabled' if production else 'GOOGLE DEMO ADS - NO REVENUE')
Path('www/ad-status.txt').write_text(status+'\n')
print(status)
