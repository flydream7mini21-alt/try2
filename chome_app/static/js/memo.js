// ============================
// ✅ 初期読み込み
// ============================
let editingIndex = null;

window.addEventListener("load", () => {

  const memo = document.getElementById("memo");
  

  // ✅ 入力欄初期
  memo.style.backgroundColor = "#ffffff";
  memo.style.color = "#000000";
  memo.style.textAlign = "left";

  setupFilters();
  showMemos();

  // ============================
  // ✅ Ctrl + V 画像貼り付け
  // ============================
  memo.addEventListener("paste", function(e){

    const items = e.clipboardData.items;

    for(let i = 0; i < items.length; i++){

      if(items[i].type.indexOf("image") !== -1){

        const file = items[i].getAsFile();
        const reader = new FileReader();

        reader.onload = function(evt){

  const wrapper = document.createElement("div");

  wrapper.style.float = "left";
  wrapper.style.margin = "5px";

  // ✅ サイズ変更可能（超重要）
  wrapper.style.resize = "both";
  wrapper.style.overflow = "auto";
  wrapper.style.display = "inline-block";

  // ✅ 編集禁止
  wrapper.contentEditable = false;

  const img = document.createElement("img");
  img.src = evt.target.result;

  // ✅ 親に合わせる
  img.style.width = "30%";

  wrapper.appendChild(img);

  memo.appendChild(wrapper);

  // ✅ 改行
  const clear = document.createElement("div");
  clear.style.clear = "both";
  memo.appendChild(clear);

  // ✅ ダブルクリック削除
  img.ondblclick = () => wrapper.remove();
};

        reader.readAsDataURL(file);

        e.preventDefault();
      }
    }
  });

});


// ============================
// ✅ 保存（背景込み）
// ============================
function saveMemo(){

  const memoEl = document.getElementById("memo");

  let text = memoEl.innerHTML.trim();

  // ✅ 先頭の空行削除（正しい書き方）
  text = text.replace(/^(<div><br><\/div>)+/, "");

  // ✅ 末尾の空行削除
  text = text.replace(/(<div><br><\/div>|<br>)+$/, "");

  if(!text) return;

  const now = new Date();
  const date = now.getFullYear() + "/" +
               (now.getMonth()+1) + "/" +
               now.getDate() + " " +
               now.getHours() + ":" +
               now.getMinutes();

  let memos = JSON.parse(localStorage.getItem("memos")) || [];

  const bgColor = memoEl.style.backgroundColor || "#ffffff";

  if(editingIndex !== null){
    memos[editingIndex] = { text, date, bgColor };
    editingIndex = null;
  }else{
    memos.unshift({ text, date, bgColor });
  }

  localStorage.setItem("memos", JSON.stringify(memos));

  memoEl.innerHTML = "";
  memoEl.style.backgroundColor = "#ffffff";

  showMemos();

  alert("保存しました！");
}


// ============================
// ✅ 一覧表示
// ============================
function showMemos(){

  const list = document.getElementById("memoList");
  const memos = JSON.parse(localStorage.getItem("memos")) || [];

  const year = document.getElementById("yearFilter")?.value;
  const month = document.getElementById("monthFilter")?.value;
  const day = document.getElementById("dayFilter")?.value;

  list.innerHTML = "";

  memos.forEach((memo, index) => {

    const [y, m, d] = memo.date.split(" ")[0].split("/");

    // ✅ フィルター
    if(
      (year && parseInt(year) !== parseInt(y)) ||
      (month && parseInt(month) !== parseInt(m)) ||
      (day && parseInt(day) !== parseInt(d))
    ){
      return;
    }

    // ✅ 画像壊さない
    let text = memo.text;


const temp = document.createElement("div");
temp.innerHTML = text;

// ✅ テキストだけ処理
temp.childNodes.forEach(node => {

  if(node.nodeType === 3){ // テキストのみ

    const replaced = node.nodeValue.replace(
      /(https?:\/\/[^\s<]+)/g,
      '<a href="$1" target="_blank">$1</a>'
    );

    const span = document.createElement("span");
    span.innerHTML = replaced;

    node.replaceWith(span);
  }

});

text = temp.innerHTML;


    list.innerHTML += `
      <div style="
        background:#f5f5f5;
        border:1px solid #aaa;
        padding:10px;
        margin:10px 0;
        border-radius:8px;
      ">

        <div style="color:gray; font-size:12px;">
          ${memo.date}
        </div>

        <div style="
          background:${memo.bgColor || "#ffffff"};
          padding:8px;
          margin:5px 0;
          white-space:pre-wrap;
          border-radius:5px;
          line-height:1.6;
        ">
          ${text}
        </div>

        <div>
          <button onclick="editMemo(${index})">更新</button>
          <button onclick="deleteMemo(${index})">削除</button>
        </div>

      </div>
    `;
  });
}
// ============================
// ✅ 編集
// ============================
function editMemo(index){

  let memos = JSON.parse(localStorage.getItem("memos")) || [];

  const memoBox = document.getElementById("memo");

  memoBox.innerHTML = memos[index].text;
  memoBox.style.backgroundColor = memos[index].bgColor || "#ffffff";

  editingIndex = index;

  memoBox.focus();
}


