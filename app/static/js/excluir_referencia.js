document.addEventListener("DOMContentLoaded", function () {
    // Seleciona todos os botões de exclusão na página
    const botoesExcluir = document.querySelectorAll(".btn-excluir");

    botoesExcluir.forEach(botao => {
        botao.addEventListener("click", function (event) {
            event.preventDefault(); // Impede o envio automático do formulário

            let confirmacao = prompt("Digite 'excluir' para confirmar a exclusão da referência:");
            confirmacao = confirmacao ? confirmacao.trim().toLowerCase() : "";

            if (confirmacao !== "excluir") {
                alert("Erro: Você deve digitar 'excluir' para confirmar a exclusão.");
                return;
            }

            // Define o valor no campo oculto do formulário correspondente
            let form = this.closest(".form-excluir");
            form.querySelector("input[name='confirmacao']").value = confirmacao;

            // Envia o formulário manualmente
            form.submit();
        });
    });
});