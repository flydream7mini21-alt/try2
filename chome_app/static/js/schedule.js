//予定追加時の閉じるよう
function toggleDetail(id) {
    const detail = document.getElementById("detail-" + id);
    detail.style.display = (detail.style.display === "block") ? "none" : "block";
}

function openScheduleModal() {
    const modal = document.getElementById("scheduleModal");
    modal.classList.add("show");
    modal.style.display = "flex";
}

function closeScheduleModal() {
    const modal = document.getElementById("scheduleModal");
    modal.classList.remove("show");
    modal.style.display = "none";
}

//更新用
function editSchedule(id, title, date, start, end) {

    // モーダルを開く
    openScheduleModal();

    // フォームに値をセット
    document.querySelector("#scheduleModal input[name='title']").value = title;
    document.querySelector("#scheduleModal input[name='date']").value = date;
    document.querySelector("#scheduleModal input[name='start_time']").value = start || "";
    document.querySelector("#scheduleModal input[name='end_time']").value = end || "";

    // action を更新用に変更
    const form = document.querySelector("#scheduleModal form");
    form.action = `/schedule/update/${id}/`;

    // ボタンの文字を「更新」に変更
    form.querySelector("button[type='submit']").textContent = "更新";

    // モーダルタイトルも変更
    document.querySelector("#scheduleModal h2").textContent = "予定更新";
}


