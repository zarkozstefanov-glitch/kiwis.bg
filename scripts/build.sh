#!/usr/bin/env bash
# Builds the deployable site into dist/.
# Only files listed here are published — everything else (sources, scripts, docs, .git, .github) stays out.
set -euo pipefail

cd "$(dirname "$0")/.."

OUT=dist
VERSION="${GITHUB_SHA:-${VERCEL_GIT_COMMIT_SHA:-$(git rev-parse HEAD 2>/dev/null || date +%s)}}"
VERSION="${VERSION:0:8}"
LASTMOD="$(date -u +%Y-%m-%d)"

rm -rf "$OUT"
mkdir -p "$OUT"

cp index.html menu.html 404.html "$OUT/"
cp .htaccess robots.txt sitemap.xml llms.txt site.webmanifest "$OUT/"
cp favicon.ico favicon-32.png apple-touch-icon.png "$OUT/"
cp -R css js images "$OUT/"
find "$OUT" -name ".DS_Store" -delete

# Cache-busting: CSS/JS are cached for a year, so every deploy gets a new ?v=
for f in "$OUT"/*.html; do
  sed -i.bak -E "s#(href|src)=\"(/?)(css|js)/([a-z0-9_-]+)\.(css|js)\"#\1=\"\2\3/\4.\5?v=${VERSION}\"#g" "$f"
  rm "$f.bak"
done
sed -i.bak "s#__LASTMOD__#${LASTMOD}#g" "$OUT/sitemap.xml" && rm "$OUT/sitemap.xml.bak"

# --- Checks -----------------------------------------------------------------
fail=0

# Every local asset referenced from HTML/CSS/manifest must exist in dist/
refs=$(grep -hoE ' (src|href)="[^"]+"' "$OUT"/*.html | sed -E 's/^ [a-z]+="//; s/"$//')
refs+=$'\n'$(grep -hoE '(srcset|imagesrcset)="[^"]+"' "$OUT"/*.html \
         | sed -E 's/^[a-z]+="//; s/"$//' | tr ',' '\n' | awk '{print $1}')
refs+=$'\n'$( (grep -hoE 'url\([^)]+\)' "$OUT"/css/*.css || true) | sed -E "s/url\(['\"]?//; s/['\"]?\)$//")
refs+=$'\n'$(grep -hoE '"src": *"[^"]+"' "$OUT/site.webmanifest" | sed -E 's/.*"(\/[^"]+)"$/\1/')
while read -r ref; do
  [[ -z "$ref" || "$ref" =~ ^(https?:|tel:|mailto:|#|data:) ]] && continue
  path="${ref%%[?#]*}"
  path="${path#/}"
  [[ -z "$path" ]] && continue
  if [[ ! -e "$OUT/$path" ]]; then
    echo "Missing asset: $ref"; fail=1
  fi
done <<< "$refs"

# No development leftovers or insecure URLs
if grep -rnE 'localhost|127\.0\.0\.1|/Users/|C:\\|http://' "$OUT" --include='*.html' --include='*.css' --include='*.js' --include='*.txt' --include='*.xml' --include='*.webmanifest' \
     | grep -v 'http://www.sitemaps.org\|http://www.google.com/schemas'; then
  echo "Found development paths or http:// URLs (see above)"; fail=1
fi
if grep -rn 'console\.log' "$OUT"/js; then
  echo "console.log left in production JS"; fail=1
fi
if find "$OUT" -name '.env*' -o -name '*.md' -o -name '*.map' | grep -q .; then
  echo "Internal files found in dist/"; fail=1
fi

[[ $fail -eq 0 ]] || { echo "Build checks FAILED"; exit 1; }

echo "Build OK (version ${VERSION}): $(find "$OUT" -type f | wc -l | tr -d ' ') files, $(du -sh "$OUT" | cut -f1)"
