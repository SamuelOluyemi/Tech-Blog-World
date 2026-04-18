
// With the aid of ChatGPT Atlas
function formatSmartTime(date) {
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);
    const days = Math.floor(seconds / 86400);

    if (seconds < 60) return "Just now";

    if (seconds < 3600) {
        const minutes = Math.floor(seconds / 60);
        return minutes + " minute" + (minutes > 1 ? "s" : "") + " ago";
    }

    if (seconds < 86400) {
        const hours = Math.floor(seconds / 3600);
        return hours + " hour" + (hours > 1 ? "s" : "") + " ago";
    }

    if (days === 1) return "Yesterday";

    if (days < 7) {
        return days + " days ago";
    }

    return date.toLocaleDateString(undefined, {
        year: "numeric",
        month: "short",
        day: "numeric"
    });
}

function updateSmartTimes() {
    document.querySelectorAll(".smart-time").forEach(function(el) {
        const utcTime = el.getAttribute("data-time");
        if (!utcTime) return;

        const date = new Date(utcTime);
        el.textContent = formatSmartTime(date);
    });
}

document.addEventListener("DOMContentLoaded", function () {
    updateSmartTimes();
    setInterval(updateSmartTimes, 60000);
});

