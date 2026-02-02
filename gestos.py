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
ROXO_NEON = (255, 0, 255)
BRANCO_PURO = (255, 255, 255)
VERMELHO_REC = (0, 0, 255)

MODO_ROSTO_ATIVO = False
ULTIMO_ESTADO_PINCH = False
GRAVANDO = False
video_writer = None

# Configuração do Botão Virtual de Gravação
BOTAO_REC_POS = (LARGURA_MONITOR // 2, 80) # Centralizado no topo
BOTAO_REC_RAIO = 40
COOLDOWN_BOTAO = 0 # Para evitar múltiplos cliques rápidos

mp_hands = mp.solutions.hands
mp_face_mesh = mp.solutions.face_mesh
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8)
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True, min_detection_confidence=0.7)

cap = cv2.VideoCapture(0)
nome_janela = "Interface Bio-Tech Holographic REC"
cv2.namedWindow(nome_janela, cv2.WINDOW_NORMAL)
cv2.setWindowProperty(nome_janela, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

OLHO_ESQ = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
OLHO_DIR = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]

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

def desenhar_contorno_olho(img, landmarks, indices, cor):
    pts = []
    for i in indices:
        p = landmarks[i]
        pts.append([int(p.x * LARGURA_MONITOR), int(p.y * ALTURA_MONITOR)])
    cv2.polylines(img, [np.array(pts, np.int32)], True, cor, 1, cv2.LINE_AA)

while True:
    ret, frame = cap.read()
    if not ret: break

    frame = cv2.flip(frame, 1)
    h_orig, w_orig = frame.shape[:2]

    escala = min(LARGURA_MONITOR / w_orig, ALTURA_MONITOR / h_orig)
    nw, nh = int(w_orig * escala), int(h_orig * escala)
    frame_redim = cv2.resize(frame, (nw, nh))

    canvas = np.zeros((ALTURA_MONITOR, LARGURA_MONITOR, 3), dtype=np.uint8)
    y_off, x_off = (ALTURA_MONITOR - nh) // 2, (LARGURA_MONITOR - nw) // 2
    canvas[y_off:y_off+nh, x_off:x_off+nw] = frame_redim

    rgb = cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)
    res_hands = hands.process(rgb)

    total_dedos = 0
    pinch_mao_direita = False
    ponto_indicador = None

    if res_hands.multi_hand_landmarks:
        for idx, hand_landmarks in enumerate(res_hands.multi_hand_landmarks):
            info_mao = res_hands.multi_handedness[idx].classification[0].label
            
            # Coordenada da ponta do indicador para o botão REC
            p8 = hand_landmarks.landmark[8]
            ix, iy = int(p8.x * LARGURA_MONITOR), int(p8.y * ALTURA_MONITOR)
            ponto_indicador = (ix, iy)

            if info_mao == "Right":
                p4 = hand_landmarks.landmark[4]
                distancia = np.hypot(p4.x - p8.x, p4.y - p8.y)
                if distancia < 0.03: pinch_mao_direita = True

            mp_draw.draw_landmarks(canvas, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                mp_draw.DrawingSpec(color=BRANCO_PURO, thickness=2, circle_radius=2),
                mp_draw.DrawingSpec(color=AZUL_PYTHON if info_mao == "Left" else AMARELO_PYTHON, thickness=3))
            
            dedos = contar_dedos_pt(hand_landmarks.landmark, info_mao)
            total = dedos.count(True)
            total_dedos = max(total_dedos, total)
            
            pos_x_hud = 40 if info_mao == "Left" else LARGURA_MONITOR - 320
            desenhar_hud_vibrante(canvas, f"DADOS: {total}", total, info_mao, pos_x_hud, MODO_ROSTO_ATIVO)

    # --- LÓGICA DO BOTÃO VIRTUAL REC ---
    cor_botao = VERMELHO_REC if GRAVANDO else (100, 100, 100)
    cv2.circle(canvas, BOTAO_REC_POS, BOTAO_REC_RAIO, cor_botao, 2 if not GRAVANDO else -1)
    cv2.putText(canvas, "REC", (BOTAO_REC_POS[0]-18, BOTAO_REC_POS[1]+7), cv2.FONT_HERSHEY_SIMPLEX, 0.5, BRANCO_PURO, 2)

    if ponto_indicador:
        # Verifica se o indicador está dentro do botão
        dist_botao = np.hypot(ponto_indicador[0] - BOTAO_REC_POS[0], ponto_indicador[1] - BOTAO_REC_POS[1])
        if dist_botao < BOTAO_REC_RAIO and time.time() > COOLDOWN_BOTAO:
            GRAVANDO = not GRAVANDO
            COOLDOWN_BOTAO = time.time() + 2 # Espera 2 segundos para o próximo clique
            if GRAVANDO:
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                filename = f"fb_rec_{int(time.time())}.mp4"
                video_writer = cv2.VideoWriter(filename, fourcc, 20.0, (LARGURA_MONITOR, ALTURA_MONITOR))
            else:
                video_writer.release()

    if pinch_mao_direita and not ULTIMO_ESTADO_PINCH:
        MODO_ROSTO_ATIVO = not MODO_ROSTO_ATIVO
    ULTIMO_ESTADO_PINCH = pinch_mao_direita

    if MODO_ROSTO_ATIVO:
        res_face = face_mesh.process(rgb)
        if res_face.multi_face_landmarks:
            for face_landmarks in res_face.multi_face_landmarks:
                mp_draw.draw_landmarks(canvas, face_landmarks, mp_face_mesh.FACEMESH_TESSELATION,
                    None, mp_draw.DrawingSpec(color=VERDE_NEON, thickness=1))
                desenhar_contorno_olho(canvas, face_landmarks.landmark, OLHO_ESQ, ROXO_NEON)
                desenhar_contorno_olho(canvas, face_landmarks.landmark, OLHO_DIR, ROXO_NEON)
                for i in [468, 473]:
                    p = face_landmarks.landmark[i]
                    ix, iy = int(p.x * LARGURA_MONITOR), int(p.y * ALTURA_MONITOR)
                    cv2.circle(canvas, (ix, iy), 10, ROXO_NEON, 1)

    if arduino:
        arduino.write(str(min(total_dedos, 5)).encode())

    if GRAVANDO:
        video_writer.write(canvas)
        # Feedback visual piscante de gravação
        if int(time.time() * 2) % 2 == 0:
            cv2.putText(canvas, "LIVE REEL", (BOTAO_REC_POS[0] + 60, BOTAO_REC_POS[1] + 5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, VERMELHO_REC, 2)

    cv2.imshow(nome_janela, canvas)
    if cv2.waitKey(1) & 0xFF == 27: break

cap.release()
if video_writer: video_writer.release()
cv2.destroyAllWindows()
if arduino: arduino.close()