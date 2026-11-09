/* Gladstone Road or Disraeli Street? Every British street named after a politician or Victorian hero, coloured by party,
 * with towns ringed by their Liberal vote 1868 to 1900. Plain OpenFreeMap Positron base map.
 * Dr Tristan Hotham, Independent researcher, 2026. MIT licence. */
(function () {
  'use strict';
  const qs = new URLSearchParams(location.search);
  const STYLE = 'https://tiles.openfreemap.org/styles/positron';
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const norm = s => String(s).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  const small = matchMedia('(max-width:800px)').matches;
  const START = small ? [[-6.6, 50.0], [1.8, 58.6]] : [[-7.6, 49.9], [2.0, 58.8]];
  const PARTY = { LIB: 'Liberal', CON: 'Conservative', LU: 'Liberal Unionist', LAB: 'Labour', PEEL: 'Conservative (Peelite)', WHIG: 'Whig', TORY: 'Tory', IRN: 'Irish Nationalist', '': 'not a party figure' };
  const CLASS = { main: 'party name used in the main test', main20: 'Edwardian Liberal', labour: 'Labour name', test: 'tested name: also a place, estate or surname', amb: 'set aside: mostly a place, a royal or a common surname', royal: 'royal', hero: 'military or imperial hero', reform: 'reformer or radical hero' };
  // group: 0 main, 1 labour and Edwardian Liberals, 2 tested, 3 other
  let map = null, D = null, T = null, popup = null;
  const grp = c => c === 'main' ? 0 : (c === 'labour' || c === 'main20') ? 1 : c === 'test' ? 2 : 3;
  const col = n => {
    if (n.c === 'main' || n.c === 'main20') return n.p === 'LIB' ? '#E08A1E' : '#2D5C9E';
    if (n.c === 'labour') return '#C2332B';
    if (n.c === 'test') return n.p === 'LIB' ? '#F0C27A' : n.p === 'LAB' ? '#E58A84' : '#9DB3D3';
    if (n.c === 'royal') return '#9C86AE';
    return '#A8A29E';
  };

  document.getElementById('theme').addEventListener('click', () => {
    const r = document.documentElement, dark = r.dataset.theme ? r.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
    r.dataset.theme = dark ? 'light' : 'dark';
  });
  const ct = document.getElementById('cartouche');
  const fold = f => ct.classList.toggle('folded', f);
  if (small) fold(true);
  document.getElementById('ctToggle').addEventListener('click', () => fold(!ct.classList.contains('folded')));
  document.getElementById('ctFold').addEventListener('click', () => fold(true));

  function streetPopup(r, ll) {
    const n = D.names[r[2]];
    const name = r[3] || n.l;
    let h = `<b class="t">${esc(name)}</b><div class="nt">${esc(r[4] || 'not in a town')}</div><table>`;
    h += `<tr><td>Named after</td><td><b>${esc(n.l)}</b>: ${esc(n.note)}</td></tr>`;
    h += `<tr><td>Party</td><td>${esc(PARTY[n.p])}${n.y ? ', prominent ' + esc(n.y) : ''}</td></tr>`;
    h += `<tr><td>In this study</td><td>${esc(r[6] ? 'set aside: within 25 km of Beaconsfield, Bucks, so possibly a route name' : CLASS[n.c])}</td></tr></table>`;
    h += `<p class="nt">Street name from OpenStreetMap. The name alone cannot prove whom a street was named after.</p>`;
    h += `<div class="lk"><a href="https://www.openstreetmap.org/way/${r[5]}" target="_blank" rel="noopener">OpenStreetMap way ${r[5]}</a></div>`;
    show(h, ll);
  }
  function townPopup(t, ll) {
    let h = `<b class="t">${esc(t.n)}</b><table>`;
    h += `<tr><td>Liberal vote</td><td>${t.v === null ? 'no contested election' : '<b>' + t.v.toFixed(1) + '%</b> of the Liberal and Conservative vote, general elections 1868 to 1900 (' + t.e + ' with a contest)'}</td></tr>`;
    h += `<tr><td>Party streets</td><td><b>${t.l}</b> Liberal, <b>${t.c}</b> Conservative${t.l + t.c ? ' (' + Math.round(100 * t.l / (t.l + t.c)) + '% Liberal)' : ''}</td></tr>`;
    if (t.lab !== null) h += `<tr><td>Labour vote</td><td>${t.lab.toFixed(1)}% of all votes, 1945 to 1970</td></tr>`;
    h += `<tr><td>Seat</td><td>${t.b ? 'a parliamentary borough in 1868' : 'seats named after the town from 1885'}</td></tr></table>`;
    h += `<p class="nt">Votes: UK Parliament results for the seats named after the town. Streets: OpenStreetMap, assigned to the town by distance.</p>`;
    show(h, ll);
  }
  function show(h, ll) { if (popup) popup.remove(); popup = new maplibregl.Popup({ maxWidth: '330px', offset: 8 }).setLngLat(ll).setHTML(h).addTo(map); }

  function apply() {
    const g = [document.getElementById('ckMain').checked, document.getElementById('ckLab').checked, document.getElementById('ckTest').checked, document.getElementById('ckOther').checked];
    const one = document.getElementById('nameSel').value;
    const f = one !== '' ? ['==', ['get', 'k'], +one] : ['any', ...g.map((v, i) => v ? ['==', ['get', 'g'], i] : false).filter(Boolean), false];
    ['st', 'stl'].forEach(id => map.setFilter(id, f));
    const vis = (id, v) => map.setLayoutProperty(id, 'visibility', v ? 'visible' : 'none');
    vis('stl', document.getElementById('ckNames').checked);
    vis('tw', document.getElementById('ckTown').checked);
  }

  function setupLayers() {
    const before = (map.getStyle().layers.find(l => l.type === 'symbol') || {}).id;
    const tf = T.map((t, i) => ({ type: 'Feature', properties: { i, v: t.v === null ? -1 : t.v, s: t.l + t.c }, geometry: { type: 'Point', coordinates: [t.lon, t.lat] } }));
    map.addSource('tw', { type: 'geojson', data: { type: 'FeatureCollection', features: tf }, attribution: 'Votes: UK Parliament (Open Parliament Licence)' });
    map.addLayer({ id: 'tw', type: 'circle', source: 'tw', paint: {
      'circle-radius': ['interpolate', ['linear'], ['zoom'], 4, ['+', 5, ['*', 1.2, ['sqrt', ['get', 's']]]], 9, ['+', 14, ['*', 3, ['sqrt', ['get', 's']]]], 13, ['+', 40, ['*', 6, ['sqrt', ['get', 's']]]]],
      'circle-color': ['case', ['<', ['get', 'v'], 0], '#DDDAD2', ['interpolate', ['linear'], ['get', 'v'], 30, '#2D5C9E', 42, '#9DB3D3', 50, '#F4F1EA', 58, '#F0C27A', 70, '#E08A1E']],
      'circle-opacity': ['interpolate', ['linear'], ['zoom'], 5, 0.55, 10, 0.25], 'circle-stroke-color': '#2B2119', 'circle-stroke-width': 0.8, 'circle-stroke-opacity': 0.6 } }, before);
    const feats = D.s.map((r, i) => { const n = D.names[r[2]]; return { type: 'Feature', properties: { i, k: r[2], g: r[6] ? 3 : grp(n.c), c: col(n), n: r[3] || n.l, z: n.c === 'main' ? 3 : n.c === 'labour' ? 2 : 1 }, geometry: { type: 'Point', coordinates: [r[0], r[1]] } }; });
    map.addSource('st', { type: 'geojson', data: { type: 'FeatureCollection', features: feats }, attribution: 'Streets: <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors (ODbL)' });
    map.addLayer({ id: 'st', type: 'circle', source: 'st', layout: { 'circle-sort-key': ['get', 'z'] }, paint: {
      'circle-radius': ['interpolate', ['linear'], ['zoom'], 4, 3, 8, 4.5, 13, 8], 'circle-color': ['get', 'c'],
      'circle-stroke-color': '#FFFFFF', 'circle-stroke-width': ['interpolate', ['linear'], ['zoom'], 4, 0.7, 10, 1.5] } });
    map.addLayer({ id: 'stl', type: 'symbol', source: 'st', minzoom: 12,
      layout: { 'text-field': ['get', 'n'], 'text-font': ['Noto Sans Italic'], 'text-size': 12, 'text-offset': [0, 0.9], 'text-anchor': 'top', 'text-optional': true },
      paint: { 'text-color': '#2B2119', 'text-halo-color': 'rgba(255,255,255,0.95)', 'text-halo-width': 1.6 } });
    map.on('click', e => {
      const box = [[e.point.x - 6, e.point.y - 6], [e.point.x + 6, e.point.y + 6]];
      const f = map.queryRenderedFeatures(box, { layers: ['st'] })[0];
      if (f) return streetPopup(D.s[f.properties.i], f.geometry.coordinates);
      const t = map.queryRenderedFeatures(e.point, { layers: ['tw'] })[0];
      if (t) townPopup(T[t.properties.i], t.geometry.coordinates);
    });
    ['st', 'tw'].forEach(l => { map.on('mouseenter', l, () => map.getCanvas().style.cursor = 'pointer'); map.on('mouseleave', l, () => map.getCanvas().style.cursor = ''); });
    const sel = document.getElementById('nameSel');
    D.names.map((n, i) => [n, i]).filter(([n, i]) => D.s.some(r => r[2] === i)).sort((a, b) => a[0].l.localeCompare(b[0].l)).forEach(([n, i]) => {
      const o = document.createElement('option'); o.value = i; o.textContent = n.l + ' (' + PARTY[n.p] + ')'; sel.appendChild(o); });
    if (qs.get('name')) { const i = D.names.findIndex(n => n.k === qs.get('name')); if (i >= 0) sel.value = i; }
    const lp = document.getElementById('lp'), btn = document.getElementById('lyrBtn');
    btn.addEventListener('click', e => { e.stopPropagation(); const o = lp.classList.toggle('open'); btn.setAttribute('aria-expanded', o); });
    document.addEventListener('click', e => { if (!lp.contains(e.target) && e.target !== btn) { lp.classList.remove('open'); btn.setAttribute('aria-expanded', false); } });
    ['ckMain', 'ckLab', 'ckTest', 'ckOther', 'ckNames', 'ckTown', 'nameSel'].forEach(id => document.getElementById(id).addEventListener('change', apply));
    document.querySelectorAll('.chip[data-n]').forEach(b => b.addEventListener('click', () => {
      const on = b.getAttribute('aria-pressed') !== 'true';
      document.querySelectorAll('.chip[data-n]').forEach(c => c.setAttribute('aria-pressed', 'false'));
      sel.value = on ? String(D.names.findIndex(n => n.k === b.dataset.n)) : ''; b.setAttribute('aria-pressed', String(on)); apply(); }));
    document.querySelectorAll('a[data-t]').forEach(a => a.addEventListener('click', e => { e.preventDefault(); flyTown(a.dataset.t); document.getElementById('mapWrap').scrollIntoView({ behavior: 'smooth' }); }));
    apply();
  }
  function flyTown(n) {
    const t = T.find(t => t.n === n); if (!t) return; fold(true);
    map.flyTo({ center: [t.lon, t.lat], zoom: n === 'London' ? 9.6 : 11.5, duration: 1300 });
  }

  function setupSearch() {
    const q = document.getElementById('q'), sug = document.getElementById('sug');
    let items = [], k = -1;
    const sts = D.s.map(r => ({ t: 's', name: r[3] || D.names[r[2]].l, sub: (r[4] || '') + ' · ' + D.names[r[2]].l, lon: r[0], lat: r[1], r }));
    const towns = T.map(t => ({ t: 'p', name: t.n, sub: t.v === null ? 'town' : 'town · ' + t.v.toFixed(0) + '% Liberal 1868 to 1900', lon: t.lon, lat: t.lat, tt: t }));
    const showS = () => {
      const v = norm(q.value.trim()); sug.innerHTML = ''; k = -1;
      if (v.length < 2) { sug.style.display = 'none'; return; }
      const m = arr => arr.filter(p => norm(p.name).startsWith(v)).concat(arr.filter(p => !norm(p.name).startsWith(v) && v.length > 2 && norm(p.name).includes(v)));
      items = m(towns).slice(0, 5).concat(m(sts).slice(0, 8));
      items.forEach((p, i) => { const li = document.createElement('li'); li.setAttribute('role', 'option'); li.innerHTML = `${esc(p.name)} <span>${esc(p.sub)}</span>`;
        li.addEventListener('mousedown', e => { e.preventDefault(); pick(i); }); sug.appendChild(li); });
      sug.style.display = items.length ? 'block' : 'none';
    };
    const pick = i => {
      const p = items[i]; if (!p) return; q.value = p.name; sug.style.display = 'none'; fold(true);
      map.flyTo({ center: [p.lon, p.lat], zoom: p.t === 's' ? 15 : 11.5, duration: 1300 });
      map.once('moveend', () => p.t === 's' ? streetPopup(p.r, [p.lon, p.lat]) : townPopup(p.tt, [p.lon, p.lat]));
    };
    q.addEventListener('input', showS);
    q.addEventListener('keydown', e => {
      const lis = [...sug.children];
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); k = Math.max(0, Math.min(lis.length - 1, k + (e.key === 'ArrowDown' ? 1 : -1))); lis.forEach((l, i) => l.setAttribute('aria-selected', i === k)); }
      else if (e.key === 'Enter') { e.preventDefault(); if (!items.length) showS(); pick(k < 0 ? 0 : k); }
      else if (e.key === 'Escape') sug.style.display = 'none';
    });
    q.addEventListener('blur', () => setTimeout(() => sug.style.display = 'none', 150));
  }

  Promise.all([fetch('data/streets.json').then(r => r.json()), fetch('data/towns.json').then(r => r.json())]).then(([d, t]) => {
    D = d; T = t;
    const at = (qs.get('at') || '').split(',').map(Number);
    const mo = at.length === 3 && at.every(isFinite) ? { center: [at[1], at[0]], zoom: at[2] } : { bounds: START, fitBoundsOptions: { padding: 6 } };
    const m0 = new maplibregl.Map(Object.assign({ container: 'map', style: STYLE, attributionControl: { compact: true }, maxZoom: 18 }, mo));
    return new Promise((res, rej) => { m0.once('load', () => res(m0)); m0.once('error', e => { if (!m0.loaded()) rej(e.error || e); }); });
  }).then(m => {
    map = m; window.__map = m;
    m.on('error', e => { const er = e && e.error; if (er && (er.name === 'AbortError' || /abort/i.test(er.message || ''))) return; console.error(er || e); });
    const n = document.getElementById('nojs'); if (n) n.remove();
    m.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'bottom-right');
    const foldAt = () => document.querySelectorAll('.maplibregl-ctrl-attrib.maplibregl-compact').forEach(a => { a.classList.remove('maplibregl-compact-show'); a.removeAttribute('open'); });
    m.once('idle', foldAt); setTimeout(foldAt, 1500);
    setupLayers(); setupSearch();
    document.getElementById('mapWrap').addEventListener('pointerdown', e => { if (e.target.closest && e.target.closest('.cartouche,.ov,.lp,.keys,.mfs-btn,.maplibregl-ctrl,.maplibregl-popup')) return; fold(true); }, { capture: true, passive: true, once: true });
    if (qs.get('town')) flyTown(qs.get('town'));
  }).catch(e => { console.error(e); const n = document.getElementById('nojs'); if (n) n.textContent = 'The map could not load: ' + e.message; });
})();
