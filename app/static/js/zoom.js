document.addEventListener("DOMContentLoaded", function () {
    console.log("🔍 Script de Zoom carregado!");

    // Criando o overlay para exibir imagens ampliadas
    let zoomOverlay = document.createElement("div");
    zoomOverlay.id = "zoomOverlay";
    
    // Criando o botão "X" e a imagem dentro do overlay
    zoomOverlay.innerHTML = `
        <button id="closeZoom">&times;</button>
        <img src="" alt="Imagem ampliada">
    `;
    
    document.body.appendChild(zoomOverlay);

    let zoomImage = zoomOverlay.querySelector("img");
    let closeZoom = document.getElementById("closeZoom");

    // Adicionando evento a todas as imagens para ampliar ao clicar
    document.querySelectorAll("img").forEach(img => {
        img.classList.add("zoomable");

        img.addEventListener("click", function () {
            zoomImage.src = this.src; 
            zoomOverlay.classList.add("mostrar"); // 🔹 Adiciona classe para ativar a transição
        });
    });

    // 🔹 Evento para fechar ao clicar no botão "X"
    closeZoom.addEventListener("click", function () {
        zoomOverlay.classList.remove("mostrar"); // 🔹 Remove a classe para esconder com efeito
    });

    // 🔹 Fechar ao clicar no overlay (fora da imagem)
    zoomOverlay.addEventListener("click", function (event) {
        if (event.target === zoomOverlay) {
            zoomOverlay.classList.remove("mostrar");
        }
    });

    // 🔹 Fechar ao pressionar a tecla ESC
    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            zoomOverlay.classList.remove("mostrar");
        }
    });
});
