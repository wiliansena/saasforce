$(document).ready(function () {
    console.log("🔹 Script de edição de referência carregado!");

    // 🔹 Função para adicionar itens na tabela correta
    function adicionarItemNaTabela(tipo, id, descricao, preco) {
        let tabela = $(`#tabela-${tipo} tbody`);
        if (!tabela.length) {
            console.error(`❌ Erro: Tabela '${tipo}' não encontrada.`);
            return;
        }

        // 🚨 Se algum valor for indefinido, exibe erro e impede a adição
        if (!id || !descricao || isNaN(parseFloat(preco))) {
            console.error(`❌ Erro: Tentativa de adicionar item indefinido!`, { id, descricao, preco, tipo });
            return;
        }

        // Verifica se o item já está na tabela para evitar duplicação
        if ($(`#tabela-${tipo} tbody tr[data-id="${id}"]`).length > 0) {
            console.warn(`⚠️ O item ${id} já foi adicionado à tabela '${tipo}'.`);
            return;
        }

        let nomeInput = tipo.includes("embalagem") ? `componentes_${tipo}[]` : `${tipo}_id[]`;
        let consumoInput = tipo.includes("embalagem") ? `consumo_${tipo}[]` : `${tipo}_consumo[]`;

        let novaLinha = `
            <tr class="linha-adicionada" data-id="${id}">
                <td><input type="hidden" name="${nomeInput}" value="${id}">${id}</td>
                <td>${descricao}</td>
                <td>R$ ${parseFloat(preco).toFixed(2)}</td>
                <td><input type="number" name="${consumoInput}" class="form-control consumo-input" step="0.000001" min="0" value="1"></td>
                <td><button type="button" class="btn btn-danger btn-sm remover-item">Remover</button></td>
            </tr>
        `;

        tabela.append(novaLinha);
        console.log(`✅ Item adicionado: ${descricao} (ID: ${id}) na tabela '${tipo}'.`);
    }

    // 🔹 Remover itens da tabela
    $(document).on("click", ".remover-item", function () {
        $(this).closest("tr").remove();
        console.log("❌ Item removido.");
    });

    // 🔹 Mantendo a estrutura original dos botões para custo operacional e mão de obra
    $(document).on("click", ".selecionar-custo", function () {
        adicionarItemNaTabela("custo", $(this).data("id"), $(this).data("descricao"), $(this).data("preco"));
      //  $("#modalCustos").modal("hide");
    });

    $(document).on("click", ".selecionar-mao", function () {
        let id = $(this).data("id");
        let descricao = $(this).data("descricao");
        let diaria = $(this).data("diaria");
    
        let tabela = $("#tabela-mao_obra tbody");
    
        if (!tabela.length) {
            console.error("Erro: Tabela 'mao_obra' não encontrada.");
            return;
        }
    
        // Evita duplicação na tabela
        if ($(`#tabela-mao_obra tbody tr[data-id="${id}"]`).length > 0) {
            console.warn(`O item ${id} já foi adicionado à tabela 'mao_obra'.`);
            return;
        }
    
        let novaLinha = `
            <tr class="linha-adicionada" data-id="${id}">
                <td><input type="hidden" name="mao_obra_id[]" value="${id}">${id}</td>
                <td>${descricao}</td>
                <td>R$ ${parseFloat(diaria).toFixed(2)}</td>
                <td><input type="number" name="mao_obra_consumo[]" class="form-control consumo-input" step="0.000001" min="0" value="1"></td>
                <td><input type="number" name="mao_obra_producao[]" class="form-control producao-input" step="1" min="1" value="1"></td>
                <td><button type="button" class="btn btn-danger btn-sm remover-item">Remover</button></td>
            </tr>
        `;
    
        tabela.append(novaLinha);
        console.log(`✅ Item adicionado: ${descricao} (ID: ${id}) na tabela 'mao_obra'.`);
    
      //  $("#modalMaoObra").modal("hide");
    });
    

    // 🔹 Mantendo a estrutura original para solado e alça
    $(document).on("click", ".selecionar-solado", function () {
        adicionarItemNaTabela("solado", $(this).data("id"), $(this).data("descricao"), $(this).data("preco"));
        $("#modalSolado").modal("hide");
    });

    $(document).on("click", ".selecionar-alca", function () {
        adicionarItemNaTabela("alca", $(this).data("id"), $(this).data("descricao"), $(this).data("preco"));
        $("#modalAlca").modal("hide");
    });

    // 🔹 Selecionar Componentes (corrigido)
    $(document).on("click", ".selecionar-componente", function () {
        let button = $(this);
        let id = button.data("id");
        let descricao = button.data("descricao");
        let preco = button.data("preco");
        let tipo = "componente"; // Forçar o tipo correto

        // Se os dados estiverem indefinidos, exibir erro e não prosseguir
        if (!id || !descricao || isNaN(parseFloat(preco))) {
            console.warn(`⚠️ Ignorando clique no botão ${tipo} - Dados incompletos`);
            return;
        }

        console.log(`🛠️ Clicado: ${tipo} | ID: ${id}, Descrição: ${descricao}, Preço: ${preco}`);
        adicionarItemNaTabela(tipo, id, descricao, preco);

        // Fechar modal corretamente
        //$("#modalComponentes").modal("hide");//
    });

    // 🔹 Melhorando apenas os botões de componentes e embalagens
    $(document).on("click", ".selecionar-embalagem1, .selecionar-embalagem2, .selecionar-embalagem3", function () {
        let button = $(this);
        let id = button.data("id");
        let descricao = button.data("descricao");
        let preco = button.data("preco");
        let tipo = button.data("tipo");
    
        // Se os dados estiverem indefinidos, não faz nada
        if (!id || !descricao || isNaN(parseFloat(preco))) {
            console.warn(`⚠️ Ignorando clique no botão ${tipo} - Dados incompletos`);
            return;
        }
    
        console.log(`🛠️ Clicado: ${tipo} | ID: ${id}, Descrição: ${descricao}, Preço: ${preco}`);
        adicionarItemNaTabela(tipo, id, descricao, preco);
        $(`#modalComponentes`).modal("hide");
    });

    // 🔹 Capturando o tipo correto ao abrir os modais de embalagem
    $(".selecionar-embalagem1, .selecionar-embalagem2, .selecionar-embalagem3").on("click", function () {
        let tipo = $(this).data("tipo");
        console.log(`📌 Abrindo modal de ${tipo}`);
        $("#modalComponentes").attr("data-tipo", tipo);
    });

    // 🔹 Antes de enviar o formulário, garantir que os campos vazios tenham valores padrão
    $("form").on("submit", function () {
        console.log("🔹 Preparando os valores antes de enviar...");

        $("input[type='number']").each(function () {
            if ($(this).val().trim() === "" || isNaN($(this).val())) {
                $(this).val(0);
            }
        });

        console.log("🔹 Formulário pronto para envio!");
    });
});
