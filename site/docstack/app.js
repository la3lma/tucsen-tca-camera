(() => {
  const root = document.documentElement;
  const storedTheme = localStorage.getItem("camera-docstack-theme");
  if (storedTheme === "dark") root.dataset.theme = "dark";

  const tools = document.createElement("div");
  tools.className = "site-tools";
  tools.setAttribute("aria-label", "Document tools");
  tools.innerHTML = `
    <button type="button" data-action="theme" aria-label="Toggle colour theme">Theme</button>
    <button type="button" data-action="print" aria-label="Print or save as PDF">Print</button>
    <button type="button" data-action="top" aria-label="Return to top">Top</button>`;
  document.body.appendChild(tools);

  tools.addEventListener("click", (event) => {
    const button = event.target.closest("button");
    if (!button) return;
    if (button.dataset.action === "theme") {
      const next = root.dataset.theme === "dark" ? "light" : "dark";
      if (next === "dark") root.dataset.theme = "dark";
      else delete root.dataset.theme;
      localStorage.setItem("camera-docstack-theme", next);
    }
    if (button.dataset.action === "print") window.print();
    if (button.dataset.action === "top") window.scrollTo({ top: 0, behavior: "smooth" });
  });

  const taskCards = [...document.querySelectorAll(".task-card")];
  const filters = [...document.querySelectorAll("[data-task-filter]")];
  const progress = document.querySelector(".task-progress");
  const complete = taskCards.filter((card) => card.dataset.state === "complete").length;
  const ready = taskCards.filter((card) => card.dataset.state === "ready").length;
  if (progress) progress.textContent = `${complete}/${taskCards.length} complete · ${ready} ready`;

  filters.forEach((button) => {
    button.addEventListener("click", () => {
      const filter = button.dataset.taskFilter;
      filters.forEach((candidate) => candidate.setAttribute("aria-pressed", String(candidate === button)));
      taskCards.forEach((card) => {
        card.hidden = filter !== "all" && card.dataset.state !== filter;
      });
    });
  });

  const tocLinks = [...document.querySelectorAll("nav#TOC a[href^='#']")];
  const sectionById = new Map(
    tocLinks
      .map((link) => document.getElementById(decodeURIComponent(link.hash.slice(1))))
      .filter(Boolean)
      .map((section) => [section.id, section])
  );
  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver((entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0];
      if (!visible) return;
      tocLinks.forEach((link) => {
        const active = decodeURIComponent(link.hash.slice(1)) === visible.target.id;
        if (active) link.setAttribute("aria-current", "true");
        else link.removeAttribute("aria-current");
      });
    }, { rootMargin: "-12% 0px -74% 0px", threshold: [0, 1] });
    sectionById.forEach((section) => observer.observe(section));
  }
})();

