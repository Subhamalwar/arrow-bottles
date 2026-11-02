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
const setInset = pixels => document.documentElement.style.setProperty('--native-banner-height', Math.max(0, pixels || 0) + 'px');
const configured = id => /^ca-app-pub-\d+\/\d+$/.test(id || '');

async function ensureReady() {
  if (!native()) return false;
  if (ready) return true;
  if (consentPromise) return consentPromise;
  consentPromise = (async () => {
    try {
      let state = await AdMob.requestConsentInfo();
      if (state.isConsentFormAvailable && state.status === AdmobConsentStatus.REQUIRED) {
        state = await AdMob.showConsentForm();
      }
      if (!state.canRequestAds) return false;
      await AdMob.initialize();
      ready = true;
      return true;
    } catch (e) {
      console.warn('[admob] SDK/UMP initialization unavailable', e);
      return false;
    }
  })();
  const ok = await consentPromise;
  if (!ok) consentPromise = null; // allow retry after network recovers
  return ok;
}

async function rewarded() {
  if (pendingReward || !configured(config.rewardedId)) return false;
  pendingReward = true;
  try {
    if (!await ensureReady()) return false;
    await AdMob.prepareRewardVideoAd({adId: config.rewardedId, isTesting: !!config.rewardedTesting});
    const reward = await AdMob.showRewardVideoAd();
    return !!(reward && Number(reward.amount) > 0); // never grant on dismiss or ad click
  } catch (e) {
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
  if (!configured(config.bannerId)) return false;
  const requestId = ++bannerGeneration;
  if (!await ensureReady() || requestId !== bannerGeneration) return false;
  if (!bannerListenerRegistered) {
    await AdMob.addListener(BannerAdPluginEvents.SizeChanged, size => {
      if (bannerVisible) setInset(Number(size.height) || 0);
    });
    bannerListenerRegistered = true;
  }
  try {
    bannerVisible = true; // Count SizeChanged events fired during showBanner loading.
    await AdMob.showBanner({adId: config.bannerId, adSize: BannerAdSize.ADAPTIVE_BANNER,
      position: BannerAdPosition.BOTTOM_CENTER, margin: 0, isTesting: !!config.bannerTesting});
    if (requestId !== bannerGeneration) { await hideBanner(); return false; }
    bannerVisible = true;
    return true;
  } catch (e) {
    bannerVisible = false;
    setInset(0);
    console.warn('[admob] banner unavailable', e);
    return false;
  }
}
async function hideBanner() {
  bannerGeneration++;
  bannerVisible = false;
  setInset(0);
  if (native()) { try { await AdMob.removeBanner(); } catch (e) { console.warn('[admob] banner removal', e); } }
}
window.ABNativeAds = { isNative: native, available: () => native() && !!configured(config.rewardedId),
  ensureReady, rewarded, interstitial, showBanner, hideBanner,
  privacyOptions: async () => { if (native()) await AdMob.showPrivacyOptionsForm(); } };
