/* ==========================================
   NAVBAR 27ZERO
========================================== */

const nav = document.querySelector(".nav");

if (nav) {
  const initialTheme = nav.classList.contains("nav--black")
    ? "nav--black"
    : "nav--white";

  const updateNavbar = () => {
    if (window.scrollY > 50) {
      nav.classList.remove("nav--white", "nav--black");
      nav.classList.add("nav--scrolled");
    } else {
      nav.classList.remove("nav--scrolled");
      nav.classList.add(initialTheme);
    }
  };

  window.addEventListener("scroll", updateNavbar);

  updateNavbar();
}

/* ==========================================
   WORK DROPDOWN
========================================== */

const workDropdown = document.querySelector(".nav-dropdown");

if (workDropdown) {
  const toggle = workDropdown.querySelector(".nav-dropdown-toggle");

  toggle.addEventListener("click", (e) => {
    e.stopPropagation();

    const open = workDropdown.classList.toggle("is-open");

    toggle.setAttribute("aria-expanded", open ? "true" : "false");
  });

  document.addEventListener("click", (e) => {
    if (
      workDropdown.classList.contains("is-open") &&
      !workDropdown.contains(e.target)
    ) {
      workDropdown.classList.remove("is-open");

      toggle.setAttribute("aria-expanded", "false");
    }
  });
}

/* ==========================================
   LANGUAGE SWITCHER
========================================== */

const languageSwitcher = document.querySelector(".lang-switcher");

if (languageSwitcher) {
  const button = languageSwitcher.querySelector(".lang-switcher-btn");

  button.addEventListener("click", (e) => {
    e.stopPropagation();

    const open = languageSwitcher.classList.toggle("is-open");

    button.setAttribute("aria-expanded", open ? "true" : "false");
  });

  document.addEventListener("click", (e) => {
    if (
      languageSwitcher.classList.contains("is-open") &&
      !languageSwitcher.contains(e.target)
    ) {
      languageSwitcher.classList.remove("is-open");

      button.setAttribute("aria-expanded", "false");
    }
  });
}
/* ==========================================
   MOBILE MENU
========================================== */

const hamburger = document.querySelector(".nav-hamburger");
const mobileMenu = document.querySelector(".nav-mobile-menu");
const mobileClose = document.querySelector(".nav-mobile-close");

if (hamburger && mobileMenu) {
  const openMenu = () => {
    mobileMenu.classList.add("is-open");

    hamburger.setAttribute("aria-expanded", "true");

    document.body.style.overflow = "hidden";
  };

  const closeMenu = () => {
    mobileMenu.classList.remove("is-open");

    hamburger.setAttribute("aria-expanded", "false");

    document.body.style.overflow = "";
  };

  hamburger.addEventListener("click", () => {
    if (mobileMenu.classList.contains("is-open")) {
      closeMenu();
    } else {
      openMenu();
    }
  });

  if (mobileClose) {
    mobileClose.addEventListener("click", closeMenu);
  }

  mobileMenu.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", closeMenu);
  });
}
/* ==========================================
   MOBILE WORK ACCORDION
========================================== */

const mobileGroup = document.querySelector(".nav-mobile-group");

if (mobileGroup) {
  const toggle = mobileGroup.querySelector(".nav-mobile-group-toggle");
  const content = mobileGroup.querySelector(".nav-mobile-group-content");

  toggle.addEventListener("click", () => {
    const open = mobileGroup.classList.contains("is-open");

    if (open) {
      content.style.height = content.scrollHeight + "px";

      requestAnimationFrame(() => {
        mobileGroup.classList.remove("is-open");

        toggle.setAttribute("aria-expanded", "false");

        content.style.height = "0px";
      });

      return;
    }

    mobileGroup.classList.add("is-open");

    toggle.setAttribute("aria-expanded", "true");

    content.style.height = content.scrollHeight + "px";

    content.addEventListener("transitionend", function handler(e) {
      if (e.propertyName !== "height") return;

      if (mobileGroup.classList.contains("is-open")) {
        content.style.height = "auto";
      }

      content.removeEventListener("transitionend", handler);
    });
  });
}
