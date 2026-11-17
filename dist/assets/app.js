(() => {
  'use strict';
  const appScript = document.querySelector('script[src*="assets/app.js"]');
  const siteBase = appScript ? new URL('..', appScript.src).pathname.replace(/\/$/, '') : '';
  const withBase = (path) => path.startsWith('/') ? `${siteBase}${path}` : path;
  const $ = (selector, parent = document) => parent.querySelector(selector);
  const $$ = (selector, parent = document) => [...parent.querySelectorAll(selector)];
  const escape = (text) => String(text ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const arrow = '<svg class="icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>';
  let products = [];
  let enquiryText = '';

  function toast(message) {
    window.dispatchEvent(new CustomEvent('avarthana:status',{detail:{message}}));
  }

  const menu = $('.menu-toggle');
  const mobileNav = $('#mobile-nav');
  const setMenuOpen = (open) => {
    if (!menu || !mobileNav) return;
    menu.setAttribute('aria-expanded', String(open));
    menu.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
    mobileNav.hidden = !open;
  };
  menu?.addEventListener('click', () => setMenuOpen(menu.getAttribute('aria-expanded') !== 'true'));
  mobileNav?.addEventListener('click', event => {
    if (event.target.closest('a')) setMenuOpen(false);
  });
  document.addEventListener('click', event => {
    if (mobileNav && !mobileNav.hidden && !event.target.closest('.site-header')) setMenuOpen(false);
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && mobileNav && !mobileNav.hidden) {
      setMenuOpen(false);
      menu?.focus();
    }
  });

  $$('dialog').forEach(dialog => {
    $('.dialog-close', dialog)?.addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', event => {
      if (event.target !== dialog) return;
      const rect = dialog.getBoundingClientRect();
      if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close();
    });
  });

  function renderSearch() {
    const query = $('#global-search').value.trim().toLowerCase();
    const results = products.filter(p => [p.title,p.subtitle,p.processor,p.category,p.family,p.summary].join(' ').toLowerCase().includes(query)).slice(0,7);
    $('#search-results').innerHTML = results.length ? results.map(p => `<a href="${withBase('/products/' + escape(p.slug) + '/')}"><img src="${escape(withBase(p.image))}" alt=""><span><strong>${escape(p.title)}</strong><small>${escape(p.subtitle)} · ${escape(p.processor)}</small></span>${arrow}</a>`).join('') : '<p>No matching products. Try “3U”, “RFSoC”, “Versal” or “LRU”.</p>';
  }
  $('.search-open')?.addEventListener('click', () => {
    renderSearch();
    $('#search-dialog').showModal();
    $('#global-search').focus();
  });
  $('#global-search')?.addEventListener('input', renderSearch);

  function setupCatalogue() {
    const form = $('#product-filters');
    if (!form) return;
    const sidebar = $('.catalogue-sidebar');
    const filterToggle = $('#filter-toggle');
    const activeFilterMeta = $('#active-filter-count');
    const params = new URLSearchParams(location.search);
    let hasUrlFilters = false;
    ['category','form','family'].forEach(key => {
      const values = params.getAll(key);
      if (values.length) hasUrlFilters = true;
      $$(`input[name="${key}"]`,form).forEach(input => { input.checked = values.includes(input.value); });
    });
    if (sidebar && filterToggle && hasUrlFilters) {
      sidebar.classList.add('is-open');
      filterToggle.setAttribute('aria-expanded', 'true');
    }
    filterToggle?.addEventListener('click', () => {
      const open = !sidebar.classList.contains('is-open');
      sidebar.classList.toggle('is-open', open);
      filterToggle.setAttribute('aria-expanded', String(open));
    });
    $('#catalogue-search').value = params.get('q') || '';
    const cards = $$('.catalogue-grid .product-card');
    const filter = (writeURL=true) => {
      const filters = Object.fromEntries(['category','form','family'].map(key => [key,$$(`input[name="${key}"]:checked`,form).map(x => x.value)]));
      const activeCount = Object.values(filters).reduce((sum, list) => sum + list.length, 0);
      if (activeFilterMeta) activeFilterMeta.textContent = activeCount ? `${activeCount} active` : 'Show';
      const query = $('#catalogue-search').value.trim().toLowerCase();
      let count = 0;
      cards.forEach(card => {
        const match = Object.entries(filters).every(([key,values]) => !values.length || values.includes(card.dataset[key])) && (!query || card.dataset.search.includes(query));
        card.hidden = !match;
        if (match) count++;
      });
      $('#result-count').textContent = count === cards.length ? `Showing all ${count} products` : `Showing ${count} of ${cards.length} products`;
      $('#no-products').hidden = count !== 0;
      if (writeURL) {
        const next = new URLSearchParams();
        Object.entries(filters).forEach(([key,values]) => values.forEach(value => next.append(key,value)));
        if (query) next.set('q',query);
        history.replaceState(null,'',location.pathname+(next.toString() ? '?'+next.toString() : ''));
      }
    };
    const reset = () => { form.reset(); $('#catalogue-search').value=''; $('#product-sort').value='featured'; sort(); filter(); };
    const sort = () => {
      const mode = $('#product-sort').value;
      const ordered = [...cards].sort((a,b) => mode==='name' ? a.querySelector('h3').textContent.localeCompare(b.querySelector('h3').textContent) : mode==='form' ? a.dataset.form.localeCompare(b.dataset.form) || Number(a.dataset.id)-Number(b.dataset.id) : Number(a.dataset.id)-Number(b.dataset.id));
      ordered.forEach(card => $('.catalogue-grid').appendChild(card));
    };
    form.addEventListener('change',() => filter());
    $('#catalogue-search').addEventListener('input',() => filter());
    $('#reset-filters').addEventListener('click',reset);
    $('#empty-reset').addEventListener('click',reset);
    $('#product-sort').addEventListener('change',sort);
    window.addEventListener('popstate', () => location.reload());
    filter(false);
  }
  setupCatalogue();

  $('#resource-search')?.addEventListener('input',event => {
    const query = event.target.value.trim().toLowerCase();
    let visible=0;
    $$('.resource-item').forEach(item => { item.hidden = !item.dataset.search.includes(query); if(!item.hidden) visible++; });
    $('#resource-empty').hidden = visible>0;
  });

  const enquiry = $('#enquiry-form');
  if (enquiry) {
    const params = new URLSearchParams(location.search);
    const slug = params.get('product');
    if (slug) {
      const option = $$('#enquiry-product option').find(x => x.dataset.slug===slug);
      if (option) $('#enquiry-product').value=option.value;
    }
    const expertiseMap = {
      radar: 'Advanced Radars & RF Solutions',
      embedded: 'Embedded Engineering',
      aerospace: 'Aerospace & Defence',
      hardware: 'Hardware Systems',
      software: 'Interactive Application Software'
    };
    const applicationMap = {
      defence: 'Defence & Radar',
      aerospace: 'Aerospace',
      space: 'Space',
      industrial: 'Industrial & Research'
    };
    const expertise = params.get('expertise');
    if (expertise) {
      const label = expertiseMap[expertise] || expertise;
      const option = $$('#enquiry-product option').find(x => x.value === label);
      enquiry.elements.product.value = option ? option.value : 'Custom engineering';
      if (!enquiry.elements.message.value.trim()) {
        enquiry.elements.message.value = `Area of interest: ${label}.\n\n`;
      }
    }
    const appParam = params.get('application');
    if (appParam) {
      const appLabel = applicationMap[appParam] || appParam;
      if (!enquiry.elements.message.value.trim()) {
        enquiry.elements.message.value = `Application: ${appLabel}.\n\n`;
      }
    }
    if (params.get('topic')) enquiry.elements.product.value = 'Custom engineering';
    enquiry.addEventListener('submit',event => {
      event.preventDefault();
      if(!enquiry.reportValidity()) return;
      const values = new FormData(enquiry);
      const subject = `Avarthana enquiry — ${values.get('product')}`;
      enquiryText = `Hello Avarthana team,\n\n${values.get('message')}\n\nProduct / interest: ${values.get('product')}\n\nName: ${values.get('name')}\nOrganization: ${values.get('organization')}\nEmail: ${values.get('email')}\n`;
      $('#enquiry-ready').hidden=false;
      toast('Email draft ready · Review and send it in your email application.');
      location.href=`mailto:info@avarthana.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(enquiryText)}`;
    });
    $('#copy-enquiry')?.addEventListener('click',async () => {
      try { await navigator.clipboard.writeText(enquiryText); toast('Enquiry copied. Paste it into your email to info@avarthana.com.'); }
      catch {
        const text = document.createElement('textarea');
        text.value=enquiryText; text.setAttribute('aria-label','Your enquiry');
        $('#enquiry-ready').appendChild(text);text.focus();text.select();
        toast('Select and copy your enquiry below.');
      }
    });
  }

  fetch(withBase('/assets/products.json')).then(response => {
    if(!response.ok) throw new Error('Product index unavailable');
    return response.json();
  }).then(data => {
    products=data;
    if($('#search-dialog').open) renderSearch();
  }).catch(() => {
    $('#search-results').innerHTML=`<p>Product search is temporarily unavailable. <a href="${withBase('/products/')}">Browse all products</a>.</p>`;
  });
})();
