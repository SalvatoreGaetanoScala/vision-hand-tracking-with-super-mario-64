import cv2
import mediapipe as mp
import numpy as np
import time
import math
from pynput.keyboard import Controller, KeyCode

# --- 1. Configurazione Tastiera e Controlli ---
keyboard = Controller()

# Mappatura Tasti per Super Mario 64
KEY_UP = KeyCode.from_char('w')
KEY_DOWN = KeyCode.from_char('s')
KEY_LEFT = KeyCode.from_char('a')
KEY_RIGHT = KeyCode.from_char('d')
KEY_JUMP = KeyCode.from_char('p')   # Tasto A
KEY_PUNCH = KeyCode.from_char('o')  # Tasto B

# Variabili di stato
is_w_pressed = False
is_s_pressed = False
is_a_pressed = False
is_d_pressed = False
is_jump_pressed = False
is_punch_pressed = False

# --- 2. Inizializzazione e Setup ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=2, 
    min_detection_confidence=0.7, 
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils

# Estetica: Colore Giallo per scheletro e linee[span_4](start_span)[span_4](end_span)
landmark_style = mp_draw.DrawingSpec(color=(0, 255, 255), thickness=2, circle_radius=4)
connection_style = mp_draw.DrawingSpec(color=(0, 255, 255), thickness=2)

cap = cv2.VideoCapture(0)
window_name = "Mario 64 Hand Controller"
cv2.namedWindow(window_name)

pTime = 0

# --- 3. Funzioni di Supporto ---
def calculate_distance(p1, p2):
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def release_all_keys():
    global is_w_pressed, is_s_pressed, is_a_pressed, is_d_pressed, is_jump_pressed, is_punch_pressed
    keys_states = [
        (is_w_pressed, KEY_UP), (is_s_pressed, KEY_DOWN),
        (is_a_pressed, KEY_LEFT), (is_d_pressed, KEY_RIGHT),
        (is_jump_pressed, KEY_JUMP), (is_punch_pressed, KEY_PUNCH)
    ]
    for state, key in keys_states:
        if state: keyboard.release(key)
    
    is_w_pressed = is_s_pressed = is_a_pressed = is_d_pressed = False
    is_jump_pressed = is_punch_pressed = False

