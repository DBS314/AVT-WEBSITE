(() => {
  const panel=document.querySelector('.activity-status');
  if(!panel)return;
  const message=panel.querySelector('#activity-message');
  const dismiss=panel.querySelector('.activity-dismiss');
  let timer;
  function hide(){clearTimeout(timer);panel.classList.remove('is-visible');document.documentElement.classList.remove('status-visible');dismiss.tabIndex=-1;}
  function show(text,duration=4500){
    if(typeof text!=='string'||!text.trim())return;
    clearTimeout(timer);message.textContent=text;panel.classList.add('is-visible');document.documentElement.classList.add('status-visible');dismiss.tabIndex=0;
    timer=setTimeout(hide,duration);
  }
  dismiss.addEventListener('click',hide);
  panel.addEventListener('mouseenter',()=>clearTimeout(timer));
  panel.addEventListener('mouseleave',()=>{timer=setTimeout(hide,1800);});
  panel.addEventListener('focusin',()=>clearTimeout(timer));
  panel.addEventListener('focusout',()=>{timer=setTimeout(hide,1800);});
  window.addEventListener('avarthana:status',event=>show(event.detail?.message));
  document.addEventListener('click',event=>{
    const link=event.target.closest('a');if(!link)return;
    if(link.hasAttribute('download')||/\/downloads\//.test(link.pathname)){
      const filename=decodeURIComponent(link.pathname.split('/').pop()).replace(/\.(pdf|zip)$/i,'').replace(/-/g,' ');
      const label=(link.getAttribute('aria-label')||filename).replace(/^Download /i,'');
      show('Download requested · '+label);
    }else if(link.protocol==='mailto:')show('Opening your email application.');
  });
  // One brief release note per browser session; no account sign-in is required.
  try{
    const key='avarthana-release-expertise-2026-11';
    if(!sessionStorage.getItem(key)){
      sessionStorage.setItem(key,'seen');
      setTimeout(()=>{if(!message.textContent)show('New · Explore our engineering expertise and product downloads.',5200);},650);
    }
  }catch{/* Status actions still work when browser storage is unavailable. */}
})();
