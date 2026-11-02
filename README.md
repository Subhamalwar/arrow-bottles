# Arrow Escape — Android source (v2.0)

Timed arrow-path puzzle built with HTML5/CSS/JavaScript and Capacitor 8. This repo keeps the original app ID (`com.arrowbottles.game`) so updates preserve your on-device app storage. The displayed app name is **Arrow Escape**.

## What is implemented

- All **300 campaign boards** are kept and sorted by measured complexity (arrow count and total path cells). Arrow count never drops when advancing to the next level; tie levels have a progressively tighter countdown. The former repeating easy → medium → boss cadence is removed. All 300 layouts are verified solvable with the included session solver.
- Timed campaign/daily play instead of move-limited failure. A blocked tap costs **2 seconds**; Shield protects it; Undo refunds the last blocked penalty. Practice/tutorial remains untimed. Stars still reflect accurate taps.
- Countdown pauses when opening the pause panel, leaving the app, or seeing reward/failure panels, and resumes with saved remaining time. Old saves from move-based versions get a fresh countdown.
- After time expires, players may get **up to two 20-second extensions per attempt** via eligible rewarded video, coins, or VIP entitlement. Count persists across app restarts. On giving up or after both extensions, retry/map remains available.
- Rewarded ad offers: **double coins on every paid campaign win**, gems, spin extras, hearts, bottle rewards, and time extension. One reward is granted only after the native Google Mobile Ads SDK confirms it; failed/skipped native ads never pay out.
- In the Android build, optional **AdMob banner** on the map after Level 30, and frequency-capped interstitial ads between won levels. Banner is native and the WebView is inset to avoid obscuring controls.
- Google's UMP consent flow is called before the mobile ads SDK initializes; a privacy-choice entry point is present in Settings.
- **Google Play Billing is not integrated.** Native app real-money IAP buttons are labelled *Coming soon* / disabled. Browser simulator is for QA only. Do not sell virtual items without validated purchases.
- Debug APK and release AAB GitHub Actions workflow, with optional signing secrets, Android target SDK 36 and minimum SDK **24** (required by the AdMob plugin).

## How to build using GitHub on Android tablet

1. Upload the extracted contents of this folder into the root of your GitHub repository, replacing the matching files, and remove any old nested `.github/workflows/.github/...` workflow files.
2. In GitHub, open **Actions → Build Arrow Escape Android → Run workflow**, or push the changes to `main`.
3. The workflow installs Node/Capacitor/AdMob dependencies, runs tests, bundles the native bridge, creates Android, configures the manifest, then builds `app-debug.apk` and `app-release.aab`.
4. Open the successful run and download `arrow-escape-android-*` from **Artifacts**.
5. Install the APK and test Levels 1–10, Level 30, pause/restore, timer expiry, both extensions, rewards, ads, and rotation on your own Android device.

### AdMob setup before enabling real monetisation

The Android source has your **AdMob app ID** `ca-app-pub-6081700970691881~6352526941` and your **live Android banner unit** `ca-app-pub-6081700970691881/7399061483` included as build defaults. AdMob identifiers are public config, not passwords; both can be overridden with GitHub Actions secrets. **All ads use Google's official demo units until production is explicitly enabled.**

In GitHub **Settings → Secrets and variables → Actions**, add the repository **variable** `ADMOB_PRODUCTION` with value `true` only when the AdMob app is ready, its privacy/consent messages are configured, and you intend to serve real ads. When enabled, your supplied banner ID is used; missing rewarded and interstitial unit IDs are **disabled**, not silently replaced with demo ads.

When ready to add additional formats, create the **Android Rewarded** and **Interstitial** ad units in AdMob, then add these repository **secrets**:

- `ADMOB_REWARDED_UNIT_ID` (format `ca-app-pub-.../...`)
- `ADMOB_INTERSTITIAL_UNIT_ID` (format `ca-app-pub-.../...`)

Optional overrides: `ADMOB_APP_ID` and `ADMOB_BANNER_UNIT_ID` (both already configured in the code). The generated `www/ad-status.txt` tells you exactly which formats are live. Google demo units generate **no revenue**. Do not click your own live ads; use demo IDs or register test devices while testing.

**No Google Play login is needed.** Google Play Games sign-in and cloud saves would be separate features and are not integrated here; guest/offline gameplay remains available.

### Optional Play Store signing

For signed release builds add four repository **secrets**:

- `ANDROID_KEYSTORE_BASE64` (your keystore file encoded with base64, no surrounding quotes)
- `ANDROID_KEYSTORE_PASSWORD`
- `ANDROID_KEY_ALIAS`
- `ANDROID_KEY_PASSWORD`

If not provided, the AAB is **unsigned** and **cannot be submitted directly** to Google Play. Keep your upload key secure; do not commit the keystore. Check `www/signing-status.txt` inside the build artifact. Play Console listing, testing, app signing enrollment and policy declarations are separate release steps.

## Local development

```sh
npm install
npm test
npm run build:web
npx cap add android
npx cap sync android
python3 scripts/configure_android_ads.py
python3 scripts/configure_android_signing.py
cd android && ./gradlew assembleDebug bundleRelease
```

`npm run build:web` replaces the browser-only `www/native-ads-bridge.js` stub with the real Capacitor/AdMob JS bridge. **Never publish using the stub.** The workflow does this automatically. For web preview, demo UI ads and demo purchases do not produce real income.

## Validation and blockers

- `npm test` exercises the actual session engine, all 300 campaign solvers, level order, countdown expiration, extension snapshot/restore, tutorial and native-ad guards.
- Browser smoke tests exercise the countdown, timeout dialog and 20-second coin continuation.
- A complete Android Gradle build and live AdMob SDK test cannot be verified in this editing environment (required packages and Android SDK not available locally). Confirm using the GitHub Actions run and your Android device.
- **Native monetisation requires your own AdMob app and unit IDs, Google UMP setup, and real app installs.** Google Play Billing is intentionally disabled until secure purchase verification is implemented.
- Because level IDs are re-ordered, existing saved progress remains unlocked but a replayed level may show a different layout than before. Back up important game progress before upgrading.
