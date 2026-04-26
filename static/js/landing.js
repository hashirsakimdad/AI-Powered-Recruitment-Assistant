/**
 * Landing page enhancements:
 * - Hero morphing text
 * - Nav morphing word loop
 * - Scroll reveal (fade-in-up + stagger)
 * - Count-up stats (IntersectionObserver + rAF)
 * - How-it-works line dash animation
 */

(function () {
  "use strict";

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  function isLanding() {
    return Boolean($("[data-landing]"));
  }

  // ----------------------------
  // Morphing text (crossfade)
  // ----------------------------
  function setupMorphText(el, words, intervalMs = 2200) {
    if (!el || !words?.length) return;

    let idx = 0;
    el.textContent = words[idx];
    el.style.opacity = "1";

    const tick = () => {
      const next = words[(idx + 1) % words.length];
      el.classList.add("morph-fade-out");
      window.setTimeout(() => {
        el.textContent = next;
        el.classList.remove("morph-fade-out");
        el.classList.add("morph-fade-in");
        window.setTimeout(() => el.classList.remove("morph-fade-in"), 620);
        idx = (idx + 1) % words.length;
      }, 620);
    };

    window.setInterval(tick, intervalMs);
  }

  // ----------------------------
  // Scroll reveal + stagger
  // ----------------------------
  function setupReveal() {
    const targets = $$("[data-reveal]");
    if (!targets.length) return;

    const io = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          if (!e.isIntersecting) continue;
          const node = e.target;
          node.classList.add("is-in");

          const group = node.getAttribute("data-reveal-group");
          if (group) {
            const groupItems = $$(`[data-reveal-item="${group}"]`);
            groupItems.forEach((item, i) => {
              item.style.transitionDelay = `${i * 0.1}s`;
              item.classList.add("is-in");
            });
          }

          io.unobserve(node);
        }
      },
      { threshold: 0.2 }
    );

    targets.forEach((t) => io.observe(t));
  }

  // ----------------------------
  // Count up stats
  // ----------------------------
  function setupCountUp() {
    const nums = $$("[data-countup]");
    if (!nums.length) return;

    const animate = (el) => {
      const raw = el.getAttribute("data-countup") || "0";
      const isLessThan = raw.trim().startsWith("<");
      const hasPlus = raw.includes("+");

      // extract number portion (e.g. "2,400+" -> 2400, "< 15sec" -> 15)
      const match = raw.replace(/,/g, "").match(/(\d+(\.\d+)?)/);
      const target = match ? Number(match[1]) : 0;

      const duration = 2000;
      const start = performance.now();

      const step = (now) => {
        const t = Math.min(1, (now - start) / duration);
        // easeOutCubic
        const eased = 1 - Math.pow(1 - t, 3);
        const val = Math.round(target * eased);

        let out = val.toLocaleString();
        if (isLessThan) out = `< ${out}`;
        if (hasPlus && !isLessThan) out = `${out}+`;
        if (/sec/i.test(raw)) out = `${isLessThan ? "< " : ""}${val}sec`;

        el.textContent = out;

        if (t < 1) requestAnimationFrame(step);
      };

      requestAnimationFrame(step);
    };

    const io = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          if (!e.isIntersecting) continue;
          animate(e.target);
          io.unobserve(e.target);
        }
      },
      { threshold: 0.2 }
    );

    nums.forEach((n) => io.observe(n));
  }

  // ----------------------------
  // Dashed line animation trigger
  // ----------------------------
  function setupDashLine() {
    const line = $(".how-line");
    if (!line) return;
    const io = new IntersectionObserver(
      (entries) => {
        if (!entries[0]?.isIntersecting) return;
        line.classList.add("is-animating");
        io.disconnect();
      },
      { threshold: 0.2 }
    );
    io.observe(line);
  }

  // ----------------------------
  // Boot
  // ----------------------------
  document.addEventListener("DOMContentLoaded", () => {
    if (!isLanding()) return;

    setupMorphText($("[data-morph='hero']"), [
      "top talent",
      "perfect matches",
      "dream candidates",
      "the right hire",
    ]);

    setupMorphText($("[data-morph='nav']"), [
      "Smarter Hiring",
      "AI Screening",
      "Better Matches",
      "Faster Recruiting",
    ], 2400);

    setupReveal();
    setupCountUp();
    setupDashLine();
  });
})();

