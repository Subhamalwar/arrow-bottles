const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const html = fs.readFileSync(require('node:path').join(__dirname, '..', 'www', 'index.html'),'utf8');
test('mobile-first layout supports narrow displays and safe touch controls',()=>{
  assert.match(html, /@media \(max-width: 480px\)/);
  assert.match(html, /@media \(max-width: 360px\)/);
  assert.match(html, /class: 'g-zoom g-zoom-out'/);
  assert.match(html, /aria-label': 'Zoom out'/);
  assert.match(html, /duration >= 430 && this\.zoomable\(\)/);
  assert.match(html, /this\.zoomOutBtn\.disabled = this\.cam\.zoom <= 1\.001/);
  assert.match(html, /this\.cam\.zoom >= ZOOM_MAX/);
  assert.match(html, /touch-action: none/);
});
