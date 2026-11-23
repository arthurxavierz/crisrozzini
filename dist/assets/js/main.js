/* Cris Rozzini · Achilles Media */
(function () {
  "use strict";
  var doc = document.documentElement;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var hasIO = "IntersectionObserver" in window;
  var mobile = function () { return window.innerWidth < 860; };
  var play = function (v) { var p = v.play(); if (p && p.catch) p.catch(function () {}); };

  /* ---------- Cabeçalho, progresso e paralaxe ---------- */
  var header = $(".site-header"), bar = $(".progress-bar"), wa = $(".wa-float"), last = 0;
  var heroMove = $(".hero-reels, .ph-media.cols");
  function onScroll() {
    var y = window.scrollY, h = doc.scrollHeight - window.innerHeight;
    header.classList.toggle("is-solid", y > 40);
    var hide = y > 600 && y > last + 4 && !document.body.classList.contains("menu-open");
    if (hide) header.classList.add("is-hidden"); else if (y < last - 4 || y < 600) header.classList.remove("is-hidden");
    last = y;
    if (bar) bar.style.setProperty("--p", h > 0 ? (y / h).toFixed(4) : 0);
    if (wa) wa.classList.toggle("show", y > window.innerHeight * .6 || document.body.getAttribute("data-page") !== "index");
    if (!reduce && heroMove && y < window.innerHeight * 1.3) heroMove.style.setProperty("--hy", (y * 0.22).toFixed(1) + "px");
    fill();
    sweep();
  }
  var ticking = false;
  window.addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(function () { ticking = false; onScroll(); }); } }, { passive: true });

  /* ---------- Menu tela cheia ---------- */
  var toggle = $(".menu-toggle"), overlay = $(".overlay");
  function setMenu(open) {
    overlay.setAttribute("data-open", open ? "true" : "false");
    overlay.setAttribute("aria-hidden", open ? "false" : "true");
    if (open) overlay.removeAttribute("inert"); else overlay.setAttribute("inert", "");
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    document.body.classList.toggle("menu-open", open);
    $(".t", toggle).textContent = open ? "Fechar" : "Menu";
  }
  if (toggle && overlay) {
    toggle.addEventListener("click", function () { setMenu(overlay.getAttribute("data-open") !== "true"); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") setMenu(false); });
    $$("a", overlay).forEach(function (a) { a.addEventListener("click", function () { setMenu(false); }); });
  }

  /* ---------- Vídeos de fundo: versão certa para a tela ---------- */
  var save = navigator.connection && navigator.connection.saveData;
  $$("video[data-desktop]").forEach(function (v) {
    var m = mobile() && v.getAttribute("data-mobile");
    if (m && v.getAttribute("data-poster-m")) v.poster = v.getAttribute("data-poster-m");
    if (reduce || save) return;
    if (mobile() && !m && v.closest(".hero-reels")) return; /* colunas extras não aparecem no celular */
    v.src = m ? v.getAttribute("data-mobile") : v.getAttribute("data-desktop");
    play(v);
  });

  /* prévias que só carregam perto da tela e pausam quando saem dela */
  if (!reduce && !save) {
    var vio = hasIO ? new IntersectionObserver(function (es) {
      es.forEach(function (en) {
        var v = en.target, card = v.closest(".reel");
        if (en.isIntersecting) {
          if (!v.getAttribute("src")) v.src = v.getAttribute("data-src");
          play(v);
          v.addEventListener("playing", function () { if (card) card.classList.add("playing"); }, { once: true });
        } else if (v.getAttribute("src")) v.pause();
      });
    }, { rootMargin: "120px 200px" }) : null;
    $$("video[data-src]").forEach(function (v) { if (vio) vio.observe(v); });
  }

  /* ---------- Título do hero letra a letra ---------- */
  var title = $(".hero-title");
  if (title) {
    var i = 0;
    var walk = function (node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (n) {
        if (n.nodeType === 3 && n.textContent.trim()) {
          var frag = document.createDocumentFragment();
          Array.from(n.textContent.trim()).forEach(function (c) {
            var s = document.createElement("span");
            s.className = "ch"; s.style.setProperty("--i", i++); s.textContent = c;
            frag.appendChild(s);
          });
          n.parentNode.replaceChild(frag, n);
        } else if (n.nodeType === 1 && n.tagName !== "svg") walk(n);
      });
    };
    $$(".line", title).forEach(walk);
  }

  /* ---------- Títulos grandes sempre cabem na largura ---------- */
  var fitEls = $$(".hero-title, .page-hero h1.mega, .cta-big .display");
  function fitTitles() {
    fitEls.forEach(function (el) {
      el.style.fontSize = "";
      var avail = el.parentElement.clientWidth, widest = 0;
      var lines = $$(".line", el);
      if (!lines.length) { el.style.whiteSpace = "nowrap"; widest = el.scrollWidth; el.style.whiteSpace = ""; if (widest <= avail) return; }
      lines.forEach(function (l) {
        var inner = l.firstElementChild && l.firstElementChild.tagName !== "svg" ? l.firstElementChild : l;
        l.style.whiteSpace = "nowrap";
        var w = inner.scrollWidth || inner.getBoundingClientRect().width;
        if (l.classList.contains("l2")) w = l.scrollWidth;
        widest = Math.max(widest, w);
      });
      if (widest > avail && widest > 0) {
        var fs = parseFloat(getComputedStyle(el).fontSize);
        el.style.fontSize = Math.floor(fs * (avail / widest) * 0.985) + "px";
      }
    });
  }
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitTitles); else fitTitles();
  var rt; window.addEventListener("resize", function () { clearTimeout(rt); rt = setTimeout(fitTitles, 120); });

  /* ---------- Títulos que sobem palavra a palavra ---------- */
  $$("[data-split]").forEach(function (el) {
    var wi = 0;
    var walk = function (node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (n) {
        if (n.nodeType === 3) {
          var frag = document.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach(function (p) {
            if (!p) return;
            if (/^\s+$/.test(p)) { frag.appendChild(document.createTextNode(" ")); return; }
            var w = document.createElement("span"), s = document.createElement("span");
            w.className = "w"; s.textContent = p; s.style.setProperty("--wi", wi++);
            w.appendChild(s); frag.appendChild(w);
          });
          n.parentNode.replaceChild(frag, n);
        } else if (n.nodeType === 1) walk(n);
      });
    };
    walk(el);
  });

  /* ---------- Revelação no scroll (com varredura para páginas abertas já roladas) ---------- */
  var revs = $$("[data-reveal], [data-mask], [data-split], .step");
  function show(el) { el.classList.add("in"); }
  var rio = hasIO ? new IntersectionObserver(function (es) {
    es.forEach(function (en) { if (en.isIntersecting) { show(en.target); rio.unobserve(en.target); } });
  }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 }) : null;
  revs.forEach(function (el) { if (rio) rio.observe(el); else show(el); });
  function sweep() {
    var vh = window.innerHeight;
    revs.forEach(function (el) { if (!el.classList.contains("in") && el.getBoundingClientRect().top < vh * 0.95) show(el); });
  }
  setTimeout(sweep, 400);

  /* ---------- Manifesto que se preenche com a leitura ---------- */
  var fillEl = $("[data-fill]"), fillWords = [];
  if (fillEl) {
    var wrapWords = function (node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (n) {
        if (n.nodeType === 3) {
          var frag = document.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach(function (p) {
            if (!p) return;
            if (/^\s+$/.test(p)) { frag.appendChild(document.createTextNode(" ")); return; }
            var s = document.createElement("span"); s.textContent = p; s.style.transition = "opacity .3s"; fillWords.push(s); frag.appendChild(s);
          });
          n.parentNode.replaceChild(frag, n);
        } else if (n.nodeType === 1) wrapWords(n);
      });
    };
    wrapWords(fillEl);
  }
  function fill() {
    if (!fillEl || reduce) return;
    var r = fillEl.getBoundingClientRect(), vh = window.innerHeight;
    var p = Math.min(1, Math.max(0, (vh * 0.85 - r.top) / (r.height + vh * 0.35)));
    var n = Math.round(p * fillWords.length);
    fillWords.forEach(function (w, k) { w.style.opacity = k < n ? 1 : 0.18; });
  }

  /* ---------- Contadores ---------- */
  var cio = hasIO ? new IntersectionObserver(function (es) {
    es.forEach(function (en) {
      if (!en.isIntersecting) return;
      var el = en.target, to = +el.getAttribute("data-count"), t0 = null;
      cio.unobserve(el);
      if (reduce) { el.textContent = to; return; }
      var step = function (t) {
        if (!t0) t0 = t;
        var p = Math.min(1, (t - t0) / 1600), e = 1 - Math.pow(1 - p, 4);
        el.textContent = Math.round(e * to);
        if (p < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    });
  }, { threshold: 0.6 }) : null;
  $$("[data-count]").forEach(function (el) { if (cio) cio.observe(el); else el.textContent = el.getAttribute("data-count"); });

  /* ---------- Brilho de pó no hero (glitter que segue o cursor) ---------- */
  var cv = $(".hero-glitter");
  if (cv && !reduce) {
    var ctx = cv.getContext("2d"), dpr = Math.min(window.devicePixelRatio || 1, 2), W = 0, H = 0, parts = [], running = true;
    var COLORS = ["244,211,220", "228,154,176", "255,250,251", "231,196,148", "201,111,139"];
    var size = function () { W = cv.offsetWidth; H = cv.offsetHeight; cv.width = W * dpr; cv.height = H * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0); };
    size(); window.addEventListener("resize", size);
    var spawn = function (x, y, burst) {
      parts.push({ x: x, y: y, vx: (Math.random() - .5) * (burst ? 1.6 : .25), vy: burst ? (Math.random() - .7) * 1.4 : -(.15 + Math.random() * .45),
        r: burst ? .6 + Math.random() * 1.8 : .4 + Math.random() * 1.5, life: 0, max: burst ? 60 + Math.random() * 60 : 260 + Math.random() * 260,
        c: COLORS[(Math.random() * COLORS.length) | 0], tw: Math.random() * 6.28, star: Math.random() < .14 });
    };
    for (var k = 0; k < (mobile() ? 50 : 110); k++) { spawn(Math.random() * W, Math.random() * H, false); parts[k].life = Math.random() * parts[k].max; }
    var hero = $(".hero"), lastSpawn = 0;
    hero.addEventListener("pointermove", function (e) {
      var r = cv.getBoundingClientRect(), now = performance.now();
      if (now - lastSpawn < 16) return; lastSpawn = now;
      for (var j = 0; j < 4; j++) spawn(e.clientX - r.left + (Math.random() - .5) * 18, e.clientY - r.top + (Math.random() - .5) * 18, true);
    });
    var drawStar = function (x, y, s) {
      ctx.beginPath(); ctx.moveTo(x, y - s * 3); ctx.lineTo(x + s * .6, y - s * .6); ctx.lineTo(x + s * 3, y); ctx.lineTo(x + s * .6, y + s * .6);
      ctx.lineTo(x, y + s * 3); ctx.lineTo(x - s * .6, y + s * .6); ctx.lineTo(x - s * 3, y); ctx.lineTo(x - s * .6, y - s * .6); ctx.closePath(); ctx.fill();
    };
    var tick = function () {
      if (!running) return;
      ctx.clearRect(0, 0, W, H);
      ctx.globalCompositeOperation = "lighter";
      for (var n = parts.length - 1; n >= 0; n--) {
        var p = parts[n];
        p.life++; p.x += p.vx; p.y += p.vy; p.vx *= .995; p.tw += .08;
        var lf = p.life / p.max, a = Math.sin(Math.PI * lf) * (.45 + .55 * Math.abs(Math.sin(p.tw)));
        if (p.life >= p.max || p.y < -10) {
          if (p.max > 200 && parts.length < (mobile() ? 60 : 130)) { p.x = Math.random() * W; p.y = H + 5; p.life = 0; continue; }
          parts.splice(n, 1); continue;
        }
        ctx.fillStyle = "rgba(" + p.c + "," + a.toFixed(3) + ")";
        if (p.star) drawStar(p.x, p.y, p.r * .9);
        else { ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, 6.283); ctx.fill(); }
      }
      if (parts.length > 400) parts.splice(0, parts.length - 400);
      requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
    if (hasIO) new IntersectionObserver(function (es) { var vis = es[0].isIntersecting; if (vis && !running) { running = true; requestAnimationFrame(tick); } running = vis; }).observe(cv);
  }

  /* ---------- Vitrine de reels: setas e arrastar ---------- */
  $$("[data-rail]").forEach(function (rail) {
    var sec = rail.closest("section");
    var by = function (d) { var c = rail.querySelector(".reel"); rail.scrollBy({ left: d * (c ? c.offsetWidth + 16 : 300) * 2, behavior: "smooth" }); };
    var pv = $("[data-rail-prev]", sec), nx = $("[data-rail-next]", sec);
    if (pv) pv.addEventListener("click", function () { by(-1); });
    if (nx) nx.addEventListener("click", function () { by(1); });
    var down = false, sx = 0, sl = 0, moved = false;
    rail.addEventListener("pointerdown", function (e) { if (e.pointerType !== "mouse") return; down = true; moved = false; sx = e.clientX; sl = rail.scrollLeft; });
    window.addEventListener("pointermove", function (e) { if (!down) return; var dx = e.clientX - sx; if (Math.abs(dx) > 5) { moved = true; rail.classList.add("drag"); } rail.scrollLeft = sl - dx; });
    window.addEventListener("pointerup", function () { down = false; rail.classList.remove("drag"); });
    rail.addEventListener("click", function (e) { if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; } }, true);
  });

  /* ---------- Modal de vídeo ---------- */
  var vm = $("#vmodal"), vmv = vm && $("video", vm), lastFocus = null;
  function openVideo(el) {
    if (!vm) return;
    lastFocus = el;
    vmv.src = el.getAttribute("data-full");
    $(".vm-title", vm).textContent = el.getAttribute("data-title") || "";
    $(".vm-cap", vm).textContent = el.getAttribute("data-cap") || "";
    $(".vm-cat", vm).textContent = el.getAttribute("data-cat") || el.getAttribute("data-catname") || "";
    var ig = $(".vm-ig", vm); if (ig && el.getAttribute("data-ig")) ig.href = el.getAttribute("data-ig");
    vm.setAttribute("aria-hidden", "false"); vm.removeAttribute("inert");
    document.body.style.overflow = "hidden";
    play(vmv);
    $(".vmodal-close", vm).focus();
  }
  function closeVideo() {
    if (!vm || vm.getAttribute("aria-hidden") === "true") return;
    vmv.pause(); vmv.removeAttribute("src"); vmv.load();
    vm.setAttribute("aria-hidden", "true"); vm.setAttribute("inert", "");
    document.body.style.overflow = "";
    if (lastFocus) lastFocus.focus();
  }
  if (vm) {
    $(".vmodal-close", vm).addEventListener("click", closeVideo);
    vm.addEventListener("click", function (e) { if (e.target === vm) closeVideo(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeVideo(); });
  }
  document.addEventListener("click", function (e) {
    var el = e.target.closest("[data-full]");
    if (el) { e.preventDefault(); openVideo(el); }
  });

  /* ---------- Lightbox de fotos ---------- */
  var lb = $(".lightbox");
  document.addEventListener("click", function (e) {
    var el = e.target.closest("[data-img]");
    if (!el || !lb) return;
    $("img", lb).src = el.getAttribute("data-img");
    $("img", lb).alt = el.getAttribute("data-title") || "";
    $("p", lb).textContent = el.getAttribute("data-title") || "";
    if (lb.showModal) lb.showModal(); else lb.setAttribute("open", "");
  });
  if (lb) {
    $(".lb-close", lb).addEventListener("click", function () { lb.close(); });
    lb.addEventListener("click", function (e) { if (e.target === lb) lb.close(); });
  }

  /* ---------- Filtro da galeria ---------- */
  var mosaic = $("[data-mosaic]");
  if (mosaic) {
    var fbtns = $$(".filters button");
    fbtns.forEach(function (b) {
      b.addEventListener("click", function () {
        var f = b.getAttribute("data-f");
        fbtns.forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
        $$(".tile", mosaic).forEach(function (t) { t.hidden = f !== "todas" && t.getAttribute("data-cat") !== f; });
      });
    });
  }

  /* ---------- Prévia de foto nos serviços (segue o cursor) ---------- */
  var peek = $(".svc-peek");
  if (peek && !reduce && window.matchMedia("(hover: hover)").matches) {
    var pimg = $("img", peek), px = 0, py = 0, tx = 0, ty = 0, on = false;
    $$(".svc[data-peek]").forEach(function (s) {
      s.addEventListener("mouseenter", function () { pimg.src = s.getAttribute("data-peek"); peek.classList.add("on"); on = true; });
      s.addEventListener("mouseleave", function () { peek.classList.remove("on"); on = false; });
    });
    window.addEventListener("mousemove", function (e) { tx = e.clientX + 150; ty = e.clientY; });
    (function loop() { px += (tx - px) * .14; py += (ty - py) * .14; if (on) { peek.style.left = px + "px"; peek.style.top = py + "px"; } requestAnimationFrame(loop); })();
  }

  /* ---------- Formulário de agendamento → WhatsApp ---------- */
  var form = $("[data-wa-form]");
  if (form) {
    var prev = $("[data-wa-preview]");
    var val = function (n) { var el = form.elements[n]; return el ? String(el.value || "").trim() : ""; };
    var checked = function (n) { return $$('input[name="' + n + '"]:checked', form).map(function (i) { return i.value; }); };
    var fmtDate = function (s) {
      if (!s) return "";
      var p = s.split("-"); var d = new Date(+p[0], +p[1] - 1, +p[2]);
      var dias = ["domingo", "segunda", "terça", "quarta", "quinta", "sexta", "sábado"];
      return p[2] + "/" + p[1] + "/" + p[0] + " (" + dias[d.getDay()] + ")";
    };
    var msg = function () {
      var L = ["Olá, Cris! Vim pelo site e gostaria de agendar.", ""];
      if (val("nome")) L.push("*Nome:* " + val("nome"));
      if (val("idade")) L.push("*Idade:* " + val("idade") + " anos");
      var sv = checked("servico"); if (sv.length) L.push("*Serviço:* " + sv.join(", "));
      var dt = fmtDate(val("data"));
      var ag = [dt, val("hora") ? "às " + val("hora") : "", checked("periodo")[0] ? "período: " + checked("periodo")[0].toLowerCase() : ""].filter(Boolean).join(", ");
      if (ag) L.push("*Sugestão de agenda:* " + ag);
      if (val("pessoas") && val("pessoas") !== "1") L.push("*Pessoas:* " + val("pessoas"));
      if (val("ocasiao")) L.push("*Ocasião:* " + val("ocasiao"));
      if (val("obs")) L.push("*Observações:* " + val("obs"));
      return L.join("\n");
    };
    var render = function () {
      if (!prev) return;
      var m = msg();
      if (m.split("\n").length <= 2) { prev.innerHTML = "<em>Sua mensagem aparece aqui enquanto você preenche…</em>"; return; }
      prev.textContent = "";
      m.split("\n").forEach(function (line, k) {
        if (k) prev.appendChild(document.createTextNode("\n"));
        line.split(/(\*[^*]+\*)/).forEach(function (part) {
          if (/^\*[^*]+\*$/.test(part)) { var b = document.createElement("b"); b.textContent = part.slice(1, -1); prev.appendChild(b); }
          else if (part) prev.appendChild(document.createTextNode(part));
        });
      });
      var now = new Date(); prev.setAttribute("data-time", String(now.getHours()).padStart(2, "0") + ":" + String(now.getMinutes()).padStart(2, "0"));
    };
    /* serviço vindo da página de serviços (?servico=Noivas) */
    var q = new URLSearchParams(location.search).get("servico");
    if (q) {
      var map = { "Noivas": "Noiva", "Madrinhas e convidadas": "Convidada", "15 anos e formaturas": "15 anos", "Cabelo": "Corte e cor", "Maquiagem social": "Maquiagem social", "Visagismo e imagem": "Visagismo" };
      var target = map[q] || q;
      $$('input[name="servico"]', form).forEach(function (i) { if (i.value === target) i.checked = true; });
    }
    var dateIn = form.elements.data;
    if (dateIn) { var t = new Date(); dateIn.min = t.getFullYear() + "-" + String(t.getMonth() + 1).padStart(2, "0") + "-" + String(t.getDate()).padStart(2, "0"); }
    form.addEventListener("input", function (e) { render(); var f = e.target.closest("[data-field]"); if (f) f.classList.remove("invalid"); });
    form.addEventListener("change", render);
    render();
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var bad = [];
      if (!val("nome")) bad.push("nome");
      var idade = +val("idade"); if (!idade || idade < 1 || idade > 120) bad.push("idade");
      if (!checked("servico").length) bad.push("servico");
      if (!val("data")) bad.push("data");
      $$("[data-field]", form).forEach(function (f) { f.classList.toggle("invalid", bad.indexOf(f.getAttribute("data-field")) > -1); });
      if (bad.length) {
        var first = $('[data-field="' + bad[0] + '"]', form);
        first.scrollIntoView({ behavior: "smooth", block: "center" });
        var inp = $("input", first); if (inp) setTimeout(function () { inp.focus({ preventScroll: true }); }, 350);
        return;
      }
      window.open("https://wa.me/" + form.getAttribute("data-wa") + "?text=" + encodeURIComponent(msg()), "_blank", "noopener");
    });
  }

  /* ---------- Rodapé ---------- */
  $$("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });
  $$("[data-top]").forEach(function (b) { b.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: "smooth" }); }); });

  onScroll();
})();
