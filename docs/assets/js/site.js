/* Small progressive enhancements. The publication remains readable without JS. */
(() => {
  "use strict";
  const assetRoot = new URL("../", document.currentScript.src);
  const initialize = () => {
    document.querySelectorAll(".md-typeset__scrollwrap").forEach((table, index) => {
      table.tabIndex = 0;
      table.setAttribute("role", "region");
      table.setAttribute("aria-label", `Research table ${index + 1}; scroll horizontally to read every column`);
    });
    if (!matchMedia("(prefers-reduced-motion: reduce)").matches && "IntersectionObserver" in window) {
      const observer = new IntersectionObserver(entries => entries.forEach(entry => {
        if (entry.isIntersecting) { entry.target.classList.add("is-visible"); observer.unobserve(entry.target); }
      }), {threshold: 0.15});
      document.querySelectorAll(".wl-reveal:not(.is-visible)").forEach(item => observer.observe(item));
    }
    const expressions = document.querySelectorAll(".arithmatex:not([data-rendered])");
    if (!expressions.length) return;
    const render = () => expressions.forEach(element => {
      const text = element.textContent.trim();
      const displayMode = text.startsWith("\\[");
      const source = text.replace(/^\\[\[(]/, "").replace(/\\[\])]$/, "");
      window.katex.render(source, element, {displayMode, throwOnError: false, strict: "warn", trust: false, output: "htmlAndMathml"});
      element.dataset.rendered = "true";
    });
    if (window.katex) {render(); return;}
    const link = document.createElement("link");
    link.rel = "stylesheet"; link.href = new URL("vendor/katex/katex.min.css", assetRoot); document.head.append(link);
    const script = document.createElement("script");
    script.src = new URL("vendor/katex/katex.min.js", assetRoot); script.onload = render;
    script.onerror = () => console.warn("Math renderer unavailable; the original formula text remains visible.");
    document.head.append(script);
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", initialize, {once:true}); else initialize();
})();
