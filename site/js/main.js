/* Blueline Travels — Mosul · vanilla JS, no dependencies */
(function () {
  'use strict';

  var d = document;

  /* ---------- Sticky header ---------- */
  var header = d.querySelector('.site-header');
  function onScrollHeader() {
    if (header) header.classList.toggle('scrolled', window.scrollY > 60);
  }
  window.addEventListener('scroll', onScrollHeader, { passive: true });
  onScrollHeader();

  /* ---------- Mobile nav ---------- */
  var toggle = d.querySelector('.nav-toggle');
  var nav = d.querySelector('.nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  /* ---------- Dropdown (tap/keyboard on small screens) ---------- */
  d.querySelectorAll('.has-sub > a').forEach(function (link) {
    link.addEventListener('click', function (e) {
      if (window.matchMedia('(max-width: 991px)').matches) {
        e.preventDefault();
        var li = link.parentElement;
        var open = li.classList.toggle('open');
        link.setAttribute('aria-expanded', open ? 'true' : 'false');
      }
    });
  });

  /* ---------- Hero Ken Burns slideshow ---------- */
  var slides = d.querySelectorAll('.hero .slide');
  if (slides.length > 1) {
    // Progressive loading: slide 0 is already painted (inline background).
    // Each later slide's image is fetched only shortly before it's shown, so
    // the ~0.5 MB of slides 2 & 3 never touch the initial page load.
    var loadSlide = function (i) {
      var s = slides[i];
      if (s && s.getAttribute('data-bg') && !s.style.backgroundImage) {
        s.style.backgroundImage = 'url(' + s.getAttribute('data-bg') + ')';
      }
    };
    var current = 0;
    // prime slide 1 a few seconds after load, ready for the first transition
    setTimeout(function () { loadSlide(1); }, 4500);
    setInterval(function () {
      var next = (current + 1) % slides.length;
      slides[current].classList.remove('active');
      slides[next].classList.add('active');
      current = next;
      // fetch the slide *after* this one so it's decoded before its turn
      loadSlide((current + 1) % slides.length);
    }, 9000);
  }

  /* ---------- Lazy section backgrounds ---------- */
  // Below-the-fold sections carry their bg in data-bg-section and get it only
  // as they approach the viewport, keeping them off the initial load.
  var bgSections = d.querySelectorAll('[data-bg-section]');
  var setBg = function (el) {
    if (el.getAttribute('data-bg-section')) {
      el.style.backgroundImage = 'url(' + el.getAttribute('data-bg-section') + ')';
      el.removeAttribute('data-bg-section');
    }
  };
  if ('IntersectionObserver' in window && bgSections.length) {
    var bgo = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { setBg(en.target); bgo.unobserve(en.target); }
      });
    }, { rootMargin: '300px' });
    bgSections.forEach(function (el) { bgo.observe(el); });
    // Guaranteed fallback: once the critical load is done, ensure every
    // section bg is loaded even if its observer never fired (fast scroll,
    // background tab, etc.). Still off the initial critical path.
    var ensureAllBgs = function () {
      setTimeout(function () { bgSections.forEach(setBg); }, 1500);
    };
    if (d.readyState === 'complete') ensureAllBgs();
    else window.addEventListener('load', ensureAllBgs);
  } else {
    bgSections.forEach(setBg);
  }

  /* ---------- Scroll reveal ---------- */
  var revealEls = d.querySelectorAll('.fade-up');
  if ('IntersectionObserver' in window && revealEls.length) {
    var ro = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          en.target.classList.add('in-view');
          ro.unobserve(en.target);
        }
      });
    }, { threshold: 0.12 });
    revealEls.forEach(function (el) { ro.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add('in-view'); });
  }

  /* ---------- Count-up numbers ---------- */
  function animateCount(el) {
    var target = parseInt(el.getAttribute('data-count'), 10) || 0;
    var dur = 1800;
    var t0 = null;
    function frame(t) {
      if (!t0) t0 = t;
      var p = Math.min((t - t0) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = '+' + Math.round(target * eased).toLocaleString('en-US');
      if (p < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }
  var counters = d.querySelectorAll('[data-count]');
  if ('IntersectionObserver' in window && counters.length) {
    var co = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          animateCount(en.target);
          co.unobserve(en.target);
        }
      });
    }, { threshold: 0.4 });
    counters.forEach(function (el) { co.observe(el); });
  } else {
    counters.forEach(function (el) {
      el.textContent = '+' + (parseInt(el.getAttribute('data-count'), 10) || 0).toLocaleString('en-US');
    });
  }

  /* ---------- Scroll progress ring / back to top ---------- */
  var ring = d.querySelector('.progress-ring');
  if (ring) {
    var circle = ring.querySelector('circle');
    var C = 126; // 2πr, r=20
    function onScrollRing() {
      var h = d.documentElement.scrollHeight - window.innerHeight;
      var p = h > 0 ? window.scrollY / h : 0;
      circle.style.strokeDashoffset = String(C * (1 - p));
      ring.classList.toggle('show', window.scrollY > 250);
    }
    window.addEventListener('scroll', onScrollRing, { passive: true });
    onScrollRing();
    ring.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  /* ---------- Footer year ---------- */
  var yearEl = d.getElementById('year');
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());

  /* ---------- Contact form ---------- */
  var form = d.querySelector('.contact-form');
  if (form) {
    form.addEventListener('submit', function (e) {
      var status = form.querySelector('.form-status');
      var action = form.getAttribute('action') || '';
      if (action.indexOf('YOUR_FORM_ID') !== -1) {
        // Formspree not configured yet — fall back to a prefilled email draft
        e.preventDefault();
        var get = function (n) { var f = form.querySelector('[name="' + n + '"]'); return f ? f.value : ''; };
        var to = form.getAttribute('data-mailto') || '';
        var subject = encodeURIComponent(get('subject') || 'Website enquiry');
        var body = encodeURIComponent(
          'Name: ' + get('name') + '\nEmail: ' + get('email') +
          '\nPhone: ' + get('phone') + '\n\n' + get('message'));
        window.location.href = 'mailto:' + to + '?subject=' + subject + '&body=' + body;
        return;
      }
      // Formspree configured — submit via fetch for a soft inline confirmation
      e.preventDefault();
      var data = new FormData(form);
      fetch(action, { method: 'POST', body: data, headers: { Accept: 'application/json' } })
        .then(function (res) {
          if (res.ok) {
            form.reset();
            status.textContent = 'Your message was sent successfully.';
            status.classList.remove('error');
          } else {
            status.textContent = 'Something went wrong — please try again or email us directly.';
            status.classList.add('error');
          }
          status.classList.add('show');
        })
        .catch(function () {
          status.textContent = 'Network error — please try again or email us directly.';
          status.classList.add('error', 'show');
        });
    });
  }
})();
