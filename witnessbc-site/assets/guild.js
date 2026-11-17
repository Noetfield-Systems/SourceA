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

  /* Attach an anonymous correlation ID to the existing Witness merchant Payment
     Link. This is not a purchase signal; Stripe must independently confirm money. */
  document.querySelectorAll('[data-guild-checkout]').forEach(function(link){
    try{
      var destination=new URL(link.href);
      if(destination.hostname!=='buy.stripe.com')return;
      var reference=sessionStorage.getItem('witness_guild_checkout_ref');
      if(!reference){
        reference='wbc_guild_'+crypto.randomUUID().replace(/-/g,'').slice(0,24);
        sessionStorage.setItem('witness_guild_checkout_ref',reference);
      }
      destination.searchParams.set('client_reference_id',reference);
      destination.searchParams.set('utm_source','witnessbc');
      destination.searchParams.set('utm_medium','guild');
      destination.searchParams.set('utm_campaign','season-zero');
      link.href=destination.toString();
    }catch(_){/* Keep original merchant link valid even with storage disabled. */}
  });
})();