// ============================
// ✅ 削除
// ============================
function deleteMemo(index){

  let memos = JSON.parse(localStorage.getItem("memos")) || [];

  memos.splice(index, 1);

  localStorage.setItem("memos", JSON.stringify(memos));

  showMemos();
}


// ============================
// ✅ 全削除
// ============================
function clearMemo(){

  if(confirm("全部削除する？")){
    localStorage.removeItem("memos");
    document.getElementById("memo").innerHTML = "";
    showMemos();
  }
}


// ============================
// ✅ リセット
// ============================
function resetMemo(){

  const memo = document.getElementById("memo");

  memo.innerHTML = "";
  memo.style.backgroundColor = "#ffffff";
  memo.style.color = "#000000";
  memo.style.textAlign = "left";

  memo.focus();
}


// ============================
// ✅ 色
// ============================
function applyColor(color){

  const mode = document.getElementById("mode").value;

  if(mode === "text"){
    document.execCommand("foreColor", false, color);
  }

  if(mode === "highlight"){
    document.execCommand("hiliteColor", false, color);
  }

  if(mode === "memo"){
    document.getElementById("memo").style.backgroundColor = color;
  }
}


// ============================
// ✅ サイズ
// ============================
function changeSize(size){

  const sizes = {
    1:"10px",2:"12px",3:"14px",
    4:"16px",5:"20px",6:"26px",7:"32px"
  };

  const selection = window.getSelection();
  if(!selection.rangeCount) return;

  const range = selection.getRangeAt(0);

  const span = document.createElement("span");
  span.style.fontSize = sizes[size] || "16px";

  span.appendChild(range.extractContents());
  range.insertNode(span);
}


// ============================
// ✅ 位置
// ============================
function changeAlign(align){
  document.execCommand(
    "justify" + align.charAt(0).toUpperCase() + align.slice(1)
  );
}


// ============================
// ✅ フィルター
// ============================
function setupFilters(){

  const memos = JSON.parse(localStorage.getItem("memos")) || [];

  const years = new Set();
  const months = new Set();
  const days = new Set();

  memos.forEach(memo=>{
    const [y,m,d] = memo.date.split(" ")[0].split("/");
    years.add(y);
    months.add(m);
    days.add(d);
  });

  const ySel = document.getElementById("yearFilter");
  const mSel = document.getElementById("monthFilter");
  const dSel = document.getElementById("dayFilter");

  years.forEach(y=>{
    ySel.innerHTML += `<option value="${y}">${y}年</option>`;
  });

  months.forEach(m=>{
    mSel.innerHTML += `<option value="${m}">${m}月</option>`;
  });

  days.forEach(d=>{
    dSel.innerHTML += `<option value="${d}">${d}日</option>`;
  });
}


window.addEventListener("scroll", () => {
  const btn = document.getElementById("topBtn");

  if(window.scrollY > 200){
    btn.style.display = "block";
  } else {
    btn.style.display = "none";
  }
});



function scrollToTop(){
  window.scrollTo({
    top: 0,
    behavior: "smooth"
  });
}
