/* Witness outbound attribution: append only declared marketing context, never claim a sale. */
(function(){
  'use strict';
  document.querySelectorAll('[data-guild-link]').forEach(function(link){
    try{
      var dest=new URL(link.href);
      if(dest.hostname!=='community-economy-production.up.railway.app')return;
      var source=new URLSearchParams(location.search);
      ['utm_campaign','utm_content'].forEach(function(key){if(source.has(key))dest.searchParams.set(key,source.get(key).slice(0,80));});
      link.href=dest.toString();
    }catch(_){}
  });
})();