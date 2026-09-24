// ===============================
// まず centerIndex を宣言
// ===============================
let centerIndex = 0;

// ===============================
// URL に応じて centerIndex を設定
// ===============================
const currentPath = window.location.pathname;

// 項目1（/n_home/）
if (currentPath === "/n_home/") {
    centerIndex = 0;
}

// 項目2（/tryhome/）
if (currentPath === "/tryhome/") {
    centerIndex = 1;
}

// ===============================
// メニュー項目
// ===============================
const menuData = [
    { title: "項目１", description: "ホーム画面です。", icon: "🏠", className: "menu-home", url: "/n_home/" },
    { title: "項目２", description: "ユーザー情報です。", icon: "👤", className: "menu-user", url: "/tryhome/" },
    { title: "項目３", description: "一覧画面です。", icon: "📋", className: "menu-list", url: "//" },
    { title: "項目４", description: "フォルダーです。", icon: "📁", className: "menu-folder", url: "//" },
    { title: "項目５", description: "設定画面です。", icon: "⚙", className: "menu-setting", url: "//" },
    { title: "項目６", description: "項目６です。", icon: "📧", className: "", url: "//" },
    { title: "項目７", description: "項目７です。", icon: "💬", className: "", url: "/friend_home/" },
    { title: "項目８", description: "項目８です。", icon: "📅", className: "", url: "//" },
    { title: "項目９", description: "項目９です。", icon: "📰", className: "", url: "//" },
  

  
];

// ===============================
// 取得
// ===============================
const circle = document.getElementById("circle");
const title = document.getElementById("title");
const contentText = document.querySelector(".content p");

// ===============================
// 描画
// ===============================
function render() {

    circle.innerHTML = "";

    const frameCount = 5;
    const normalHeight = 78;
    const activeHeight = 110;
    const gap = 20;

    let top = 60;

    for (let i = 0; i < frameCount; i++) {

        const index = (centerIndex + i) % menuData.length;
        const item = menuData[index];

        const card = document.createElement("div");
        card.className = "item";

        card.style.left = "40px";
        card.style.top = top + "px";

        card.innerHTML = `
            <div class="icon">${item.icon}</div>
            <div class="text">
                <h3>${item.title}</h3>
                <p>${item.description}</p>
            </div>
            <span>➜</span>
        `;

        // ==========================
        // クリック処理
        // ==========================
        card.onclick = () => {

            // 中央以外なら中央へ移動
            if (i !== 2) {

                centerIndex =
                    (index - 2 + menuData.length) %
                    menuData.length;

                render();

            }

            // 中央ならページ遷移
            else {

                if (
                    item.url &&
                    item.url !== "//"
                ) {
                    window.location.href = item.url;
                }

            }

        };

        // ==========================
        // 中央カード
        // ==========================
        if (i === 2) {

            card.classList.add("active");

            if (item.className) {
                card.classList.add(item.className);
            }

            title.textContent = item.title;
            contentText.textContent = item.description;

            top += activeHeight + gap;

        } else {

            top += normalHeight + gap;

        }

        circle.appendChild(card);

    }
}

// ===============================
// スクロール
// ===============================
document
.querySelector(".nav-wrapper")
.addEventListener("wheel", (e) => {

    e.preventDefault();

    if (e.deltaY > 0) {

        centerIndex =
            (centerIndex + 1) %
            menuData.length;

    } else {

        centerIndex =
            (centerIndex - 1 + menuData.length) %
            menuData.length;

    }

    render();

}, { passive: false });

// ===============================
// キーボード操作
// ===============================
document.addEventListener("keydown", (e) => {

    if (e.key === "ArrowDown") {

        centerIndex =
            (centerIndex + 1) %
            menuData.length;

        render();

    }

    if (e.key === "ArrowUp") {

        centerIndex =
            (centerIndex - 1 + menuData.length) %
            menuData.length;

        render();

    }

});

// ===============================
// メニュー開閉
// ===============================
const menuBtn = document.getElementById("menuToggle");
const nav = document.getElementById("navWrapper");
const content = document.querySelector(".content");

menuBtn.onclick = () => {

    nav.classList.toggle("hide");

    if (nav.classList.contains("hide")) {

        menuBtn.innerHTML = "▶";

        content.style.marginLeft = "0";
        content.style.paddingLeft = "20px";

    } else {

        menuBtn.innerHTML = "☰";

        content.style.marginLeft = "360px";
        content.style.paddingLeft = "50px";

    }

};

// ===============================
// 初期表示
// ===============================
render();