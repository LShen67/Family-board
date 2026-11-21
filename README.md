# Family board

A simple always-on kitchen display for an old iPad mini 2. It shows:

- an analogue clock, the digital time, the time in words and the date
- the current weather and today's forecast for Westminster, London, with a short tip (umbrella, coat and so on)
- a darker theme from 7pm to 7am

The page is plain HTML, CSS and older-style JavaScript, so it runs in Safari on iOS 12.5.7, the last version the iPad mini 2 supports.

## Files

| File | What it is |
| --- | --- |
| `index.html` | The board itself (this is the home page of the site) |
| `index.md` | A short "About" page, published at `/about/` |
| `README.md` | This file |

## Settings

Open `index.html` and edit the `CONFIG` section near the top of the script:

```js
var CONFIG = {
  place: 'Westminster',   // name shown with the weather
  latitude: 51.4975,      // location for the forecast
  longitude: -0.1357,
  nightFrom: 19,          // dark theme starts (24-hour clock)
  nightUntil: 7           // dark theme ends
};
```

## Publishing with GitHub Pages

1. Upload all three files to the root of this repository.
2. Go to **Settings → Pages**, choose **Deploy from a branch**, select `main` and `/ (root)`, then **Save**.
3. Open the site address shown on that page. Changes can take a few minutes to appear.

## Setting up the iPad

1. Open the site address in Safari and choose **Share → Add to Home Screen**.
2. **Settings → Display & Brightness → Auto-Lock → Never**, and keep the iPad plugged in.
3. **Settings → General → Accessibility → Guided Access**: turn it on, set a passcode, and set its Display Auto-Lock to Never.
4. Open the board from the Home Screen, triple-click the Home button and tap **Start**.

To leave the board, triple-click the Home button and enter the Guided Access passcode.

## How it keeps itself fresh

- The weather updates every 15 minutes, and retries every 5 minutes if the connection drops.
- The page reloads itself at 3am each day.

## Privacy

On GitHub's free plan this repository is public, so anyone can read these files. Don't add names, addresses or private calendar links.

## Credits

Weather data by [Open-Meteo.com](https://open-meteo.com/), licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Font: [Fredoka](https://fonts.google.com/specimen/Fredoka) from Google Fonts.
