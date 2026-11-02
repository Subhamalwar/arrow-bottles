const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const cp = require('node:child_process');

const root = path.resolve(__dirname, '..');
const script = fs.readFileSync(path.join(root,'scripts','configure_web_ads.py'),'utf8');
const android = fs.readFileSync(path.join(root,'scripts','configure_android_ads.py'),'utf8');
const bridge = fs.readFileSync(path.join(root,'src','native-ads-bridge.js'),'utf8');
const APP_ID = 'ca-app-pub-6081700970691881~6352526941';
const BANNER_ID = 'ca-app-pub-6081700970691881/7399061483';
function buildAdsConfig(environment={}) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'arrow-adtest-'));
  try {
    fs.mkdirSync(path.join(dir,'www'));
    const py = path.join(dir, 'configure_web_ads.py');
    fs.writeFileSync(py,script);
    const env = {...process.env};
    for (const key of Object.keys(env)) if (key.startsWith('ADMOB_')) delete env[key];
    Object.assign(env,environment);
    const p=cp.spawnSync('python3',[py],{cwd:dir,env,encoding:'utf8'});
    assert.equal(p.status,0,p.stderr);
    const js=fs.readFileSync(path.join(dir,'www','ad-config.js'),'utf8');
    const data=JSON.parse(js.trim().slice('window.ARROW_AD_CONFIG = '.length,-1));
    const status=fs.readFileSync(path.join(dir,'www','ad-status.txt'),'utf8').trim();
    return {data,status};
  } finally {fs.rmSync(dir,{recursive:true,force:true});}
}
test('user AdMob app and Android banner IDs are included in Android configuration', () => {
  assert.ok(android.includes(APP_ID));
  assert.ok(script.includes(BANNER_ID));
});
test('development never uses live publisher ad unit', () => {
  const {data,status}=buildAdsConfig();
  assert.equal(data.isTesting,true);
  assert.equal(data.bannerTesting,true);
  assert.notEqual(data.bannerId,BANNER_ID);
  assert.match(status,/GOOGLE DEMO ADS/);
});
test('banner-only production disables unconfigured rewarded and interstitial units', () => {
  const {data,status}=buildAdsConfig({ADMOB_PRODUCTION:'true'});
  assert.equal(data.bannerId,BANNER_ID);
  assert.equal(data.bannerTesting,false);
  assert.equal(data.rewardedId,'');
  assert.equal(data.interstitialId,'');
  assert.match(status,/PRODUCTION ADS: banner/);
});
test('production additional rewarded/interstitial IDs must be independently supplied', () => {
  const {data}=buildAdsConfig({ADMOB_PRODUCTION:'true',ADMOB_REWARDED_UNIT_ID:'ca-app-pub-123/456',ADMOB_INTERSTITIAL_UNIT_ID:'ca-app-pub-123/789'});
  assert.equal(data.rewardedId,'ca-app-pub-123/456');
  assert.equal(data.interstitialId,'ca-app-pub-123/789');
  assert.equal(data.rewardedTesting,false);
  assert.equal(data.interstitialTesting,false);
});
test('native rewarded ads are only rewarded when SDK returns earned item', () => {
  assert.match(bridge,/return !!\(reward && Number\(reward\.amount\) > 0\)/);
  assert.match(bridge,/bannerTesting/);
  assert.match(bridge,/rewardedTesting/);
  assert.match(bridge,/interstitialTesting/);
});
