(() => {
  const $=s=>document.querySelector(s);
  const all=s=>[...document.querySelectorAll(s)];
  const reduced=matchMedia('(prefers-reduced-motion: reduce)');
  // Never hide baseline content when JS or motion support is unavailable.
  if('IntersectionObserver' in window&&!reduced.matches){
    const elements=all('main .section-heading, main .portfolio-introduction, main .family-tile, main .platform-tile, main .application-card, main .product-card, main .application-detail, main .about-layout, main .capability-detail, main .download-product, main .document-section');
    document.documentElement.classList.add('motion-ready');
    const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{
      if(entry.isIntersecting){entry.target.classList.add('is-revealed');observer.unobserve(entry.target);}
    }),{threshold:.06,rootMargin:'0px 0px -10px 0px'});
    elements.forEach((element,i)=>{element.dataset.reveal='';element.style.setProperty('--reveal-delay',`${i%3*55}ms`);observer.observe(element);});
    reduced.addEventListener('change',event=>{if(event.matches){document.documentElement.classList.remove('motion-ready');observer.disconnect();}});
  }
  if($('#resource-family')){
    const items=all('.download-product');
    function filter(){
      const query=$('#resource-search').value.trim().toLowerCase();
      const family=$('#resource-family').value;
      const type=$('#resource-type').value;
      let count=0;
      items.forEach(item=>{
        const match=(!query||item.dataset.search.includes(query))&&(!family||item.dataset.category===family)&&(type!=='diagram'||item.dataset.hasDiagram==='true');
        item.hidden=!match;if(match)count++;
        [...item.querySelectorAll('[data-doc-type]')].forEach(link=>{link.hidden=type!=='all'&&link.dataset.docType!==type;});
        const unavailable=item.querySelector('.document-unavailable');
        if(unavailable)unavailable.hidden=type==='datasheet';
      });
      $('#document-result-count').textContent=`${count} ${count===1?'product':'products'}${type==='diagram'?' with block diagrams':type==='datasheet'?' with datasheets':''}`;
      $('#resource-empty').hidden=count!==0;
    }
    $('#resource-search').addEventListener('input',filter);
    $('#resource-family').addEventListener('change',filter);
    $('#resource-type').addEventListener('change',filter);
    $('#reset-document-filters').addEventListener('click',()=>{$('#resource-search').value='';$('#resource-family').value='';$('#resource-type').value='all';filter();});
    filter();
  }
})();
