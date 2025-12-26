document.addEventListener('DOMContentLoaded', function() {

    // -------------------------------
    // Seleção de Funcionário (Solicitante / Responsável)
    // -------------------------------
    document.querySelectorAll('.selecionar-funcionario').forEach(botao => {
        botao.addEventListener('click', function() {
            const tipo = this.dataset.tipo;
            const id = this.dataset.id;
            const nome = this.dataset.nome;

            if (tipo === 'solicitante') {
                document.getElementById('solicitante_id').value = id;
                document.getElementById('solicitante_nome').value = nome;
                $('#modalSolicitante').modal('hide');
            } else if (tipo === 'responsavel') {
                document.getElementById('responsavel_id').value = id;
                document.getElementById('responsavel_nome').value = nome;
                $('#modalResponsavel').modal('hide');
            }
        });
    });

    // -------------------------------
    // Adicionar Máquina
    // -------------------------------
    document.querySelectorAll('.selecionar-maquina').forEach(botao => {
        botao.addEventListener('click', function() {
            const id = this.dataset.id;
            const codigo = this.dataset.codigo;
            const descricao = this.dataset.descricao;

            const tabela = document.querySelector('#tabela-maquinas tbody');

            if (tabela.querySelector(`tr[data-id="${id}"]`)) {
                alert('Esta máquina já foi adicionada.');
                return;
            }

            const linha = document.createElement('tr');
            linha.setAttribute('data-id', id);
            linha.innerHTML = `
                <td>
                    <input type="hidden" name="maquina_id[]" value="${id}">
                    ${codigo} - ${descricao}
                </td>
                <td><button type="button" class="btn btn-danger btn-sm remover-linha">Remover</button></td>
            `;
            tabela.appendChild(linha);

            $('#modalMaquinas').modal('hide');
        });
    });

    // -------------------------------
    // Adicionar Componente
    // -------------------------------
    document.querySelectorAll('.selecionar-componente').forEach(botao => {
        botao.addEventListener('click', function() {
            const id = this.dataset.id;
            const codigo = this.dataset.codigo;
            const descricao = this.dataset.descricao;

            const tabela = document.querySelector('#tabela-componentes tbody');

            if (tabela.querySelector(`tr[data-id="${id}"]`)) {
                alert('Este componente já foi adicionado.');
                return;
            }

            const linha = document.createElement('tr');
            linha.setAttribute('data-id', id);
            linha.innerHTML = `
                <td>
                    <input type="hidden" name="componente_id[]" value="${id}">
                    ${codigo}
                </td>
                <td>${descricao}</td>
                <td><button type="button" class="btn btn-danger btn-sm remover-linha">Remover</button></td>
            `;
            tabela.appendChild(linha);

            $('#modalComponentes').modal('hide');
        });
    });


        // -------------------------------
    // Adicionar Peca
    // -------------------------------
    document.querySelectorAll('.selecionar-peca').forEach(botao => {
        botao.addEventListener('click', function() {
            const id = this.dataset.id;
            const codigo = this.dataset.codigo;
            const descricao = this.dataset.descricao;

            const tabela = document.querySelector('#tabela-pecas tbody');

            if (tabela.querySelector(`tr[data-id="${id}"]`)) {
                alert('Esta Peça já foi adicionada.');
                return;
            }

            const linha = document.createElement('tr');
            linha.setAttribute('data-id', id);
            linha.innerHTML = `
                <td>
                    <input type="hidden" name="peca_id[]" value="${id}">
                    ${codigo}
                </td>
                <td>${descricao}</td>
                <td><button type="button" class="btn btn-danger btn-sm remover-linha">Remover</button></td>
            `;
            tabela.appendChild(linha);

            $('#modalPecas').modal('hide');
        });
    });

    // -------------------------------
    // Remover qualquer linha
    // -------------------------------
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('remover-linha')) {
            e.target.closest('tr').remove();
        }
    });

});
