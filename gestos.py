import cv2
import mediapipe as mp
import numpy as np
import serial
import time
import tkinter as tk

# --- 1. RESOLUÇÃO DO MONITOR ---
root = tk.Tk()
LARGURA_MONITOR = root.winfo_screenwidth()
ALTURA_MONITOR = root.winfo_screenheight()
root.destroy()

# --- 2. COMUNICAÇÃO SERIAL ---
try:
    arduino = serial.Serial('COM5', 9600)
    time.sleep(2)
except:
    arduino = None

# --- 3. CONFIGURAÇÕES E ESTADOS ---
AZUL_PYTHON = (255, 150, 50)
AMARELO_PYTHON = (0, 255, 255)
VERDE_NEON = (0, 255, 100)
BRANCO_PURO = (255, 255, 255)

# Variáveis de controle para o modo rosto
MODO_ROSTO_ATIVO = False
ULTIMO_ESTADO_PINCH = False

mp_hands = mp.solutions.hands
mp_face_mesh = mp.solutions.face_mesh
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8)
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True, min_detection_confidence=0.7)

cap = cv2.VideoCapture(0)
nome_janela = "Interface Bio-Tech"
cv2.namedWindow(nome_janela, cv2.WINDOW_NORMAL)
cv2.setWindowProperty(nome_janela, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

def desenhar_hud_vibrante(img, texto, total_dedos, mao_tipo, pos_x, modo_rosto):
    overlay = img.copy()
    cor_tema = AZUL_PYTHON if mao_tipo == "Left" else AMARELO_PYTHON
    
    cv2.rectangle(overlay, (pos_x, 20), (pos_x + 280, 140), (10, 10, 10), -1)
    cv2.addWeighted(overlay, 0.7, img, 0.3, 0, img)
    
    cv2.line(img, (pos_x, 20), (pos_x + 50, 20), cor_tema, 4)
    cv2.putText(img, f"MAO {mao_tipo.upper()}", (pos_x + 15, 55), cv2.FONT_HERSHEY_DUPLEX, 0.7, cor_tema, 2)
    cv2.putText(img, texto, (pos_x + 15, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.6, BRANCO_PURO, 1)
    
    status_rosto = "ROSTO: ATIVO" if modo_rosto else "ROSTO: STANDBY"
    cv2.putText(img, status_rosto, (pos_x + 15, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5, VERDE_NEON if modo_rosto else (100,100,100), 1)

    largura_barra = int((total_dedos / 5) * 250)
    cv2.rectangle(img, (pos_x + 15, 120), (pos_x + 265, 130), (40, 40, 40), -1)
    cv2.rectangle(img, (pos_x + 15, 120), (pos_x + 15 + largura_barra, 130), cor_tema, -1)

def contar_dedos_pt(landmarks, hand_label):
    dedos = []
    if hand_label == "Right":
        dedos.append(landmarks[4].x < landmarks[3].x)
    else:
        dedos.append(landmarks[4].x > landmarks[3].x)
    for ponta, base in [(8, 6), (12, 10), (16, 14), (20, 18)]:
        dedos.append(landmarks[ponta].y < landmarks[base].y)
    return dedos

# --- LOOP PRINCIPAL ---
while True:
    ret, frame = cap.read()
    if not ret: break

    frame = cv2.flip(frame, 1)
    h_orig, w_orig = frame.shape[:2]

    # Letterboxing (Mantendo proporção)
    escala = min(LARGURA_MONITOR / w_orig, ALTURA_MONITOR / h_orig)
    nw, nh = int(w_orig * escala), int(h_orig * escala)
    frame_redim = cv2.resize(frame, (nw, nh))

    canvas = np.zeros((ALTURA_MONITOR, LARGURA_MONITOR, 3), dtype=np.uint8)
    y_off, x_off = (ALTURA_MONITOR - nh) // 2, (LARGURA_MONITOR - nw) // 2
    canvas[y_off:y_off+nh, x_off:x_off+nw] = frame_redim

    rgb = cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)
    res_hands = hands.process(rgb)

    total_dedos = 0
    pinch_nesta_frame = False

    if res_hands.multi_hand_landmarks:
        for idx, hand_landmarks in enumerate(res_hands.multi_hand_landmarks):
            info_mao = res_hands.multi_handedness[idx].classification[0].label
            
            # --- LÓGICA DO GESTO ATIVADOR ---
            p4 = hand_landmarks.landmark[4] # Polegar
            p8 = hand_landmarks.landmark[8] # Indicador
            # Distância entre os dedos (normalizada)
            distancia = np.hypot(p4.x - p8.x, p4.y - p8.y)

            if distancia < 0.03: # Limiar para o "clique" dos dedos
                pinch_nesta_frame = True
            
            # Desenha mãos conforme lógica original
            mp_draw.draw_landmarks(canvas, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                mp_draw.DrawingSpec(color=BRANCO_PURO, thickness=2, circle_radius=2),
                mp_draw.DrawingSpec(color=AZUL_PYTHON if info_mao == "Left" else AMARELO_PYTHON, thickness=3))
            
            dedos = contar_dedos_pt(hand_landmarks.landmark, info_mao)
            total = dedos.count(True)
            total_dedos = max(total_dedos, total)
            
            pos_x_hud = 40 if info_mao == "Left" else LARGURA_MONITOR - 320
            desenhar_hud_vibrante(canvas, f"SISTEMA: {total} DADOS", total, info_mao, pos_x_hud, MODO_ROSTO_ATIVO)

    # Inverter estado do rosto apenas na transição do "toque"
    if pinch_nesta_frame and not ULTIMO_ESTADO_PINCH:
        MODO_ROSTO_ATIVO = not MODO_ROSTO_ATIVO
    ULTIMO_ESTADO_PINCH = pinch_nesta_frame

    # --- PROCESSAMENTO DO ROSTO (WIRE FRAME) ---
    if MODO_ROSTO_ATIVO:
        res_face = face_mesh.process(rgb)
        if res_face.multi_face_landmarks:
            for face_landmarks in res_face.multi_face_landmarks:
                # Wireframe Mesh
                mp_draw.draw_landmarks(
                    image=canvas,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_draw.DrawingSpec(color=VERDE_NEON, thickness=1)
                )
                # Olhos / Íris com precisão
                for i in [468, 473]:
                    p = face_landmarks.landmark[i]
                    ix, iy = int(p.x * LARGURA_MONITOR), int(p.y * ALTURA_MONITOR)
                    cv2.circle(canvas, (ix, iy), 12, AMARELO_PYTHON, 1)
                    cv2.circle(canvas, (ix, iy), 2, BRANCO_PURO, -1)

    # Comunicação Serial
    if arduino:
        arduino.write(str(min(total_dedos, 5)).encode())

    # Rodapé dinâmico
    status_msg = "SISTEMA COMPLETO ATIVO" if MODO_ROSTO_ATIVO else "AGUARDANDO GESTO DE ATIVACAO"
    cv2.putText(canvas, status_msg, (int(LARGURA_MONITOR/2)-150, ALTURA_MONITOR-30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, VERDE_NEON if MODO_ROSTO_ATIVO else (100,100,100), 1)

    cv2.imshow(nome_janela, canvas)
    if cv2.waitKey(1) & 0xFF == 27: break

cap.release()
cv2.destroyAllWindows()
if arduino: arduino.close()