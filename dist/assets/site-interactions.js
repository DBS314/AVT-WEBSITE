(() => {
  const items=[...document.querySelectorAll('.nav-item')];
  const setExpanded=(item,value)=>item.querySelector('.nav-trigger').setAttribute('aria-expanded',String(value));
  items.forEach(item=>{
    item.addEventListener('mouseenter',()=>setExpanded(item,true));
    item.addEventListener('mouseleave',()=>{if(!item.contains(document.activeElement))setExpanded(item,false)});
    item.addEventListener('focusin',()=>setExpanded(item,true));
    item.addEventListener('focusout',event=>{if(!item.contains(event.relatedTarget))setExpanded(item,false)});
    item.addEventListener('keydown',event=>{if(event.key==='Escape'){item.querySelector('.nav-trigger').blur();setExpanded(item,false)}});
  });

  const slides=[...document.querySelectorAll('.banner-slide')];
  if(!slides.length)return;
  const dots=[...document.querySelectorAll('[data-slide-to]')];
  let index=0,paused=matchMedia('(prefers-reduced-motion: reduce)').matches,timer;
  const pause=document.querySelector('.banner-pause');
  function show(next){
    index=(next+slides.length)%slides.length;
    const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
    slides.forEach((slide,i)=>{
      const active=i===index;
      slide.setAttribute('aria-hidden',String(!active));
      slide.inert=!active;
      if(active){
        slide.hidden=false;
        requestAnimationFrame(()=>requestAnimationFrame(()=>slide.classList.add('is-active')));
      }else{
        slide.classList.remove('is-active');
        setTimeout(()=>{if(!slide.classList.contains('is-active'))slide.hidden=true;},reduced?0:720);
      }
    });
    dots.forEach((dot,i)=>dot.setAttribute('aria-pressed',String(i===index)));
  }
  function run(){clearInterval(timer);if(!paused&&!document.hidden)timer=setInterval(()=>{const banner=document.querySelector('.epiq-banner');if(!banner.matches(':hover')&&!banner.contains(document.activeElement))show(index+1)},9500);}
  document.querySelector('.banner-next').addEventListener('click',()=>{show(index+1);run()});
  document.querySelector('.banner-prev').addEventListener('click',()=>{show(index-1);run()});
  dots.forEach(dot=>dot.addEventListener('click',()=>{show(Number(dot.dataset.slideTo));run()}));
  function pauseLabel(){pause.textContent=paused?'▶':'II';pause.setAttribute('aria-label',paused?'Play slideshow':'Pause slideshow');}
  pause.addEventListener('click',()=>{paused=!paused;pauseLabel();run()});
  document.addEventListener('visibilitychange',run);

  const banner=document.querySelector('.epiq-banner');
  let touchX=null,touchY=null;
  banner?.addEventListener('touchstart',e=>{
    if(e.touches.length===1){touchX=e.touches[0].clientX;touchY=e.touches[0].clientY;}
  },{passive:true});
  banner?.addEventListener('touchend',e=>{
    if(touchX===null||e.changedTouches.length!==1)return;
    const dx=e.changedTouches[0].clientX-touchX;
    const dy=e.changedTouches[0].clientY-touchY;
    touchX=touchY=null;
    if(Math.abs(dx)>40&&Math.abs(dx)>Math.abs(dy)){show(dx<0?index+1:index-1);run();}
  },{passive:true});

  pauseLabel();run();
})();
