import cv2
import mediapipe as mp
import time
import random

# --- CONFIGURAÇÃO ---
# Mantemos os nomes, mas inverteremos os índices no código
POSES = ["MAO DIREITA NO TOPO", "MAO ESQUERDA NO TOPO", "BRACOS ABERTOS"]
tempo_por_pose = 6.0  # Tempo mais generoso para ser acolhedor
intervalo_entre_poses = 1.5
score = 0
pose_atual = random.choice(POSES)
inicio_tempo = time.time()
frames_confirmacao = 0 
NECESSARIO_CONFIRMAR = 12 
em_intervalo = False
momento_acerto = 0

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(model_complexity=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, image = cap.read()
    if not success: break

    image = cv2.flip(image, 1) # Espelho para o usuário
    h, w, _ = image.shape
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)

    agora = time.time()

    if em_intervalo:
        cv2.putText(image, "PREPARE-SE...", (w//4, h//2), cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 255, 0), 2)
        if agora - momento_acerto > intervalo_entre_poses:
            em_intervalo = False
            pose_atual = random.choice(POSES)
            inicio_tempo = time.time()
            frames_confirmacao = 0
    else:
        tempo_restante = max(0, tempo_por_pose - (agora - inicio_tempo))

        if tempo_restante <= 0:
            score = max(0, score - 5)
            inicio_tempo = time.time()
            pose_atual = random.choice(POSES)

        if results.pose_landmarks:
            nariz = results.pose_landmarks.landmark[0]
            
            # --- AQUI ESTÁ A INVERSÃO SOLICITADA ---
            # Para o MediaPipe no modo espelho:
            # Sua mão DIREITA real é o landmark 15 (Left Hand no modelo)
            # Sua mão ESQUERDA real é o landmark 16 (Right Hand no modelo)
            mao_direita_usuario = results.pose_landmarks.landmark[15] 
            mao_esquerda_usuario = results.pose_landmarks.landmark[16]

            pose_correta = False
            if pose_atual == "MAO DIREITA NO TOPO" and mao_direita_usuario.y < nariz.y - 0.1:
                pose_correta = True
            elif pose_atual == "MAO ESQUERDA NO TOPO" and mao_esquerda_usuario.y < nariz.y - 0.1:
                pose_correta = True
            elif pose_atual == "BRACOS ABERTOS" and abs(mao_direita_usuario.x - mao_esquerda_usuario.x) > 0.7:
                pose_correta = True

            if pose_correta:
                frames_confirmacao += 1
            else:
                frames_confirmacao = max(0, frames_confirmacao - 1)

            if frames_confirmacao >= NECESSARIO_CONFIRMAR:
                score += 10
                em_intervalo = True
                momento_acerto = time.time()

            # Estilização: Remove rosto (0 a 10)
            for i in range(11): results.pose_landmarks.landmark[i].visibility = 0
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                     mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=4, circle_radius=4),
                                     mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=8))

        # UI Visual
        cv2.rectangle(image, (0, 0), (w, 100), (0,0,0), -1)
        cv2.putText(image, f"ORDEM: {pose_atual}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        # Barra de tempo amigável
        cv2.rectangle(image, (20, 60), (w-20, 75), (50, 50, 50), -1)
        w_barra = int((tempo_restante / tempo_por_pose) * (w - 40))
        cv2.rectangle(image, (20, 60), (20 + w_barra, 75), (0, 255, 0), -1)
        
        cv2.putText(image, f"PONTOS: {score}", (20, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    cv2.imshow('Simon Says - Corrigido', image)
    if cv2.waitKey(5) & 0xFF == 27: break

cap.release()
cv2.destroyAllWindows()