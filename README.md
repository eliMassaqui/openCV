# Motor de Gestos Python - Interface Neon 🖐️⚡

Este projeto é um sistema de visão computacional de alta performance que utiliza Mediapipe e OpenCV para rastrear mãos em tempo real com uma interface HUD (Heads-Up Display) estilizada em cores neon.

---

## 🛠️ Tecnologias e Ambiente

* **Python 3.10** (Gerenciado via Anaconda)
* **OpenCV**: Manipulação de frames e renderização de interface.
* **Mediapipe**: Extração de landmarks e processamento de gestos.
* **Numpy**: Operações de matriz.

---

## 📦 Configuração e Execução (Obrigatório)

Para garantir que o modelo funcione com todas as dependências de visão computacional, o uso do ambiente Conda é obrigatório.

### 1. Localização do Projeto

O projeto deve ser executado a partir do diretório de trabalho:

```
C:\Users\UMALAB\Desktop\gestos
```

### 2. Ativação do Ambiente Anaconda

Abra o terminal (Anaconda Prompt ou PowerShell) e execute a ativação do ambiente dedicado:

```powershell
# Ativação do ambiente específico de gestos
conda activate gestos
```

### 3. Execução do Sistema

Após a ativação, execute o motor principal:

```powershell
# Certifique-se de estar na pasta do projeto
cd C:\Users\UMALAB\Desktop\gestos
python gestos.py
```

---

## 🧠 Lógica e Estrutura do Código

O projeto respeita uma lógica rigorosa de detecção baseada na orientação da mão (Esquerda/Direita).

> **Atenção à Identação:** O código utiliza estritamente 4 espaços. Alterações na estrutura de repetição ou condicionais sem respeitar esta regra causarão falhas no loop de processamento do OpenCV.

### Função de Contagem de Dedos

```python
def contar_dedos_pt(landmarks, hand_label):
    dedos = []
    # Lógica do Polegar (Invertida conforme a mão para precisão horizontal)
    if hand_label == "Right":
        dedos.append(landmarks[4].x < landmarks[3].x)
    else:
        dedos.append(landmarks[4].x > landmarks[3].x)

    # Verificação de elevação dos outros 4 dedos (Eixo Y)
    # Comparação entre a ponta (Tip) e a articulação média (PIP)
    for ponta, base in [(8, 6), (12, 10), (16, 14), (20, 18)]:
        dedos.append(landmarks[ponta].y < landmarks[base].y)
    
    return dedos
```

---

## 🎨 Identidade Visual (Estilo Neon)

| Elemento       | Cor (BGR)       | Descrição                             |
| -------------- | --------------- | ------------------------------------- |
| AZUL_PYTHON    | (255, 150, 50)  | Azul Elétrico para Mão Esquerda       |
| AMARELO_PYTHON | (0, 255, 255)   | Amarelo Fluorescente para Mão Direita |
| BRANCO_PURO    | (255, 255, 255) | Detalhes de HUD e Texto               |
