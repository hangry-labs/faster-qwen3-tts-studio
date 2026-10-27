// SPDX-License-Identifier: Apache-2.0. Copyright 2026 Hangry Labs.
(() => {
  const content = document.querySelector('.readme-content');
  if (!content) return;
  // README HTML anchors remain useful on GitHub; map them to rendered pages here.
  const pages = JSON.parse(document.querySelector('#hangry-page-map').textContent);
  const destinations = new Map(Object.entries(pages).map(([source,target]) => [new URL(source,location.origin).pathname,target]));
  const base = document.body.dataset.baseurl || '';
  for (const anchor of content.querySelectorAll('a[href]')) {
    const target = new URL(anchor.href,location.href);
    if (target.origin !== location.origin) continue;
    if (destinations.has(target.pathname)) {
      anchor.href = destinations.get(target.pathname)+target.search+target.hash;
    } else if (document.body.dataset.repository && /\.(?:md|py|ps1|toml|yml|gemspec)$/.test(target.pathname) && target.pathname.startsWith(base+'/')) {
      anchor.href = document.body.dataset.repository+'/blob/'+document.body.dataset.sourceBranch+'/'+target.pathname.slice(base.length+1)+target.hash;
    }
  }
  const header = document.querySelector('.site-header');
  const updateHeader = () => document.documentElement.style.setProperty('--header-height', `${header.getBoundingClientRect().height}px`);
  new ResizeObserver(updateHeader).observe(header);
  updateHeader();

  const headings = [...content.querySelectorAll('h2[id]')];
  const navigation = document.querySelector('#page-sections');
  const toc = document.querySelector('#section-index');
  for (const heading of headings) {
    const link = document.createElement('a');
    link.href = `#${heading.id}`;
    link.textContent = heading.textContent;
    navigation.append(link);
  }
  if (!headings.length) toc.parentElement.hidden = true;
  const compact = matchMedia('(max-width: 900px)');
  const fitToc = () => { toc.open = !compact.matches; };
  fitToc(); compact.addEventListener('change', fitToc);
  const links = [...navigation.querySelectorAll('a')];
  const sectionObserver = new IntersectionObserver(entries => {
    const first = entries.filter(entry => entry.isIntersecting).sort((a,b) => a.boundingClientRect.top-b.boundingClientRect.top)[0];
    if (!first) return;
    for (const link of links) {
      if (link.hash === `#${first.target.id}`) link.setAttribute('aria-current','location');
      else link.removeAttribute('aria-current');
    }
  }, {rootMargin:'-10% 0px -65% 0px'});
  headings.forEach(heading => sectionObserver.observe(heading));

  function revealHash() {
    let target;
    try { target = document.getElementById(decodeURIComponent(location.hash.slice(1))); } catch { return; }
    if (!target) return;
    const parents = [];
    for (let node=target.parentElement; node; node=node.parentElement) if (node.tagName === 'DETAILS') parents.push(node);
    parents.reverse().forEach(node => { node.open = true; });
    if (parents.length) requestAnimationFrame(() => target.scrollIntoView());
  }
  addEventListener('hashchange',revealHash);
  if (location.hash) revealHash();

  for (const table of content.querySelectorAll('table')) {
    const wrapper = document.createElement('div');
    wrapper.className = 'table-scroll'; wrapper.tabIndex = 0;
    wrapper.setAttribute('role','region'); wrapper.setAttribute('aria-label','Scrollable table');
    table.before(wrapper); wrapper.append(table);
  }
  for (const pre of content.querySelectorAll('pre')) {
    const code = pre.querySelector('code');
    if (!code) continue;
    const button = document.createElement('button');
    button.className = 'copy-code'; button.type = 'button'; button.textContent = 'Copy';
    button.setAttribute('aria-label','Copy code');
    button.addEventListener('click',async () => {
      try {
        await navigator.clipboard.writeText(code.textContent);
        button.textContent = 'Copied';
        document.querySelector('#copy-status').textContent = 'Code copied to clipboard.';
      } catch {
        const range = document.createRange(); range.selectNodeContents(code);
        const selection = getSelection(); selection.removeAllRanges(); selection.addRange(range);
        document.querySelector('#copy-status').textContent = 'Code selected. Use your copy shortcut.';
      }
      setTimeout(() => { button.textContent = 'Copy'; },1800);
    });
    pre.prepend(button);
  }

  const canvas = document.querySelector('#hangry-background');
  const context = canvas.getContext('2d');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let drops = [], frame = null, last = 0;
  function resize() {
    canvas.width = innerWidth; canvas.height = innerHeight;
    drops = Array.from({length:Math.ceil(innerWidth/20)},() => Math.random()*-60);
  }
  function draw(now) {
    if (document.hidden || reduced.matches) { frame = null; return; }
    if (now-last >= 120) {
      last = now;
      context.fillStyle = 'rgba(0,0,0,.12)'; context.fillRect(0,0,canvas.width,canvas.height);
      context.fillStyle = '#ff6b00'; context.font = '14px monospace';
      drops.forEach((drop,index) => {
        context.fillText('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'[Math.floor(Math.random()*36)],index*20,drop*20);
        drops[index] = drop*20>canvas.height && Math.random()>.97 ? 0 : drop+1;
      });
    }
    frame = requestAnimationFrame(draw);
  }
  function animate() {
    if (frame !== null) cancelAnimationFrame(frame);
    frame = null;
    if (document.body.dataset.background === 'matrix' && !document.hidden && !reduced.matches) frame = requestAnimationFrame(draw);
    else context.clearRect(0,0,canvas.width,canvas.height);
  }
  resize(); animate();
  addEventListener('resize',resize); document.addEventListener('visibilitychange',animate); reduced.addEventListener('change',animate);
})();
