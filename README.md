# Motor de Gestos Python - Interface Neon 🖐️⚡

Este projeto é um sistema de visão computacional de alta performance que utiliza Mediapipe e OpenCV para rastrear mãos em tempo real com uma interface HUD (Heads-Up Display) estilizada em cores neon (Azul Elétrico e Amarelo Fluorescente). 🚀

## Funcionalidades

* **Detecção Dupla:** Suporte para até 2 mãos simultâneas.
* **HUD Vibrante:** Interface dinâmica que identifica o lado da mão (Esquerda/Direita).
* **Contador de Dados:** Lógica de contagem de dedos com barra de progresso responsiva.
* **Estética Python:** Cores personalizadas baseadas na identidade visual do Python.

## 🛠️ Tecnologias Utilizadas

* Python 3.10
* **OpenCV:** Manipulação de frames e renderização de interface.
* **Mediapipe:** Extração de landmarks e processamento de gestos.
* **Numpy:** Suporte para operações de matriz de imagem.

## 📦 Como Instalar e Rodar

1. **Clone o repositório:**

```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
```

2. **Instale as dependências:**

```bash
pip install opencv-python mediapipe numpy
```

3. **Execute o script:**

```bash
python seu_arquivo.py
```

## 🧠 Lógica e Estrutura do Código

O projeto segue uma lógica rigorosa de processamento de imagem e interface. Exemplo da estrutura principal:

```python
def contar_dedos_pt(landmarks, hand_label):
    dedos = []
    # Lógica do Polegar (Invertida conforme a mão)
    if hand_label == "Right":
        dedos.append(landmarks[4].x < landmarks[3].x)
    else:
        dedos.append(landmarks[4].x > landmarks[3].x)

    # Outros 4 dedos (Verificação de altura Y)
    for ponta, base in [(8, 6), (12, 10), (16, 14), (20, 18)]:
        dedos.append(landmarks[ponta].y < landmarks[base].y)
    
    return dedos
```

> **Nota sobre Identação:** O código utiliza 4 espaços para manter a consistência e evitar erros, especialmente em funções de desenho complexas.

## 🎨 Cores Utilizadas (Estilo Neon)

| Elemento       | Cor (BGR)       | Descrição                             |
| -------------- | --------------- | ------------------------------------- |
| AZUL_PYTHON    | (255, 150, 50)  | Azul Elétrico para Mão Esquerda       |
| AMARELO_PYTHON | (0, 255, 255)   | Amarelo Fluorescente para Mão Direita |
| BRANCO_PURO    | (255, 255, 255) | Detalhes e Texto                      |
