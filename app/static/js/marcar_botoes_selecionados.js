
// BOTÕES DE SELEÇÃO DOS MODAIS, MARCA COMO SELECIONADO.


document.addEventListener("DOMContentLoaded", function () {
    function atualizarBotoesSelecionados() {
        const botoes = document.querySelectorAll("button[data-tipo]");

        botoes.forEach(botao => {
            const tipo = botao.getAttribute("data-tipo");
            const id = botao.getAttribute("data-id");
            const codigo = botao.getAttribute("data-codigo");  // Pode não existir

            const tabela = document.getElementById(`tabela-${tipo}`);
            if (!tabela && tipo !== "referencia") return;

            let itemExiste = false;

            if (tipo === "referencia" && codigo) {
                try {
                    const seletor = "#referencia_" + CSS.escape(codigo);
                    itemExiste = !!document.querySelector(seletor);
                } catch (err) {
                    console.warn("Código de referência inválido:", codigo, err);
                }
            } else if (tabela && id) {
                itemExiste = !!tabela.querySelector(`tr[data-id='${id}']`);
            }

            if (itemExiste) {
                botao.innerText = "Selecionado";
                botao.classList.remove("btn-success");
                botao.classList.add("btn-secondary");
                botao.disabled = true;
            } else {
                botao.innerText = "Selecionar";
                botao.classList.remove("btn-secondary");
                botao.classList.add("btn-success");
                botao.disabled = false;
            }
        });
    }

    // Atualiza ao abrir qualquer modal
    document.querySelectorAll(".modal").forEach(modal => {
        modal.addEventListener("show.bs.modal", () => {
            setTimeout(atualizarBotoesSelecionados, 100);
        });
    });

    // Atualiza em tempo real após clicar
    document.addEventListener("click", function (e) {
        if (e.target.matches("button[data-tipo]") || e.target.classList.contains("remove-referencia") || e.target.classList.contains("remover-item")) {
            setTimeout(atualizarBotoesSelecionados, 100);
        }
    });
});
