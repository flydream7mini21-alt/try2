function copyUserId() {
    const idText = document.getElementById("userId").textContent;
    navigator.clipboard.writeText(idText).then(() => {
        alert("専用IDをコピーしました！");
    });
}