# Arrow Escape v3 — intertwined logic campaign

**Ready-to-upload GitHub source.** Android application ID remains `com.arrowbottles.game` so existing install identity is unchanged. This v3 package upgrades the gameplay from the previous v2 source while preserving the Capacitor Android and native AdMob integration.

## Gameplay improvements implemented

- **300 deterministic campaign levels** regenerated as denser, intertwined braid puzzles. They use winding shafts, directional blocking chains, varied S/U-shaped paths and occasional key locks. Every campaign board passes the actual in-game solver. Some arrows start unblocked; all levels can be solved without buying a power-up.
- **Exact +4 arrows per level through level 20:** level 1 = 12; level 2 = 16; level 5 = 28; level 10 = 48; level 20 = 88. Later levels grow from 88 to 132 arrows more gradually as logic complexity increases, to avoid unreadably crowded layouts on phones.
- **Thin stick arrows:** reduced from 36% to about 14.5% of the tile width for campaign and daily (tutorial retains thicker arrows). Heads and glyphs are smaller. Touch-selection tolerance follows tile scale to avoid grabbing a neighbor. Zoom-in `+`, existing pinch zoom and `Fit` are available on wider boards.
- **Puzzle IQ:** visible in the game header, level picker and victory panel. It is an **in-game challenge rating**, NOT a medical/psychometric IQ score and not a measure of players' intelligence. Scores use the level progression and path-turn complexity. They are nondecreasing.
- **Longer, more complex levels:** timing budgets scale with arrow count; removing each arrow remains the core challenge. No artificial delays or forced advertisement watching. Intended median completion-time progression must still be calibrated by actual player tests, not assumed from arrow count.
- Retains v2's countdown, two optional 20-second extensions, rewarded opportunities, banner/interstitial support, no mandatory login, heart system and missions. Real native rewarded payout still depends on the AdMob SDK confirmation. Google Play Billing **is not integrated**.
- Old v2 *in-progress* campaign resume snapshots aren't restored onto a different board. Completed level numbers, stars, coins and other stored data remain in local storage, although these levels now have **new layouts**.

## Install in GitHub Codespaces on an Android tablet

The ZIP contains an `arrow-escape/` folder with the repo source. Open your Codespace on the `main` branch and upload `arrow-escape-v3-ready-for-github.zip` into the **root of the repository** using Explorer → Upload. Then open Terminal → New Terminal and run:

```bash
unzip -o arrow-escape-v3-ready-for-github.zip
cp -a arrow-escape/. ./
rm -rf arrow-escape
rm -f arrow-escape-v3-ready-for-github.zip
# Remove the obsolete nested workflow folder ONLY if it exists:
if [ -d .github/workflows/.github ]; then git rm -r .github/workflows/.github; fi
npm install --no-audit --no-fund
npm test
npm run build:web
git add -A
git commit -m "Arrow Escape v3 - intertwined puzzles and Puzzle IQ"
git push origin main
```

If any command reports a failure, stop and check it before committing. Do not run `git push` if tests fail. `npm install` updates the `package-lock.json` present in your repository; this package intentionally does not include the stale v2 lockfile. The updated Actions workflow uses `npm install`, avoiding the prior `npm ci`/esbuild optional-dependency lock mismatch.

Open [GitHub Actions](https://github.com/Subhamalwar/arrow-bottles/actions). After **Build Arrow Escape Android** succeeds, download the `arrow-escape-android-*` artifact and extract `android/app/build/outputs/apk/debug/app-debug.apk` to install on your Android tablet. A release AAB is also built; Google Play requires your own signing secrets.

**Installation note:** GitHub builds can use different debug signing keys between runs. If Android shows *App not installed as package conflicts with an existing package*, the old APK is signed differently. Uninstalling the old app may delete locally stored gameplay progress. Back up important game data before removing it.

## Tests and validation

`npm test` runs the existing 14 tests plus 6 v3-specific tests covering exact +4 progression, all 300 board continuity, non-overlap, intertwining, Puzzle IQ, touch/zoom, and snapshot compatibility. All 300 boards are also run through the game's own solvability algorithm. A browser smoke test opened Levels 1 and 20, rendered the game, used the zoom button and reported no JS runtime errors.

**Not yet verified here:** native Gradle APK/AAB build, AdMob ad delivery on device, real user completion times, tablet accessibility/touch comfort, or Google Play release signing. Test on the tablet before treating v3 as release-ready.

## Build configuration and monetisation

- Application ID: `com.arrowbottles.game`; Android target SDK 36, min SDK 24.
- Default AdMob app ID `ca-app-pub-6081700970691881~6352526941` and banner unit `ca-app-pub-6081700970691881/7399061483` are configured; test ads are used by default. Live ads require repo variable `ADMOB_PRODUCTION=true` and production setup/consent.
- For real rewarded or interstitial ads supply `ADMOB_REWARDED_UNIT_ID` / `ADMOB_INTERSTITIAL_UNIT_ID` secrets; otherwise production versions of these formats stay disabled.
- Signed release AAB requires `ANDROID_KEYSTORE_BASE64`, `ANDROID_KEYSTORE_PASSWORD`, `ANDROID_KEY_ALIAS`, `ANDROID_KEY_PASSWORD` secrets. An unsigned AAB is not Play Store upload ready.
- To regenerate layouts: `python3 scripts/build_v3_levels.py scripts/v3-campaign.json` and re-embed the generated JSON in `www/index.html` and `arrow-bottles-final-index.html`. The generator includes an independent solver assertion for all levels. `scripts/assemble_v3.py` was used once to apply UI patches to the original v2 source; don't rerun it over an already-updated v3 file as it expects v2 markers.
