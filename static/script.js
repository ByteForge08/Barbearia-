//  funções do global
function abrirModal() {
    document.getElementById('modalLogin').style.display = 'block';
}

function fecharModal() {
    document.getElementById('modalLogin').style.display = 'none';
}

// fecha quando clica fora da caixa
window.onclick = function(event) {
    let modal = document.getElementById('modalLogin');
    if (event.target == modal) {
        fecharModal();
    }
}

//  valida o agendamento
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form-agendamento');

    if(form) {
        form.addEventListener('submit', (event) => {
            const dataSelecionada = document.getElementById('data').value;
            const hoje = new Date().toISOString().split('T')[0];

            if (dataSelecionada < hoje) {
                alert("Ei, você não pode agendar para uma data que já passou!");
                event.preventDefault();
                return;
            }
            console.log("Enviando agendamento...");
        });
    }
});