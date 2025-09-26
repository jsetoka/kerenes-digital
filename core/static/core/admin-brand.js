(function () {
  // --- CONFIG GLOBALE
  const LOGO_URL     = "/static/core/img/logo-kerasgo.png";
  const HEADER_H     = 112,  HEADER_MAX_W = 170;
  const LOGIN_H      = 80,  LOGIN_MAX_W  = 260;

  // --- HELPERS GÉNÉRIQUES
  function closestContainer(node) { return node?.closest?.("a,button,div,span,header") || node?.parentElement || null; }
  function empty(el) { while (el && el.firstChild) el.removeChild(el.firstChild); }
  function injectImg(container, src, maxW, h) {
    if (!container) return false;
    if (container.__dibosReplaced) return true;
    empty(container);
    const img = document.createElement("img");
    img.src = src; img.alt = "Logo";
    img.style.display = "block";
    img.style.objectFit = "contain";
    img.style.setProperty("height", `${h}px`, "important");
    img.style.setProperty("max-width", `${maxW}px`, "important");
    img.style.setProperty("width", "auto", "important");
    container.appendChild(img);
    container.__dibosReplaced = true;
    return true;
  }

  // --- HEADER
  function headerSvgCandidates(root = document) {
    return Array.from(root.querySelectorAll(
      'header svg,[class*="header"] svg,[class*="brand"] svg,.w-app-header__brand svg,.w-header__brand svg,.w-header__logo svg,' +
      '.w-panel__header svg,.w-panel__brand svg' // drawer
    ));
  }
  function replaceHeaderOnce(root = document) {
    for (const svg of headerSvgCandidates(root)) {
      const r = svg.getBoundingClientRect();
      if (r.width >= 40 && r.height >= 20) {
        const container = closestContainer(svg);
        if (injectImg(container, LOGO_URL, HEADER_MAX_W, HEADER_H)) return true;
      }
    }
    return false;
  }

  // --- LOGIN
  function loginContainer(root = document) {
    return root.querySelector(".login-logo") || root.querySelector(".w-login__brand, .w-login__logo");
  }
  function replaceLoginOnce(root = document) {
    const box = loginContainer(root);
    if (!box) return false;
    return injectImg(box, LOGO_URL, LOGIN_MAX_W, LOGIN_H);
  }

  // --- FAB (bouton flottant) : détection par position écran
  function isBottomRight(el) {
    const r = el.getBoundingClientRect();
    const margin = 120; // px depuis le coin
    return r.width >= 40 && r.height >= 40 &&
           r.right >= (window.innerWidth - margin) &&
           r.bottom >= (window.innerHeight - margin);
  }


  function looksLikePages(el){
    const href  = (el.getAttribute?.("href") || "").toLowerCase();
    const aria  = (el.getAttribute?.("aria-label") || "").toLowerCase();
    const title = (el.getAttribute?.("title") || "").toLowerCase();
    return href.includes("/admin/pages")
        || aria.includes("page") || aria.includes("explorer") || aria.includes("pages")
        || title.includes("page") || title.includes("explorer") || title.includes("pages");
  }
  function isBottomRightOrParent(el){
    if (!el) return false;
    const pos = getComputedStyle(el).position;
    const positioned = ["fixed","absolute","sticky"].includes(pos);
    if (positioned && isBottomRight(el)) return true;
    // parfois le lien est dans un conteneur positionné
    const p = el.parentElement;
    if (p){
      const pPos = getComputedStyle(p).position;
      const pPositioned = ["fixed","absolute","sticky"].includes(pPos);
      if (pPositioned && isBottomRight(p)) return true;
    }
    return false;
  }
  
  function findFloatingButtons(root = document) {
    const nodes = Array.from(root.querySelectorAll('a,button,[role="button"]'));
    // 1) prioriser le vrai bouton "pages"
    let hits = nodes.filter(el => looksLikePages(el) && isBottomRightOrParent(el));
    if (hits.length) return hits;
  
    // 2) fallback : si on ne trouve pas via aria/href, prends le 1er “bouton” bottom-right
    const generic = nodes.filter(el => isBottomRightOrParent(el));
    return generic;
  }
  
  function brandFabOnce(root = document) {
    const fabs = findFloatingButtons(root);
    let done = false;
    for (const fab of fabs) {
      // remplace l’icône interne (souvent un <svg>)
      const iconHost =
        fab.querySelector("svg") ||
        fab.querySelector("img") ||
        fab.firstElementChild ||
        fab;
      // on injecte une petite version du logo (taille bouton)
      if (injectFabIcon(iconHost)) {
        styleFabButton(fab);
        // ... après styleFabButton(fab); 
        fab.setAttribute("title", "Pages");
        fab.setAttribute("aria-label", "Pages");
        fab.style.setProperty("z-index","1000","important");

        done = true;
        // Option : styliser son menu contextuel s’il est déjà présent
        styleFabMenuNear(fab);
        
        break;
      }
    }
    return done;
  }
  function injectFabIcon(host) {
    if (!host) return false;
    // n’efface pas le bouton lui-même pour garder l’accessibilité/click
    while (host.firstChild) host.removeChild(host.firstChild);
    const img = document.createElement("img");
    img.src = LOGO_URL; img.alt = "Menu";
    img.style.display = "block";
    img.style.width = "60%";
    img.style.height = "60%";
    img.style.margin = "20%"; // centre dans le cercle
    host.appendChild(img);
    return true;
  }
  function styleFabButton(fab) {
    fab.style.setProperty("width", "56px", "important");
    fab.style.setProperty("height", "56px", "important");
    fab.style.setProperty("border-radius", "50%", "important");
    fab.style.setProperty("background", "#001f3f", "important");   // bleu foncé
    fab.style.setProperty("box-shadow", "0 6px 18px rgba(0,0,0,.25)", "important");
    fab.style.setProperty("display", "inline-flex", "important");
    fab.style.setProperty("align-items", "center", "important");
    fab.style.setProperty("justify-content", "center", "important");
    fab.style.setProperty("padding", "0", "important");
  }
  // tente de trouver un menu “proche” du FAB pour le styliser
  function styleFabMenuNear(fab) {
    const menus = Array.from(document.querySelectorAll('[role="menu"],[class*="menu"],[class*="actions"]'))
      .filter(el => {
        const r1 = fab.getBoundingClientRect(), r2 = el.getBoundingClientRect();
        const dx = Math.abs(r1.right - r2.right), dy = Math.abs(r1.bottom - r2.top);
        return dx < 200 && dy < 300; // à proximité
      });
    for (const m of menus) {
      m.style.setProperty("border-radius", "12px", "important");
      m.style.setProperty("box-shadow", "0 10px 30px rgba(0,0,0,.2)", "important");
      m.style.setProperty("overflow", "hidden", "important");
    }
  }

  // --- RUN
  function runAll(root = document) {
    replaceHeaderOnce(root);
    replaceLoginOnce(root);
    brandFabOnce(root);
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => runAll());
  } else {
    runAll();
  }

  // --- SPA support
  const obs = new MutationObserver((muts) => {
    for (const m of muts) {
      for (const node of m.addedNodes) {
        if (!(node instanceof Element)) continue;
        if (
          node.matches?.("header,[class*='header'],[class*='brand'],.login-logo,.w-login__brand,.w-login__logo,button,a,[role='button']") ||
          node.querySelector?.("svg,.login-logo,.w-login__brand,.w-login__logo,button,a,[role='button']")
        ) {
          runAll(node);
        }
      }
    }
  });
  obs.observe(document.documentElement, { childList: true, subtree: true });
})();
