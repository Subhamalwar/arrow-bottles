// Fallback for offline browser preview; replaced by `npm run build:web` in Android CI.
window.ABNativeAds = { available: () => false, rewarded: async () => false,
  interstitial: async () => false, showBanner: async () => false, hideBanner: async () => {} };