# --- 4. Loop Principale ---
while cap.isOpened():
    success, img = cap.read()
    if not success: 
        break
        
    img = cv2.flip(img, 1)
    h, w, _ = img.shape
    
    # Linea di divisione dello schermo[span_5](start_span)[span_5](end_span)
    cv2.line(img, (w // 2, 0), (w // 2, h), (100, 100, 100), 2)
    
    # Disegna la "Zona Morta" del Joystick Virtuale a sinistra
    cx_box, cy_box = w // 4, h // 2
    box_size = 60
    cv2.rectangle(img, (cx_box - box_size, cy_box - box_size), (cx_box + box_size, cy_box + box_size), (0, 255, 0), 2)
    cv2.putText(img, "JOYSTICK", (cx_box - 45, cy_box - 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)
    
    action_text = "Fermo"
    jump_text = ""
    
    if not results.multi_hand_landmarks:
        release_all_keys()
    else:
        movement_active = False
        action_active = False
        
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            mp_draw.draw_landmarks(
                img, hand_landmarks, mp_hands.HAND_CONNECTIONS, 
                landmark_style, connection_style
            )
            
            # --- CALCOLO BOUNDING BOX E LABEL ESTETICA[span_6](start_span)[span_6](end_span) ---
            x_min, y_min = w, h
            x_max, y_max = 0, 0
            for lm in hand_landmarks.landmark:
                x, y = int(lm.x * w), int(lm.y * h)
                x_min, y_min = min(x_min, x), min(y_min, y)
                x_max, y_max = max(x_max, x), max(y_max, y)
            
            pad = 20
            x_min, y_min = max(0, x_min - pad), max(0, y_min - pad)
            x_max, y_max = min(w, x_max + pad), min(h, y_max + pad)
            cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (0, 0, 0), 1)
            
            label = results.multi_handedness[idx].classification[0].label
            display_label = "Right" if label == "Left" else "Left"
            cv2.rectangle(img, (x_min, y_min - 25), (x_min + 55, y_min), (0, 0, 0), cv2.FILLED)
            cv2.putText(img, display_label, (x_min + 5, y_min - 5), cv2.FONT_HERSHEY_PLAIN, 1.2, (255, 255, 255), 1)
            
            # Centro della mano (polso) per capire la zona[span_7](start_span)[span_7](end_span)
            wrist = hand_landmarks.landmark[0]
            cx = int(wrist.x * w)
            
            # --- ZONA SINISTRA (JOYSTICK ANALOGICO 3D) ---
            if cx < w // 2:
                movement_active = True
                # Usiamo la base del dito medio come "levetta"
                middle_mcp = hand_landmarks.landmark[9]
                hx, hy = int(middle_mcp.x * w), int(middle_mcp.y * h)
                
                # Disegna un pallino blu per far capire dove sta puntando il joystick
                cv2.circle(img, (hx, hy), 12, (255, 0, 0), cv2.FILLED)
                
                actions = []
                
                # Asse Y (Avanti / Indietro)
                if hy < cy_box - box_size:
                    actions.append("AVANTI")
                    if not is_w_pressed: keyboard.press(KEY_UP); is_w_pressed = True
                    if is_s_pressed: keyboard.release(KEY_DOWN); is_s_pressed = False
                elif hy > cy_box + box_size:
                    actions.append("INDIETRO")
                    if not is_s_pressed: keyboard.press(KEY_DOWN); is_s_pressed = True
                    if is_w_pressed: keyboard.release(KEY_UP); is_w_pressed = False
                else:
                    if is_w_pressed: keyboard.release(KEY_UP); is_w_pressed = False
                    if is_s_pressed: keyboard.release(KEY_DOWN); is_s_pressed = False

                # Asse X (Sinistra / Destra)
                if hx < cx_box - box_size:
                    actions.append("SX")
                    if not is_a_pressed: keyboard.press(KEY_LEFT); is_a_pressed = True
                    if is_d_pressed: keyboard.release(KEY_RIGHT); is_d_pressed = False
                elif hx > cx_box + box_size:
                    actions.append("DX")
                    if not is_d_pressed: keyboard.press(KEY_RIGHT); is_d_pressed = True
                    if is_a_pressed: keyboard.release(KEY_LEFT); is_a_pressed = False
                else:
                    if is_a_pressed: keyboard.release(KEY_LEFT); is_a_pressed = False
                    if is_d_pressed: keyboard.release(KEY_RIGHT); is_d_pressed = False

                if actions:
                    action_text = " + ".join(actions)

            # --- ZONA DESTRA (PULSANTI A e B) ---
            else:
                action_active = True
                thumb_tip = hand_landmarks.landmark[4]
                index_tip = hand_landmarks.landmark[8]
                middle_tip = hand_landmarks.landmark[12]
                
                tx, ty = int(thumb_tip.x * w), int(thumb_tip.y * h)
                ix, iy = int(index_tip.x * w), int(index_tip.y * h)
                mx, my = int(middle_tip.x * w), int(middle_tip.y * h)
                
                dist_jump = calculate_distance((tx, ty), (ix, iy))
                dist_punch = calculate_distance((tx, ty), (mx, my))
                
                # Logica Salto (Pizzico Pollice-Indice)
                if dist_jump < 40:
                    cv2.circle(img, ((tx + ix) // 2, (ty + iy) // 2), 15, (0, 0, 255), cv2.FILLED)
                    jump_text = "SALTO (A)!"
                    if not is_jump_pressed: keyboard.press(KEY_JUMP); is_jump_pressed = True
                else:
                    cv2.circle(img, ((tx + ix) // 2, (ty + iy) // 2), 15, (0, 255, 0), 2)
                    if is_jump_pressed: keyboard.release(KEY_JUMP); is_jump_pressed = False
                        
                # Logica Pugno (Pizzico Pollice-Medio)
                if dist_punch < 40 and dist_jump >= 40: # Evita di premerli entrambi per sbaglio
                    cv2.circle(img, ((tx + mx) // 2, (ty + my) // 2), 15, (255, 0, 0), cv2.FILLED)
                    jump_text = "PUGNO (B)!"
                    if not is_punch_pressed: keyboard.press(KEY_PUNCH); is_punch_pressed = True
                else:
                    cv2.circle(img, ((tx + mx) // 2, (ty + my) // 2), 15, (0, 255, 255), 2)
                    if is_punch_pressed: keyboard.release(KEY_PUNCH); is_punch_pressed = False

        # Rilasci di sicurezza[span_8](start_span)[span_8](end_span)
        if not movement_active:
            if is_w_pressed: keyboard.release(KEY_UP); is_w_pressed = False
            if is_s_pressed: keyboard.release(KEY_DOWN); is_s_pressed = False
            if is_a_pressed: keyboard.release(KEY_LEFT); is_a_pressed = False
            if is_d_pressed: keyboard.release(KEY_RIGHT); is_d_pressed = False
        if not action_active:
            if is_jump_pressed: keyboard.release(KEY_JUMP); is_jump_pressed = False
            if is_punch_pressed: keyboard.release(KEY_PUNCH); is_punch_pressed = False

    # --- Interfaccia Grafica FPS e Testo Azioni[span_9](start_span)[span_9](end_span) ---
    cTime = time.time()
    fps = 1 / (cTime - pTime) if (cTime - pTime) > 0 else 0
    pTime = cTime
    
    cv2.rectangle(img, (0, h - 60), (w, h), (0, 0, 0), cv2.FILLED)
    cv2.putText(img, f'FPS: {int(fps)}', (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(img, action_text, (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
    cv2.putText(img, jump_text, (w // 2 + 20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

    cv2.imshow(window_name, img)
    
    # --- Gestione Chiusura Pulita[span_10](start_span)[span_10](end_span) ---
    if cv2.waitKey(1) & 0xFF == ord('q'): 
        break
    try:
        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1: 
            break
    except cv2.error:
        break

# Spegnimento pulito
release_all_keys()
cap.release()
cv2.destroyAllWindows()
cv2.waitKey(1)