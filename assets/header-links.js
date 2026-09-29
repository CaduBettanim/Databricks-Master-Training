// Atalhos "Setup" e "Setup guiado" no canto superior direito do cabeçalho.
// Usa o href do logo (base_url relativo) para funcionar em qualquer
// domínio/profundidade; document$ recria os links na navegação instantânea.
function initHeaderLinks() {
  var inner = document.querySelector(".md-header__inner");
  var logo = document.querySelector(".md-header__button.md-logo");
  if (!inner || !logo || inner.querySelector(".md-ext-links")) return;

  var base = logo.getAttribute("href") || ".";
  if (base.charAt(base.length - 1) !== "/") base += "/";

  var items = [
    ["00%20-%20Setup/", "Setup"],
    ["00%20-%20Setup/Setup%20guiado/", "Setup guiado"]
  ];

  var nav = document.createElement("nav");
  nav.className = "md-ext-links";
  nav.setAttribute("aria-label", "Atalhos");
  items.forEach(function (it) {
    var a = document.createElement("a");
    a.href = base + it[0];
    a.textContent = it[1];
    nav.appendChild(a);
  });

  var title = inner.querySelector(".md-header__title");
  (title || logo).insertAdjacentElement("afterend", nav);
}

if (typeof document$ !== "undefined") {
  document$.subscribe(initHeaderLinks);
} else {
  document.addEventListener("DOMContentLoaded", initHeaderLinks);
}
