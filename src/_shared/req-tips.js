/* RFP requirement tooltips. Any element with data-req="CL-3.15 CL-3.16", and any .rid or .badge whose text names
   requirement IDs, shows the requirement, our compliance status and our answer on hover and keyboard focus.
   window.RFP_REQS is injected by src/build.py with only the rows the page uses (answers as of the capture date). */
(function () {
  'use strict';
  var REQS = window.RFP_REQS || {};
  var ID = /\b(CL|OM|MS|RC|LAF|LIT|LVP)-(\d+)(?:\.(\d+))?/;
  function parse(text) {
    var out = [], prefix = null, major = null, dotted = false, last = null, pendingRange = false;
    var tokens = String(text).match(/(CL|OM|MS|RC|LAF|LIT|LVP)-\d+(?:\.\d+)?|\d+(?:\.\d+)?|\bto\b/g) || [];
    tokens.forEach(function (t) {
      if (t === 'to') { pendingRange = !!last; return; }
      var m = t.match(ID), id;
      if (m) { prefix = m[1]; dotted = !!m[3]; major = m[2]; id = t; }
      else if (prefix) {
        if (dotted) id = prefix + '-' + (t.indexOf('.') > -1 ? t : major + '.' + t);
        else if (t.indexOf('.') < 0) id = prefix + '-' + t;
        else return;
      } else return;
      if (pendingRange && last) {
        var a = last.match(ID), b = id.match(ID);
        if (a && b && a[1] === b[1]) {
          if (a[3] && b[3] && a[2] === b[2]) for (var i = +a[3] + 1; i < +b[3] && out.length < 60; i++) add(a[1] + '-' + a[2] + '.' + i);
          else if (!a[3] && !b[3]) for (var j = +a[2] + 1; j < +b[2] && out.length < 60; j++) add(a[1] + '-' + j);
        }
        pendingRange = false;
      }
      add(id); last = id;
    });
    function add(x) { if (out.indexOf(x) < 0) out.push(x); }
    return out;
  }
  window.parseReqIds = parse;
  var tip = document.createElement('div');
  tip.id = 'req-tip'; tip.setAttribute('role', 'tooltip'); tip.hidden = true;
  document.body.appendChild(tip);
  var css = document.createElement('style');
  css.textContent = '#req-tip{position:fixed;z-index:90;max-width:24rem;background:#0a634d;color:#ffffff;border-radius:calc(var(--radius,.5rem) - 2px);padding:.625rem .75rem;font:500 .75rem/1.05rem var(--font-sans,"Plus Jakarta Sans",sans-serif);box-shadow:0 8px 24px rgba(0,0,0,.18);pointer-events:none;text-align:left}' +
    '#req-tip .rq{padding:.375rem 0;border-top:1px solid rgba(255,255,255,.2)}#req-tip .rq:first-child{border-top:0;padding-top:0}#req-tip .rq:last-child{padding-bottom:0}' +
    '#req-tip b{font-weight:700}#req-tip .st{display:inline-block;margin-left:.375rem;padding:0 .375rem;border-radius:9999px;background:rgba(255,255,255,.18);font-size:.6875rem}' +
    '#req-tip .tx{margin-top:.125rem}#req-tip .an{margin-top:.25rem;opacity:.85}#req-tip .more{margin-top:.375rem;opacity:.85}' +
    '[data-req],.rid,.badge{cursor:help}[data-req]:focus-visible,.rid:focus-visible,.badge:focus-visible{outline:2px solid var(--ring,#10a37f);outline-offset:2px}';
  document.head.appendChild(css);
  function cut(s, n) { s = String(s || ''); return s.length > n ? s.slice(0, n - 1).replace(/\s+\S*$/, '') + '…' : s; }
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function status(c) { return !c ? 'No answer yet' : /^Fully/.test(c) ? 'Fully Compliant' : /^Partial/.test(c) ? 'Partially Compliant' : /^Not/.test(c) ? 'Not Compliant' : String(c).replace(/\s*·\s*on the roadmap/gi, ''); }
  var PLANNED = /roadmap|delivery plan|planned/i;
  function answer(a) { return String(a || '').split(/(?<=[.!?])\s+/).filter(function (x) { return x && !PLANNED.test(x); }).join(' '); }
  function idsFor(el) {
    var src = el.getAttribute('data-req');
    if (src === null) { if (!el.classList.contains('rid') && !el.classList.contains('badge')) return []; src = el.textContent; }
    return parse(src).filter(function (x) { return REQS[x]; });
  }
  function target(e) {
    var el = e.target && e.target.closest && e.target.closest('[data-req], .rid, .badge');
    return el && idsFor(el).length ? el : null;
  }
  function show(el, x, y) {
    var ids = idsFor(el), max = 4;
    tip.innerHTML = ids.slice(0, max).map(function (id) {
      var r = REQS[id];
      return '<div class="rq"><b>' + id + '</b><span class="st">' + esc(status(r.c)) + (r.pr ? ' · ' + esc(r.pr) : '') + '</span><div class="tx">' + esc(cut(r.r, 220)) + '</div>' + (answer(r.a) ? '<div class="an">Our answer: ' + esc(cut(answer(r.a), 200)) + '</div>' : '') + '</div>';
    }).join('') + (ids.length > max ? '<div class="more">+' + (ids.length - max) + ' more: ' + ids.slice(max).join(', ') + '</div>' : '');
    tip.hidden = false;
    var w = tip.offsetWidth, h = tip.offsetHeight;
    tip.style.left = Math.max(8, Math.min(window.innerWidth - w - 8, x + 12)) + 'px';
    tip.style.top = (y - h - 12 < 8 ? y + 20 : y - h - 12) + 'px';
  }
  document.addEventListener('pointerover', function (e) { var el = target(e); if (el) show(el, e.clientX, e.clientY); });
  document.addEventListener('pointerout', function (e) { var el = target(e); if (el && !el.contains(e.relatedTarget)) tip.hidden = true; });
  document.addEventListener('focusin', function (e) { var el = target(e); if (el) { var r = el.getBoundingClientRect(); show(el, r.left, r.top); } });
  document.addEventListener('focusout', function (e) { if (target(e)) tip.hidden = true; });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') tip.hidden = true; });
  function arm() {
    var els = document.querySelectorAll('[data-req], .rid, .badge');
    for (var i = 0; i < els.length; i++) {
      var el = els[i];
      if (el.hasAttribute('data-req-armed')) continue;
      el.setAttribute('data-req-armed', '');
      if (!idsFor(el).length) continue;
      if (!el.matches('a, button, input, select, textarea, [tabindex]')) el.setAttribute('tabindex', '0');
      if (!el.getAttribute('aria-describedby')) el.setAttribute('aria-describedby', 'req-tip');
    }
  }
  new MutationObserver(arm).observe(document.body, { childList: true, subtree: true });
  arm();
})();
