# DrawPad — Shared Brand Assets

Central home for DrawPad brand assets (app icon, logos, future imagery) so every
page — Wix, landing pages, docs — hotlinks **one stable URL** instead of relying on
per-site uploads.

Served free via the [jsDelivr](https://www.jsdelivr.com/) CDN straight from GitHub
(global edge cache, CORS-friendly).

## App icon

The current icon: a glossy rainbow petal-mandala flower on a soft white background (full-bleed, no border).

| Asset | Size | CDN URL |
|-------|------|---------|
| App icon (web/logo) | 512×512 | `https://cdn.jsdelivr.net/gh/TeamDzX/drawpad-assets@main/icon/app-icon.png` |
| App icon (full)     | 1024×1024 | `https://cdn.jsdelivr.net/gh/TeamDzX/drawpad-assets@main/icon/app-icon-1024.png` |

```html
<img src="https://cdn.jsdelivr.net/gh/TeamDzX/drawpad-assets@main/icon/app-icon.png"
     alt="DrawPad" width="40" height="40" style="border-radius:10px">
```

## Notes

- **Caching:** jsDelivr caches the `@main` tag for up to ~12h. To force an update
  after replacing a file, either bust the cache via
  `https://purge.jsdelivr.net/gh/TeamDzX/drawpad-assets@main/icon/app-icon.png`
  or reference a version tag (e.g. `@v1`) and bump it.
- **Filenames are the contract.** Keep paths stable so existing pages don't break;
  add new variants rather than renaming.
