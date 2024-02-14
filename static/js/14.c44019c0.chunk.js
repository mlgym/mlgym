!function(){"use strict";var e={14:function(e,t,n){var r=n(1753),o=n(5987),s=n(7762),c=n(4942),i=n(1413),a=n(3433),u=Object.freeze({JOB_STATUS:"job_status",JOB_SCHEDULED:"job_scheduled",EVALUATION_RESULT:"evaluation_result",EXPERIMENT_CONFIG:"experiment_config",EXPERIMENT_STATUS:"experiment_status",UNKNOWN_EVENT:"Unknown event type. No event handler for such event type."});var f=["grid_search_id","status","splits"];var l=["grid_search_id","status"];var d,p=["headers","chartsUpdates"],_={},h=(d={},(0,c.Z)(d,u.JOB_STATUS,(function(e,t){v(function(e){var t=e,n=(t.grid_search_id,t.status),r=(0,o.Z)(t,l);return(0,i.Z)({job_status:n},r)}(e),t,u.JOB_STATUS)})),(0,c.Z)(d,u.JOB_SCHEDULED,(function(e,t){return console.log("Job scheduled found")})),(0,c.Z)(d,u.EVALUATION_RESULT,(function(e,t){var n,r=function(e){var t,n=e,r=n.experiment_id,o=n.epoch,c=n.metric_scores,i=n.loss_scores,a=[],u={},f=(0,s.Z)(c);try{for(f.s();!(t=f.n()).done;){var l=t.value;u[l.split+"_"+l.metric]=l.score,a.push({chart_id:l.split+"_"+l.metric,exp_id:r,epoch:o,score:l.score})}}catch(h){f.e(h)}finally{f.f()}var d,p=(0,s.Z)(i);try{for(p.s();!(d=p.n()).done;){var _=d.value;u[_.split+"_"+_.loss]=_.score,a.push({chart_id:_.split+"_"+_.loss,exp_id:r,epoch:o,score:_.score})}}catch(h){p.e(h)}finally{p.f()}return{experiment_id:r,charts_updates:a,table_scores:u}}(e),o=r.experiment_id,c=r.charts_updates,u=r.table_scores;(n=t.chartsUpdates).push.apply(n,(0,a.Z)(c)),v((0,i.Z)({experiment_id:o},u),t)})),(0,c.Z)(d,u.EXPERIMENT_CONFIG,(function(e,t){return console.log("Exp config found")})),(0,c.Z)(d,u.EXPERIMENT_STATUS,(function(e,t){v(function(e){var t=e,n=(t.grid_search_id,t.status),r=t.splits,s=(0,o.Z)(t,f);return(0,i.Z)({model_status:n,splits:r.join(),epoch_progress:s.current_epoch/s.num_epochs,batch_progress:s.current_batch/s.num_batches},s)}(e),t,u.EXPERIMENT_STATUS)})),d);function v(e,t){var n,r,o=arguments.length>2&&void 0!==arguments[2]?arguments[2]:"";Object.assign(null!==(r=t[n=e.experiment_id])&&void 0!==r?r:t[n]=e,e),o&&_[o]||(_[o]=!0,Object.keys(t[e.experiment_id]).forEach(t.headers.add,t.headers))}function g(e,t){var n,r=(0,s.Z)(e);try{for(r.s();!(n=r.n()).done;){var o=n.value,c=o;if("batched_events"!==c.event_id){var i=o.data,a=i.event_type,u=i.payload;h[a](u,t)}else g(c.data,t)}}catch(f){r.e(f)}finally{r.f()}}var m,b,E,S=function(e){var t={headers:new Set,chartsUpdates:[]};g(e,t),postMessage(function(e){var t=e.headers,n=e.chartsUpdates,r=(0,o.Z)(e,p);return{tableHeaders:t.size>0?(0,a.Z)(t):void 0,tableData:Object.values(r),chartsUpdates:n}}(t))},O=function(e){postMessage({status:{ping:e}})},T=function(e,t,n){postMessage({status:{isSocketConnected:e,gridSearchId:t,restApiUrl:n}})},y=function(e){postMessage({status:{throughput:e}})},U=-1,x=-1,j=0,Z=[],I=function(e,t,n){e.emit("join",{rooms:[t]}),b=setInterval(M,1e3,e),T(!0,t,n),E=setInterval((function(){Z.length>0&&w()}),1e3)},N=function(e){return P(e)},k=function(e){return P(e)},C=function(e){Z.push(e),Z.length>=1e3&&w(),j++,postMessage({status:"msg_count_increment"})},A=function(){x=(new Date).getTime(),O(x-U)},M=function(e){(x>U||-1===U)&&(U=(new Date).getTime(),e.emit("ping")),y(j/1),j=0},P=function(e){console.log("".concat(e instanceof Error?"connection":"disconnected"," : ").concat(e)),clearInterval(b),clearInterval(E),Z.length>0&&w(),T(!1),y(0),O(0)},w=function(){S(Z),Z.length=0};onmessage=function(e){var t,n=e.data;"CLOSE_SOCKET"===n?m.close():void 0!==n.gridSearchId&&void 0!==n.socketConnectionUrl?(t=n,console.log("WebSocket initializing..."),(m=(0,r.ZP)(t.socketConnectionUrl,{autoConnect:!0})).on("connect",(function(){return I(m,t.gridSearchId,t.restApiUrl)})),m.on("disconnect",N),m.on("connect_error",k),m.on("mlgym_event",C),m.on("pong",A)):console.log(n)}}},t={};function n(r){var o=t[r];if(void 0!==o)return o.exports;var s=t[r]={exports:{}};return e[r](s,s.exports,n),s.exports}n.m=e,n.x=function(){var e=n.O(void 0,[131],(function(){return n(14)}));return e=n.O(e)},function(){var e=[];n.O=function(t,r,o,s){if(!r){var c=1/0;for(f=0;f<e.length;f++){r=e[f][0],o=e[f][1],s=e[f][2];for(var i=!0,a=0;a<r.length;a++)(!1&s||c>=s)&&Object.keys(n.O).every((function(e){return n.O[e](r[a])}))?r.splice(a--,1):(i=!1,s<c&&(c=s));if(i){e.splice(f--,1);var u=o();void 0!==u&&(t=u)}}return t}s=s||0;for(var f=e.length;f>0&&e[f-1][2]>s;f--)e[f]=e[f-1];e[f]=[r,o,s]}}(),n.d=function(e,t){for(var r in t)n.o(t,r)&&!n.o(e,r)&&Object.defineProperty(e,r,{enumerable:!0,get:t[r]})},n.f={},n.e=function(e){return Promise.all(Object.keys(n.f).reduce((function(t,r){return n.f[r](e,t),t}),[]))},n.u=function(e){return"static/js/"+e+".bc1f8174.chunk.js"},n.miniCssF=function(e){},n.o=function(e,t){return Object.prototype.hasOwnProperty.call(e,t)},n.r=function(e){"undefined"!==typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})},n.p="/mlgym/",function(){var e={14:1};n.f.i=function(t,r){e[t]||importScripts(n.p+n.u(t))};var t=self.webpackChunkfront_end=self.webpackChunkfront_end||[],r=t.push.bind(t);t.push=function(t){var o=t[0],s=t[1],c=t[2];for(var i in s)n.o(s,i)&&(n.m[i]=s[i]);for(c&&c(n);o.length;)e[o.pop()]=1;r(t)}}(),function(){var e=n.x;n.x=function(){return n.e(131).then(e)}}();n.x()}();
//# sourceMappingURL=14.c44019c0.chunk.js.map