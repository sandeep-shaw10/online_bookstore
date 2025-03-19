document.addEventListener('DOMContentLoaded', function() {


    document.querySelectorAll("#message-popup").forEach((msg) => {
        setTimeout(() => {
            msg.classList.add("opacity-0");
            setTimeout(() => msg.remove(), 500);
        }, 5000);
    
        msg.addEventListener("click", () => {
            msg.classList.add("opacity-0");
            setTimeout(() => msg.remove(), 500);
        });
    });


});