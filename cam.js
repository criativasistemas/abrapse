// Inicializar o acesso à câmera e capturar imagens em cada etapa
function setupVideo(videoElement, canvasElement, snapButton, nextButton) {
    // Acessar a câmera para o vídeo
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(stream => {
        videoElement.srcObject = stream;
      })
      .catch(err => {
        console.error('Erro ao acessar a câmera:', err);
      });
  
    // Capturar imagem do vídeo
    const context = canvasElement.getContext('2d');
    snapButton.addEventListener('click', () => {
      context.drawImage(videoElement, 0, 0, 320, 240);
    });
  
    nextButton.addEventListener('click', () => {
      nextStep();
    });
  }
  
  // Função para passar para a próxima etapa
  function nextStep() {
    const currentStep = document.querySelector('.active');
    currentStep.classList.remove('active');
    
    const nextStep = currentStep.nextElementSibling;
    if (nextStep) {
      nextStep.classList.add('active');
    }
  }
  
  // Configurar os vídeos e os botões para cada etapa
  setupVideo(document.getElementById('video1'), document.getElementById('canvas1'), document.getElementById('snap1'), document.getElementById('next1'));
  setupVideo(document.getElementById('video2'), document.getElementById('canvas2'), document.getElementById('snap2'), document.getElementById('next2'));
  setupVideo(document.getElementById('video3'), document.getElementById('canvas3'), document.getElementById('snap3'), document.getElementById('next3'));
  setupVideo(document.getElementById('video4'), document.getElementById('canvas4'), document.getElementById('snap4'), document.getElementById('finish'));
  
  // Finalizar o teste e enviar todas as imagens
  document.getElementById('finish').addEventListener('click', () => {
    const images = [
      document.getElementById('canvas1').toDataURL('image/png'),
      document.getElementById('canvas2').toDataURL('image/png'),
      document.getElementById('canvas3').toDataURL('image/png'),
      document.getElementById('canvas4').toDataURL('image/png'),
    ];
  
    // Enviar as imagens capturadas para o backend
    fetch('/upload', {
      method: 'POST',
      body: JSON.stringify({ images }),
      headers: { 'Content-Type': 'application/json' }
    })
    .then(response => response.json())
    .then(data => {
      console.log('Imagens enviadas com sucesso:', data);
    })
    .catch(error => {
      console.error('Erro ao enviar as imagens:', error);
    });
  });
  