import cv2
import mediapipe as mp
import numpy as np
import serial
import time

# Comunicação Serial com Arduino (ajuste a porta)
arduino = serial.Serial('COM5', 9600)
time.sleep(2)  # Aguarda Arduino reiniciar

# Cores Neon
AZUL_PYTHON = (255, 150, 50)
AMARELO_PYTHON = (0, 255, 255)
BRANCO_PURO = (255, 255, 255)

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.8,
    min_tracking_confidence=0.8
)

cap = cv2.VideoCapture(0)

def desenhar_hud_vibrante(img, texto, total_dedos, mao_tipo, pos_x):
    overlay = img.copy()
    cor_tema = AZUL_PYTHON if mao_tipo == "Left" else AMARELO_PYTHON
    lado_pt = "ESQUERDA" if mao_tipo == "Left" else "DIREITA"

    cv2.rectangle(overlay, (pos_x, 20), (pos_x + 280, 130), (10, 10, 10), -1)
    cv2.addWeighted(overlay, 0.7, img, 0.3, 0, img)

    cv2.line(img, (pos_x, 20), (pos_x + 50, 20), cor_tema, 4)
    cv2.line(img, (pos_x, 20), (pos_x, 70), cor_tema, 4)

    cv2.putText(img, f"MÃO {lado_pt}", (pos_x + 15, 55), 
                cv2.FONT_HERSHEY_DUPLEX, 0.7, cor_tema, 2)
    
    cv2.putText(img, texto, (pos_x + 15, 85), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, BRANCO_PURO, 1)

    largura_barra = int((total_dedos / 5) * 250)
    cv2.rectangle(img, (pos_x + 15, 105), (pos_x + 265, 115), (40, 40, 40), -1)
    cv2.rectangle(img, (pos_x + 15, 105), (pos_x + 15 + largura_barra, 115), cor_tema, -1)

def contar_dedos_pt(landmarks, hand_label):
    dedos = []
    # Polegar
    if hand_label == "Right":
        dedos.append(landmarks[4].x < landmarks[3].x)
    else:
        dedos.append(landmarks[4].x > landmarks[3].x)
    # Outros 4 dedos
    for ponta, base in [(8, 6), (12, 10), (16, 14), (20, 18)]:
        dedos.append(landmarks[ponta].y < landmarks[base].y)
    return dedos

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    total_dedos = 0

    if result.multi_hand_landmarks:
        for idx, hand_landmarks in enumerate(result.multi_hand_landmarks):
            info_mao = result.multi_handedness[idx].classification[0].label
            cor_atual = AZUL_PYTHON if info_mao == "Left" else AMARELO_PYTHON

            mp_draw.draw_landmarks(
                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                mp_draw.DrawingSpec(color=BRANCO_PURO, thickness=2, circle_radius=2),
                mp_draw.DrawingSpec(color=cor_atual, thickness=3)
            )

            dedos = contar_dedos_pt(hand_landmarks.landmark, info_mao)
            total = dedos.count(True)
            total_dedos = max(total_dedos, total)  # Mantém o maior número detectado

            status = f"PROCESSANDO: {total} DADOS" if total > 0 else "AGUARDANDO ENTRADA"
            pos_x_hud = 20 if info_mao == "Left" else w - 300
            desenhar_hud_vibrante(frame, status, total, info_mao, pos_x_hud)

    # Envia o número de dedos para o Arduino (máx 5)
    arduino.write(str(min(total_dedos, 5)).encode())

    cv2.putText(frame, "MOTOR DE GESTOS PYTHON ATIVO", (w//2 - 150, h - 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1)

    cv2.imshow("Interface Python Neon", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC para sair
        break

cap.release()
cv2.destroyAllWindows()
arduino.close()