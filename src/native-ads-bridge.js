// Native AdMob bridge. Built by `npm run build:web`.
// Google UMP consent MUST succeed before requesting paid ads.
import { Capacitor } from '@capacitor/core';
import { AdMob, AdmobConsentStatus, BannerAdPluginEvents, BannerAdPosition, BannerAdSize } from '@capacitor-community/admob';

const config = window.ARROW_AD_CONFIG || {};
const native = () => Capacitor.isNativePlatform();
let ready = false;
let consentPromise = null;
let bannerVisible = false;
let bannerGeneration = 0;
let bannerListenerRegistered = false;
let pendingReward = false;
let pendingInterstitial = false;
const adStatus = { platform: native() ? 'android-native' : 'browser', consent: 'not-checked', sdk: 'not-initialized', banner: 'not-requested', bannerError: '', rewarded: 'not-requested', rewardedError: '', bannerUnitMode: config.bannerTesting ? 'Google demo' : 'production' };
const describeError = e => String((e && (e.message || e.code)) || e || 'unknown error').slice(0, 400);
const diagnostics = () => ({...adStatus, native: native(), consentAllowed: !!ready, bannerId: config.bannerId || '(missing)', appId: 'ca-app-pub-6081700970691881~6352526941'});
const setInset = pixels => document.documentElement.style.setProperty('--native-banner-height', Math.max(0, pixels || 0) + 'px');
const configured = id => /^ca-app-pub-\d+\/\d+$/.test(id || '');

async function ensureReady() {
  if (!native()) { adStatus.sdk = 'unavailable-in-browser'; return false; }
  if (ready) return true;
  if (consentPromise) return consentPromise;
  consentPromise = (async () => {
    try {
      adStatus.consent = 'requesting';
      let state = await AdMob.requestConsentInfo();
      if (state.isConsentFormAvailable && state.status === AdmobConsentStatus.REQUIRED) {
        state = await AdMob.showConsentForm();
      }
      adStatus.consent = state.canRequestAds ? 'allowed' : ('blocked:' + state.status);
      if (!state.canRequestAds) return false;
      adStatus.sdk = 'initializing';
      await AdMob.initialize();
      adStatus.sdk = 'ready';
      ready = true;
      return true;
    } catch (e) {
      adStatus.sdk = 'failed: ' + describeError(e);
      console.warn('[admob] SDK/UMP initialization unavailable', e);
      return false;
    }
  })();
  const ok = await consentPromise;
  if (!ok) consentPromise = null; // allow retry after network recovers
  return ok;
}

async function rewarded() {
  if (pendingReward || !configured(config.rewardedId)) { adStatus.rewarded = 'unavailable-or-pending'; return false; }
  pendingReward = true;
  adStatus.rewarded = 'loading';
  try {
    if (!await ensureReady()) return false;
    await AdMob.prepareRewardVideoAd({adId: config.rewardedId, isTesting: !!config.rewardedTesting});
    const reward = await AdMob.showRewardVideoAd();
    adStatus.rewarded = reward && Number(reward.amount) > 0 ? 'earned' : 'dismissed-without-reward';
    return !!(reward && Number(reward.amount) > 0); // never grant on dismiss or ad click
  } catch (e) {
    adStatus.rewarded = 'failed'; adStatus.rewardedError = describeError(e);
    console.warn('[admob] rewarded request failed', e);
    return false;
  } finally { pendingReward = false; }
}

async function interstitial() {
  if (pendingInterstitial || !configured(config.interstitialId)) return false;
  pendingInterstitial = true;
  try {
    if (!await ensureReady()) return false;
    await AdMob.prepareInterstitial({adId: config.interstitialId, isTesting: !!config.interstitialTesting});
    await AdMob.showInterstitial();
    return true;
  } catch (e) {
    console.warn('[admob] interstitial request failed', e);
    return false;
  } finally { pendingInterstitial = false; }
}

async function showBanner() {
  if (!configured(config.bannerId)) { adStatus.banner = 'invalid-unit-id'; return false; }
  const requestId = ++bannerGeneration;
  adStatus.banner = 'requesting'; adStatus.bannerError = '';
  if (!await ensureReady()) { adStatus.banner = 'blocked-by-consent-or-sdk'; return false; }
  if (requestId !== bannerGeneration) { adStatus.banner = 'cancelled-by-navigation'; return false; }
  if (!bannerListenerRegistered) {
    await AdMob.addListener(BannerAdPluginEvents.SizeChanged, size => {
      if (bannerVisible) setInset(Number(size.height) || 0);
    });
    await AdMob.addListener(BannerAdPluginEvents.Loaded, () => { adStatus.banner = 'loaded'; });
    await AdMob.addListener(BannerAdPluginEvents.FailedToLoad, error => { adStatus.banner = 'failed-to-load'; adStatus.bannerError = describeError(error); });
    bannerListenerRegistered = true;
  }
  try {
    bannerVisible = true; // Count SizeChanged events fired during showBanner loading.
    await AdMob.showBanner({adId: config.bannerId, adSize: BannerAdSize.ADAPTIVE_BANNER,
      position: BannerAdPosition.BOTTOM_CENTER, margin: 0, isTesting: !!config.bannerTesting});
    if (requestId !== bannerGeneration) { await hideBanner(); return false; }
    bannerVisible = true;
    if (adStatus.banner !== 'loaded') adStatus.banner = 'show-request-accepted';
    return true;
  } catch (e) {
    bannerVisible = false;
    setInset(0);
    adStatus.banner = 'failed'; adStatus.bannerError = describeError(e);
    console.warn('[admob] banner unavailable', e);
    return false;
  }
}
async function hideBanner() {
  bannerGeneration++;
  bannerVisible = false;
  adStatus.banner = 'hidden';
  setInset(0);
  if (native()) { try { await AdMob.removeBanner(); } catch (e) { console.warn('[admob] banner removal', e); } }
}
window.ABNativeAds = { isNative: native, available: () => native() && !!configured(config.rewardedId),
  ensureReady, rewarded, interstitial, showBanner, hideBanner, diagnostics,
  privacyOptions: async () => { if (native()) await AdMob.showPrivacyOptionsForm(); } };
