/* 色選択の丸ボタンに選択枠を付ける */
document.querySelectorAll(".color-label").forEach(label => {
    label.addEventListener("click", () => {
        document.querySelectorAll(".color-option").forEach(opt => opt.classList.remove("selected"));
        label.querySelector(".color-option").classList.add("selected");
    });
});

/* 編集モーダルを開く */
function openEditModal(id, title, date, start, end, color) {
    document.getElementById("edit_title").value = title;
    document.getElementById("edit_date").value = date;
    document.getElementById("edit_start_time").value = start;
    document.getElementById("edit_end_time").value = end;

    document.querySelectorAll(".edit-color-radio").forEach(r => {
        r.checked = (r.value === color);
    });

    document.getElementById("editForm").action = "/group/schedule/update/" + id + "/";

    document.getElementById("editModal").style.display = "flex";
}

function closeEditModal() {
    document.getElementById("editModal").style.display = "none";
}