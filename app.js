const initialBoards = [{id:'product',name:'Product launch',color:'',description:'A little progress each day adds up to big results.',lists:[
  {id:'ideas',name:'Ideas',cards:[{id:'c1',title:'Research competitor products',description:'Collect examples of onboarding and pricing pages.',label:'pink',comments:3,checklist:'2/4',assignee:'MK',due:''},{id:'c2',title:'Define our product vision',description:'Align on the story we want to tell.',label:'',comments:0,checklist:'',assignee:'JD',due:''},{id:'c3',title:'Create moodboard',description:'Gather visual references for the launch.',label:'mint',comments:2,checklist:'',assignee:'AL',due:''}]},
  {id:'todo',name:'To do',cards:[{id:'c4',title:'Write launch announcement',description:'Draft copy for the website and newsletter.',label:'peach',comments:4,checklist:'1/3',assignee:'JD',due:''},{id:'c5',title:'Design landing page',description:'Keep it focused, clear, and easy to scan.',label:'mint',comments:1,checklist:'3/5',assignee:'MK',due:''},{id:'c6',title:'Set up analytics',description:'',label:'blue',comments:0,checklist:'',assignee:'AL',due:''}]},
  {id:'progress',name:'In progress',cards:[{id:'c7',title:'Build signup flow',description:'',label:'blue',comments:2,checklist:'4/6',assignee:'MK',due:''},{id:'c8',title:'Prepare launch email',description:'',label:'peach',comments:0,checklist:'',assignee:'JD',due:''}]},
  {id:'done',name:'Done',cards:[{id:'c9',title:'Choose a launch date',description:'',label:'',comments:0,checklist:'',assignee:'AL',due:''},{id:'c10',title:'Kickoff with the team',description:'',label:'',comments:1,checklist:'',assignee:'JD',due:''}]}
]}];
const storageKey='flowboard-v1';
let boards=readBoards(), activeBoardId=boards[0]?.id;
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
function readBoards(){try{const saved=JSON.parse(localStorage.getItem(storageKey));if(Array.isArray(saved)&&saved.length)return saved;}catch{}return structuredClone(initialBoards)}
function persist(){localStorage.setItem(storageKey,JSON.stringify(boards));const bu=$('#boardUpdated');if(bu)bu.textContent='All changes saved'}
function board(){return boards.find(b=>b.id===activeBoardId)||boards[0]}
function safe(value){return String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function render(){renderNav();renderBoard()}
function renderNav(){const nav=$('#boardNav');nav.innerHTML=boards.map(b=>`<button class="board-nav-item ${b.id===activeBoardId?'active':''}" data-board="${safe(b.id)}"><span class="board-color ${safe(b.color)}"></span>${safe(b.name)}</button>`).join('');nav.querySelectorAll('[data-board]').forEach(el=>el.onclick=()=>{activeBoardId=el.dataset.board;render()})}
function renderBoard(){const b=board();if(!b)return;$('#boardTitle').textContent=b.name;$('#crumbBoard').textContent=b.name;$('#boardDescription').textContent=b.description||'Keep your team moving forward.';const canvas=$('#boardCanvas');canvas.innerHTML=b.lists.map(list=>`<section class="list-column" data-list="${safe(list.id)}"><header class="list-header"><span class="list-color"></span><span class="list-title">${safe(list.name)}</span><span class="list-count">${list.cards.length}</span><button class="icon-button list-menu" data-list-menu="${safe(list.id)}" aria-label="List options">···</button></header><div class="card-stack">${list.cards.map(cardMarkup).join('')}</div><button class="add-card" data-add-card="${safe(list.id)}"><span>＋</span> Add a card</button></section>`).join('')+`<button class="add-list" id="addListCanvas">＋ Add another list</button>`;
  canvas.querySelectorAll('[data-add-card]').forEach(btn=>btn.onclick=()=>openCard(null,btn.dataset.addCard));canvas.querySelectorAll('[data-card]').forEach(el=>{el.onclick=()=>openCard(el.dataset.card,el.dataset.list);el.addEventListener('dragstart',e=>{e.dataTransfer.setData('text/plain',JSON.stringify({card:el.dataset.card,from:el.dataset.list}));e.dataTransfer.effectAllowed='move';setTimeout(()=>el.classList.add('dragging'),0)});el.addEventListener('dragend',()=>el.classList.remove('dragging'))});
  canvas.querySelectorAll('.list-column').forEach(col=>{col.addEventListener('dragover',e=>{e.preventDefault();col.classList.add('drop-target')});col.addEventListener('dragleave',e=>{if(!col.contains(e.relatedTarget))col.classList.remove('drop-target')});col.addEventListener('drop',e=>{e.preventDefault();col.classList.remove('drop-target');try{const data=JSON.parse(e.dataTransfer.getData('text/plain'));moveCard(data.card,data.from,col.dataset.list)}catch{}})});
  canvas.querySelectorAll('[data-list-menu]').forEach(btn=>btn.onclick=()=>{const l=b.lists.find(x=>x.id===btn.dataset.listMenu);const name=prompt('Rename this list',l.name);if(name?.trim()){l.name=name.trim();persist();renderBoard()}});$('#addListCanvas').onclick=()=>$('#listDialog').showModal();applySearch();
}
function cardMarkup(c){const labelName={mint:'Design',blue:'Development',peach:'Marketing',pink:'Research'}[c.label];const due=c.due?new Date(`${c.due}T00:00:00`):null;const today=new Date();today.setHours(0,0,0,0);let dueClass='',dueText='';if(due){const days=Math.ceil((due-today)/86400000);dueClass=days<0?'overdue':days<=2?'soon':'';dueText=due.toLocaleDateString(undefined,{month:'short',day:'numeric'})}
return `<article class="task-card" draggable="true" data-card="${safe(c.id)}" data-list="${safe(c._listId||'')}">${labelName?`<div class="task-label ${safe(c.label)}" title="${labelName}"></div>`:''}<h3 class="task-title">${safe(c.title)}</h3>${c.description?`<p class="task-desc">${safe(c.description)}</p>`:''}<footer class="card-footer"><div class="card-signals">${c.comments?`<span class="card-signal" title="Comments">▤ ${c.comments}</span>`:''}${c.checklist?`<span class="card-signal" title="Checklist">☑ ${safe(c.checklist)}</span>`:''}${due?`<span class="due-pill ${dueClass}">◷ ${dueText}</span>`:''}</div>${c.assignee?`<span class="card-assignee ${c.assignee==='AL'?'green':c.assignee==='JD'?'pink':''}" title="${safe(c.assignee)}">${safe(c.assignee)}</span>`:''}</footer></article>`}
function fixListIds(){for(const l of board()?.lists||[])for(const c of l.cards)c._listId=l.id}
function openCard(id,listId){const dialog=$('#cardDialog'),c=id?board().lists.flatMap(l=>l.cards).find(x=>x.id===id):null;$('#cardId').value=c?.id||'';$('#cardListId').value=listId;$('#cardName').value=c?.title||'';$('#cardDescription').value=c?.description||'';$('#cardLabel').value=c?.label||'';$('#cardDue').value=c?.due||'';$('#deleteCard').style.visibility=c?'visible':'hidden';$('#saveCard').textContent=c?'Save changes':'Add card';dialog.showModal();$('#cardName').focus()}
$('#cardForm').addEventListener('submit',e=>{e.preventDefault();const id=$('#cardId').value,listId=$('#cardListId').value,title=$('#cardName').value.trim();if(!title)return;const l=board().lists.find(x=>x.id===listId);if(!l)return;const c={title,description:$('#cardDescription').value.trim(),label:$('#cardLabel').value,due:$('#cardDue').value,comments:0,checklist:'',assignee:'JD'};if(id){const source=board().lists.find(x=>x.cards.some(y=>y.id===id));const existing=source.cards.find(y=>y.id===id);Object.assign(existing,c)}else{c.id='c'+Date.now();l.cards.push(c)}$('#cardDialog').close();persist();renderBoard()});
$('#deleteCard').onclick=()=>{const id=$('#cardId').value;if(!id)return;for(const l of board().lists)l.cards=l.cards.filter(c=>c.id!==id);$('#cardDialog').close();persist();renderBoard();toast('Card deleted')};
$('#listForm').addEventListener('submit',e=>{e.preventDefault();const name=$('#listName').value.trim();if(!name)return;board().lists.push({id:'l'+Date.now(),name,cards:[]});$('#listDialog').close();$('#listName').value='';persist();renderBoard()});
$('#boardForm').addEventListener('submit',e=>{e.preventDefault();const name=$('#newBoardName').value.trim();if(!name)return;const b={id:'b'+Date.now(),name,color:['blue','peach','lilac'][boards.length%3],description:'',lists:[{id:'ideas',name:'To do',cards:[]},{id:'progress',name:'In progress',cards:[]},{id:'done',name:'Done',cards:[]}]};boards.push(b);activeBoardId=b.id;$('#boardDialog').close();$('#newBoardName').value='';persist();render()});
function moveCard(cardId,fromId,toId){if(fromId===toId)return;const b=board(),from=b.lists.find(l=>l.id===fromId),to=b.lists.find(l=>l.id===toId),index=from?.cards.findIndex(c=>c.id===cardId);if(!from||!to||index<0)return;to.cards.push(from.cards.splice(index,1)[0]);persist();renderBoard()}
function applySearch(){const q=$('#searchInput').value.trim().toLowerCase();$$('.task-card').forEach(card=>card.hidden=q&&!card.textContent.toLowerCase().includes(q))}
$('#searchInput').addEventListener('input',applySearch);$('#addBoard').onclick=()=>$('#boardDialog').showModal();$('#boardMenu').onclick=()=>{const b=board();if(!b)return;const answer=prompt('Enter a new name for this board, or type DELETE to remove it.',b.name);if(!answer)return;if(answer.trim().toUpperCase()==='DELETE'){if(boards.length<2){toast('Keep at least one board');return}boards=boards.filter(x=>x.id!==b.id);activeBoardId=boards[0].id;persist();render()}else{b.name=answer.trim();persist();render()}};
$('.star-button').onclick=e=>{e.currentTarget.classList.toggle('is-favorite');e.currentTarget.textContent=e.currentTarget.classList.contains('is-favorite')?'★':'☆'};
$('#filterButton').onclick=()=>{const q=prompt('Show cards with a title containing:');if(q===null)return;$('#searchInput').value=q;applySearch()};$('#mobileMenu').onclick=()=>$('#sidebar').classList.toggle('open');$('#upgradeButton').onclick=()=>toast('Plan options are coming soon');$('#addWorkspace').onclick=()=>toast('Workspace settings are coming soon');$('.member-add').onclick=()=>toast('Invite link copied');
$$('.tab').forEach(t=>t.onclick=()=>{ $$('.tab').forEach(x=>x.classList.remove('active'));t.classList.add('active');if(t.textContent.includes('Table')||t.textContent.includes('Calendar'))toast(`${t.textContent.trim()} view is coming soon`)});
$$('.close-modal').forEach(b=>b.onclick=()=>b.closest('dialog')?.close());
function toast(message){const el=$('#toast');el.textContent=message;el.classList.add('visible');clearTimeout(toast.timer);toast.timer=setTimeout(()=>el.classList.remove('visible'),2200)}
document.addEventListener('keydown',e=>{if((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==='k'){e.preventDefault();$('#searchInput').focus()}if(e.key==='Escape')$('#sidebar').classList.remove('open')});
// The stored data stays free of presentation-only list references.
function renderSafe(){fixListIds();render()}
const originalRenderBoard=renderBoard;renderBoard=()=>{fixListIds();originalRenderBoard()};
// Add position-aware drag and drop after each board render. This supports
// reordering in a list as well as moving cards between lists.
let draggedCardId=null;
let draggedFromListId=null;
let suppressCardClickUntil=0;
const basicRenderBoard=renderBoard;
renderBoard=()=>{
  basicRenderBoard();
  const canvas=$('#boardCanvas');
  canvas.querySelectorAll('.task-card').forEach(card=>{
    card.addEventListener('dragstart',event=>{
      draggedCardId=card.dataset.card;
      draggedFromListId=card.dataset.list;
      suppressCardClickUntil=Date.now()+500;
      event.dataTransfer.setData('text/plain',JSON.stringify({card:draggedCardId,from:draggedFromListId}));
      event.dataTransfer.effectAllowed='move';
      requestAnimationFrame(()=>card.classList.add('dragging'));
    });
    card.addEventListener('click',event=>{
      if(Date.now()<suppressCardClickUntil){event.preventDefault();event.stopImmediatePropagation();}
    },true);
  });
  canvas.querySelectorAll('.list-column').forEach(column=>{
    column.addEventListener('dragover',event=>{
      event.preventDefault();
      event.dataTransfer.dropEffect='move';
      column.classList.add('drop-target');
      const stack=column.querySelector('.card-stack');
      const moving=canvas.querySelector('.task-card.dragging');
      if(!stack||!moving)return;
      const after=getCardAfterPointer(stack,event.clientY);
      if(after)stack.insertBefore(moving,after);else stack.appendChild(moving);
    });
    column.addEventListener('dragleave',event=>{
      if(!column.contains(event.relatedTarget))column.classList.remove('drop-target');
    });
    column.addEventListener('drop',event=>{
      event.preventDefault();event.stopPropagation();column.classList.remove('drop-target');
      let payload={card:draggedCardId,from:draggedFromListId};
      try{payload=JSON.parse(event.dataTransfer.getData('text/plain'))||payload;}catch{}
      if(payload.card)moveCardToPosition(payload.card,payload.from,column.dataset.list,cardIndexAtPointer(column.querySelector('.card-stack'),event.clientY));
      draggedCardId=null;draggedFromListId=null;
    });
  });
};
function getCardAfterPointer(stack,y){
  return [...stack.querySelectorAll('.task-card:not(.dragging)')].reduce((closest,card)=>{
    const rect=card.getBoundingClientRect(),offset=y-(rect.top+rect.height/2);
    return offset<0&&offset>closest.offset?{offset,element:card}:closest;
  },{offset:Number.NEGATIVE_INFINITY,element:null}).element;
}
function cardIndexAtPointer(stack,y){
  if(!stack)return 0;
  const cards=[...stack.querySelectorAll('.task-card:not(.dragging)')];
  const after=getCardAfterPointer(stack,y);
  return after?cards.indexOf(after):cards.length;
}
function moveCardToPosition(cardId,fromId,toId,index){
  const b=board(),from=b.lists.find(list=>list.id===fromId),to=b.lists.find(list=>list.id===toId);
  if(!from||!to)return;
  const oldIndex=from.cards.findIndex(card=>card.id===cardId);
  if(oldIndex<0)return;
  const [card]=from.cards.splice(oldIndex,1);
  // `index` is measured against the visible cards with the dragged card
  // excluded, so it already matches the destination array after removal.
  const targetIndex=index;
  to.cards.splice(Math.max(0,Math.min(targetIndex,to.cards.length)),0,card);
  persist();renderBoard();
}
renderSafe();
