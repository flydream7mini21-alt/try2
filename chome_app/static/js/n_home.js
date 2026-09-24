document.addEventListener("DOMContentLoaded", () => {
    initRightNav();
    initPanelSwitch();
    applyColorCircles();
    initSingleColorChange();
    applyTriColorButtons();
    initTriColorChange();
    initPatternChange();
    initPanelAutoClose();
});


// ===============================
// ↻ ボタンで panel‑1 を開く
// ===============================
function initRightNav() {
    const colorBtn = document.getElementById("colorBtn");

    colorBtn.onclick = (e) => {
        e.stopPropagation();

        // ★ 現在 active のボタンを取得（① or ②）
        const activeBtn = document.querySelector(".panel-left-column button.active");
        const num = activeBtn ? activeBtn.dataset.panel : "1";

        // ★ 現在選択中のパネルを開閉する
        const currentPanel = document.getElementById(`colorPanel-${num}`);
        currentPanel.classList.toggle("show");
    };

    // ★ panel1 の閉じるボタン
    const close1 = document.getElementById("closeColorPanel-1");
    close1.onclick = () => {
        document.getElementById("colorPanel-1").classList.remove("show");
    };

    // ★ panel2 の閉じるボタン
    const close2 = document.getElementById("closeColorPanel-2");
    if (close2) {
        close2.onclick = () => {
            document.getElementById("colorPanel-2").classList.remove("show");
        };
    }
}




// ===============================
// ①②で panel 切り替え
// ===============================
function initPanelSwitch() {

    const buttons = document.querySelectorAll(".panel-left-column button");

    buttons.forEach(btn => {
        btn.addEventListener("click", () => {

            const num = btn.dataset.panel;

            // ★ active 切り替え
            buttons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            // ★ 全パネル非表示
            document.querySelectorAll(".color-panel").forEach(panel => {
                panel.style.display = "none";
                panel.classList.remove("show");
            });

            // ★ 対象パネル表示（ここが最重要）
            const target = document.getElementById(`colorPanel-${num}`);
            target.style.display = "flex";
            target.style.flexDirection = "row";

            // ★ パネル切り替え時にも show を付ける（最重要）
            target.classList.add("show");
        });
    });
}









// ===============================
// 単色丸の色反映
// ===============================
function applyColorCircles() {
    document.querySelectorAll(".color-circle").forEach(c => {
        c.style.backgroundColor = c.dataset.color;
    });
}


// ===============================
// 単色背景変更
// ===============================
function initSingleColorChange() {
    document.querySelectorAll(".color-circle").forEach(c => {
        c.addEventListener("click", () => {
            const color = c.dataset.color;
            document.body.style.background = color;
        });
    });
}


// ===============================
// 三色丸の見た目
// ===============================
function applyTriColorButtons() {
    const sets = {
        red: ["#ff6666", "#ff9999", "#ffe5e5"],
        blue: ["#66ccff", "#99ddff", "#e5f7ff"]
    };

    document.querySelectorAll(".tri-color-btn").forEach(btn => {
        const set = sets[btn.dataset.set];
        if (!set) return;

        btn.style.background = `
            linear-gradient(135deg, ${set[0]}, ${set[1]}, ${set[2]})
        `;
    });
}


// ===============================
// 三色背景変更
// ===============================
function initTriColorChange() {
    const sets = {
        red: ["#ff6666", "#ff9999", "#ffe5e5"],
        blue: ["#66ccff", "#99ddff", "#e5f7ff"]
    };

    document.querySelectorAll(".tri-color-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const set = sets[btn.dataset.set];
            if (!set) return;

            document.body.style.background = `
                linear-gradient(135deg, ${set[0]}, ${set[1]}, ${set[2]})
            `;
        });
    });
}


// ===============================
// 画像背景変更
// ===============================
function initPatternChange() {
    document.querySelectorAll(".pattern-circle").forEach(p => {
        const img = p.dataset.img;

        p.style.backgroundImage = `url(${img})`;

        p.addEventListener("click", () => {
            document.body.style.backgroundImage = `url(${img})`;
            document.body.style.backgroundSize = "cover";
            document.body.style.backgroundPosition = "center";
        });
    });
    
}
// ===============================
// パネル綴じ
// ===============================
function initPanelAutoClose() {

    document.addEventListener("click", (e) => {

        const colorBtn = document.getElementById("colorBtn");
        const switchButtons = document.querySelectorAll(".panel-left-column button");
        const panels = document.querySelectorAll(".color-panel");

        panels.forEach(panel => {

            // パネルが開いている時だけ判定
            if (panel.classList.contains("show")) {

                // ★ ①②ボタンを押した場合は閉じない
                let isSwitchButton = false;
                switchButtons.forEach(btn => {
                    if (btn.contains(e.target)) {
                        isSwitchButton = true;
                    }
                });

                if (isSwitchButton) return;  // ← ★ここが最重要

                // ★ パネル外をクリックしたら閉じる
                if (!panel.contains(e.target) && !colorBtn.contains(e.target)) {
                    panel.classList.remove("show");
                }
            }
        });
    });
}
