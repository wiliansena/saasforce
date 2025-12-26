$(document).ready(function () {
    // 🔹 Aplica apenas nos campos de peso
    $(document).on("input", "input[name*='peso_medio'], input[name*='peso_friso'], input[name*='peso_sem_friso']", function () {
        let valor = $(this).val();
        
        // Substitui a vírgula por ponto ao digitar
        valor = valor.replace(",", ".");
        
        // Garante que só tenha um único ponto decimal
        let partes = valor.split(".");
        if (partes.length > 2) {
            valor = partes[0] + "." + partes.slice(1).join("");
        }

        $(this).val(valor);
    });

    // 🔹 Aplica apenas no campo "Multiplicador"
    $(document).on("input", "input[name='multiplicador']", function () {
        let valor = $(this).val();

        // Substitui a vírgula por ponto
        valor = valor.replace(",", ".");

        // Permite apenas números e um único ponto decimal
        valor = valor.replace(/[^0-9.]/g, "");

        // Se houver mais de um ponto decimal, remove os extras
        let partes = valor.split(".");
        if (partes.length > 2) {
            valor = partes[0] + "." + partes.slice(1).join("");
        }

        $(this).val(valor);
    });
});

// 🔹 Garante a formatação para os campos de preços e encargos (incluindo salário)
document.addEventListener("DOMContentLoaded", function () {
    // Seleciona todos os campos que precisam de formatação
    const camposNumericos = document.querySelectorAll("input[name='preco'], input[name='encargos']");

    camposNumericos.forEach(function (campo) {
        campo.addEventListener("input", function () {
            let valor = this.value;

            // Substitui vírgula por ponto para evitar erro no banco
            valor = valor.replace(",", ".");

            // Permite apenas números e um único ponto decimal
            valor = valor.replace(/[^0-9.]/g, "");

            // Se houver mais de um ponto decimal, remove os extras
            let partes = valor.split(".");
            if (partes.length > 2) {
                valor = partes[0] + "." + partes.slice(1).join("");
            }

            this.value = valor;
        });
    });
});