// Pagamento simulado: máscaras de cartão e contagem regressiva do PIX.
// A validação definitiva acontece no servidor.
(function () {
  'use strict';
  if (window.__pagamentosSimulados) return; // partials podem incluir o script mais de uma vez
  window.__pagamentosSimulados = true;

  const mascaras = {
    cartao: function (v) {
      return v.replace(/\D/g, '').slice(0, 16).replace(/(\d{4})(?=\d)/g, '$1 ');
    },
    validade: function (v) {
      const d = v.replace(/\D/g, '').slice(0, 4);
      return d.length > 2 ? d.slice(0, 2) + '/' + d.slice(2) : d;
    },
    cvv: function (v) { return v.replace(/\D/g, '').slice(0, 3); },
  };

  function iniciar() {
    document.querySelectorAll('[data-mascara]').forEach(function (campo) {
      const mascara = mascaras[campo.dataset.mascara];
      if (!mascara) return;
      campo.value = mascara(campo.value);
      campo.addEventListener('input', function () { campo.value = mascara(campo.value); });
    });

    // Aviso ao sair do campo de validade (o servidor continua validando no envio).
    document.querySelectorAll('[data-mascara="validade"]').forEach(function (campo) {
      const aviso = document.createElement('div');
      aviso.className = 'small text-danger mt-1';
      aviso.setAttribute('aria-live', 'polite');
      campo.insertAdjacentElement('afterend', aviso);

      function erroValidade(valor) {
        if (!valor) return '';
        const m = /^(\d{2})\/(\d{2})$/.exec(valor);
        if (!m) return 'Informe a validade no formato MM/AA.';
        const mes = parseInt(m[1], 10);
        const ano = 2000 + parseInt(m[2], 10);
        if (mes < 1 || mes > 12) return 'Mês de validade inválido.';
        const hoje = new Date();
        if (ano < hoje.getFullYear() || (ano === hoje.getFullYear() && mes < hoje.getMonth() + 1)) return 'Cartão vencido.';
        return '';
      }

      campo.addEventListener('blur', function () {
        const erro = erroValidade(campo.value);
        aviso.textContent = erro;
        campo.classList.toggle('is-invalid', Boolean(erro));
      });
      campo.addEventListener('input', function () {
        aviso.textContent = '';
        campo.classList.remove('is-invalid');
      });
    });

    document.querySelectorAll('[data-pix]').forEach(function (bloco) {
      const expira = new Date(bloco.dataset.expiraEm).getTime();
      const contador = bloco.querySelector('[data-pix-contador]');
      function atualizar() {
        const restante = Math.max(0, Math.ceil((expira - Date.now()) / 1000));
        if (restante > 0) {
          contador.textContent = 'Expira em ' + restante + ' s';
          return;
        }
        clearInterval(timer);
        contador.textContent = 'PIX expirado. Gere um novo código.';
        contador.className = 'text-danger';
        const badge = bloco.querySelector('[data-pix-badge]');
        badge.textContent = 'Expirado';
        badge.className = 'badge text-bg-secondary';
        bloco.querySelector('img').style.opacity = '0.25';
        bloco.querySelector('[data-pix-acoes]').classList.add('d-none');
        bloco.querySelector('[data-pix-novo]').classList.remove('d-none');
      }
      const timer = setInterval(atualizar, 1000);
      atualizar();
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar);
  else iniciar();
})();
