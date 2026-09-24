document.addEventListener("DOMContentLoaded", () => {
    initMenu();
});

function initMenu() {
    const navWrapper = document.querySelector(".nav-wrapper");
    if (!navWrapper) {
        console.warn("nav-wrapper が存在しないため initMenu をスキップ");
        return;
    }

    let centerIndex = 0;

    // ★ 前回選択した項目を localStorage から読み込む
    const savedIndex = localStorage.getItem("centerIndex");
    if (savedIndex !== null) {
        centerIndex = parseInt(savedIndex, 10);
    }

    const menuData = [
   
        { title: "項目１", icon: "🏠", className: "menu-home", url: "/n_home/" },
        { title: "項目２", icon: "👤", className: "menu-user", url: "//" },
        { title: "項目３", icon: "📋", className: "menu-list", url: "/report/" },
        { title: "項目４", icon: "📁", className: "menu-folder", url: "/file_manager/" },
        { title: "項目５", icon: "⚙", className: "menu-setting", url: "//" },
        { title: "項目６", icon: "📧", className: "", url: "/meil_ALL/" },
        { title: "項目７", icon: "💬", className: "", url: "/friend_home/" },
        { title: "項目８", icon: "📅", className: "", url: "/calendar/" },
        { title: "項目９", icon: "▶️", className: "", url: "//" },

  
    ];

    const circle = document.getElementById("circle");
    const title = document.getElementById("title");
    const hasTitle = !!title;

    if (!circle) {
        console.warn("circle が存在しないため initMenu をスキップ");
        return;
    }

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
                <div class="text"><h3>${item.title || ""}</h3></div>
                <span>➜</span>
            `;

            card.onclick = () => {
                if (i !== 2) {
                    centerIndex = (index - 2 + menuData.length) % menuData.length;
                    render();
                } else {
                    if (item.url && item.url !== "//") {
                        // ★ 押した項目を保存
                        localStorage.setItem("centerIndex", centerIndex);
                        window.location.href = item.url;
                    }
                }
            };

            if (i === 2) {
                card.classList.add("active");
                if (item.className) card.classList.add(item.className);
                if (hasTitle) title.textContent = item.title || "";
                top += activeHeight + gap;
            } else {
                top += normalHeight + gap;
            }

            circle.appendChild(card);
        }
    }

    // スクロール操作
    navWrapper.addEventListener("wheel", (e) => {
        e.preventDefault();
        centerIndex = e.deltaY > 0
            ? (centerIndex + 1) % menuData.length
            : (centerIndex - 1 + menuData.length) % menuData.length;
        render();
    }, { passive: false });

    // キーボード操作
    document.addEventListener("keydown", (e) => {
        if (e.key === "ArrowDown") {
            centerIndex = (centerIndex + 1) % menuData.length;
            render();
        }
        if (e.key === "ArrowUp") {
            centerIndex = (centerIndex - 1 + menuData.length) % menuData.length;
            render();
        }
    });

    // メニュー開閉
    const menuBtn = document.getElementById("menuToggle");
    const nav = document.getElementById("navWrapper");
    if (menuBtn && nav) {
        const closeMenu = () => {
            nav.classList.remove("show");
            menuBtn.innerHTML = "☰";
        };

        menuBtn.onclick = () => {
            nav.classList.toggle("show");
            menuBtn.innerHTML = nav.classList.contains("show") ? "▶" : "☰";
        };

        document.addEventListener("click", (e) => {
            if (!nav.classList.contains("show")) return;
            if (nav.contains(e.target) || menuBtn.contains(e.target)) return;
            closeMenu();
        });
    }

    render();
}
