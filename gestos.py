import cv2
import mediapipe as mp
import serial
import time
import numpy as np
import copy

# --- CONEXÃO SERIAL ---
try:
    arduino = serial.Serial('COM5', 9600, timeout=0.1)
    time.sleep(2)
except Exception:
    arduino = None

# --- CONFIGURAÇÃO VISUAL (LIGHT MODE) ---
FUNDO_OFF_WHITE = (248, 249, 250)
SUPERFICIE_BRANCA = (255, 255, 255)
TEXTO_DARK = (45, 41, 38)
BORDA_SUAVE = (220, 220, 220)

# Mantendo as cores originais das mãos para o rastreio
AZUL_PYTHON = (255, 150, 50)
AMARELO_PYTHON = (0, 255, 255)
BRANCO_PURO = (255, 255, 255)

# --- CONFIGURAÇÃO MEDIAPIPE ---
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.8)

cap = cv2.VideoCapture(0)

nome_janela = "Wandi Vision"
cv2.namedWindow(nome_janela, cv2.WINDOW_NORMAL)
cv2.setWindowProperty(nome_janela, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break

    frame = cv2.flip(frame, 1)
    h_frame, w_frame, _ = frame.shape
    
    try:
        _, _, screen_w, screen_h = cv2.getWindowImageRect(nome_janela)
    except:
        screen_w, screen_h = 1920, 1080

    # --- CANVAS DE FUNDO (LIGHT MODE) ---
    canvas = np.full((screen_h, screen_w, 3), FUNDO_OFF_WHITE, dtype=np.uint8)

    # --- DIMENSIONAMENTO ---
    espaco_titulo = int(screen_h * 0.10)
    margem = 20
    area_util_w = screen_w - (margem * 2)
    area_util_h = screen_h - espaco_titulo - margem

    escala = min(area_util_w / w_frame, area_util_h / h_frame)
    novo_w, novo_h = int(w_frame * escala), int(h_frame * escala)
    video_res = cv2.resize(frame, (novo_w, novo_h))

    x_offset = (screen_w - novo_w) // 2
    y_offset = espaco_titulo + (area_util_h - novo_h) // 2

    # --- ESTÉTICA DO PAINEL ---
    # Card de fundo do vídeo
    cv2.rectangle(canvas, (x_offset - 5, y_offset - 5), (x_offset + novo_w + 5, y_offset + novo_h + 5), SUPERFICIE_BRANCA, -1)
    cv2.rectangle(canvas, (x_offset - 5, y_offset - 5), (x_offset + novo_w + 5, y_offset + novo_h + 5), BORDA_SUAVE, 1)
    
    # Inserção do vídeo
    canvas[y_offset:y_offset+novo_h, x_offset:x_offset+novo_w] = video_res

    # Título
    font = cv2.FONT_HERSHEY_DUPLEX
    texto = "Wandi Vision - Painel De Controle"
    escala_fonte = screen_w / 1600
    tamanho_texto = cv2.getTextSize(texto, font, escala_fonte, 2)[0]
    cv2.putText(canvas, texto, ((screen_w - tamanho_texto[0]) // 2, int(espaco_titulo * 0.7)), 
                font, escala_fonte, TEXTO_DARK, 2, cv2.LINE_AA)

    # --- PROCESSAMENTO MEDIAPIPE ---
    rgb = cv2.cvtColor(video_res, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for idx, hand_landmarks in enumerate(result.multi_hand_landmarks):
            info_mao = result.multi_handedness[idx].classification[0].label
            # Retornando ao estilo de cores anterior
            cor_mao = AZUL_PYTHON if info_mao == "Left" else AMARELO_PYTHON
            
            # Deepcopy para não alterar o objeto original durante o mapeamento
            hl_mapeada = copy.deepcopy(hand_landmarks)
            for lm in hl_mapeada.landmark:
                lm.x = (lm.x * novo_w + x_offset) / screen_w
                lm.y = (lm.y * novo_h + y_offset) / screen_h

            # MANTENDO O ESTILO ANTERIOR:
            mp_draw.draw_landmarks(
                canvas, hl_mapeada, mp_hands.HAND_CONNECTIONS,
                mp_draw.DrawingSpec(color=BRANCO_PURO, thickness=2, circle_radius=2), # Pontos brancos
                mp_draw.DrawingSpec(color=cor_mao, thickness=4)                      # Conexões coloridas
            )

    # --- LOGICA DE SAÍDA ---
    key = cv2.waitKey(1) & 0xFF
    if key == 27:
        if cv2.getWindowProperty(nome_janela, cv2.WND_PROP_FULLSCREEN) == cv2.WINDOW_FULLSCREEN:
            cv2.setWindowProperty(nome_janela, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
        else:
            break

    cv2.imshow(nome_janela, canvas)

cap.release()
cv2.destroyAllWindows()
if arduino: arduino.close()