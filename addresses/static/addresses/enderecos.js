// Formulário de endereço: máscara 00000-000 e preenchimento pelo ViaCEP.
// A validação definitiva acontece no servidor; os campos continuam editáveis.
(function () {
  'use strict';

  const form = document.querySelector('[data-endereco-form]');
  if (!form) return;

  const cep = form.elements.cep;
  const botao = form.querySelector('[data-buscar-cep]');
  const status = form.querySelector('[data-cep-status]');
  const urlModelo = form.dataset.cepUrl;
  const campos = ['logradouro', 'bairro', 'cidade', 'estado'];
  const rotulos = { logradouro: 'logradouro', bairro: 'bairro', cidade: 'cidade', estado: 'estado (UF)' };
  let ultimaConsulta = '';

  function mascarar(valor) {
    const digitos = valor.replace(/\D/g, '').slice(0, 8);
    return digitos.length > 5 ? digitos.slice(0, 5) + '-' + digitos.slice(5) : digitos;
  }

  function mostrar(mensagem, tipo) {
    status.textContent = mensagem;
    status.className = 'form-text text-' + tipo;
  }

  // Como no exemplo oficial do ViaCEP: CEP inválido ou não encontrado limpa
  // os campos preenchidos pela consulta, para não misturar dados de outro CEP.
  // Falha do serviço NÃO limpa, para preservar o que o usuário digitou.
  function limparCampos() {
    campos.forEach(function (nome) { form.elements[nome].value = ''; });
  }

  async function buscar() {
    const digitos = cep.value.replace(/\D/g, '');
    if (digitos.length !== 8) {
      limparCampos();
      mostrar('Informe os 8 dígitos do CEP.', 'danger');
      return;
    }
    if (digitos === ultimaConsulta) return;
    ultimaConsulta = digitos;
    botao.disabled = true;
    mostrar('Consultando CEP...', 'secondary');
    try {
      const resposta = await fetch(urlModelo.replace('00000000', digitos), {
        headers: { Accept: 'application/json' },
      });
      const dados = await resposta.json();
      if (!resposta.ok) {
        if (resposta.status === 400 || resposta.status === 404) limparCampos();
        mostrar(dados.erro || 'Não foi possível obter os dados do endereço.', 'danger');
        ultimaConsulta = '';
        return;
      }
      campos.forEach(function (nome) { form.elements[nome].value = dados[nome] || ''; });
      if (dados.campos_faltando && dados.campos_faltando.length) {
        const faltando = dados.campos_faltando.map(function (n) { return rotulos[n]; }).join(', ');
        mostrar('CEP encontrado, mas sem ' + faltando + '. Complete esses campos manualmente.', 'warning');
      } else {
        mostrar('Endereço encontrado. Confira os dados e informe o número.', 'success');
      }
      form.elements.numero.focus();
    } catch (erro) {
      mostrar('Não foi possível consultar o CEP agora. Você pode preencher os campos manualmente.', 'danger');
      ultimaConsulta = '';
    } finally {
      botao.disabled = false;
    }
  }

  cep.addEventListener('input', function () {
    cep.value = mascarar(cep.value);
    if (cep.value.replace(/\D/g, '').length === 8) buscar();
  });
  botao.addEventListener('click', function () {
    ultimaConsulta = '';
    buscar();
  });
})();
