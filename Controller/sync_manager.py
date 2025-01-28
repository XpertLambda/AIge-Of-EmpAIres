import os
import time
from Settings.setup import SAVE_DIRECTORY

TEMP_SAVE = "temp_sync.pkl"
TEMP_SAVE_PATH = os.path.join(SAVE_DIRECTORY, TEMP_SAVE)
MAX_RETRIES = 10  # Augmenté de 5 à 10
RETRY_DELAY = 0.2  # Augmenté de 0.1 à 0.2
FILE_WAIT_TIMEOUT = 2.0  # Nouveau timeout global

def wait_for_file(filepath, timeout=FILE_WAIT_TIMEOUT):
    """Attend que le fichier soit disponible et complet"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if os.path.exists(filepath):
            try:
                # Essaie d'ouvrir le fichier en lecture
                with open(filepath, 'rb') as f:
                    # Si on peut lire le fichier, il est prêt
                    return True
            except (IOError, PermissionError):
                # Fichier pas encore prêt
                time.sleep(RETRY_DELAY)
                continue
        time.sleep(RETRY_DELAY)
    return False

def save_for_sync(game_map):
    """Sauvegarde l'état pour synchro"""
    success = False
    for attempt in range(MAX_RETRIES):
        try:
            # Essayer de supprimer l'ancien fichier s'il existe
            if os.path.exists(TEMP_SAVE_PATH):
                try:
                    os.remove(TEMP_SAVE_PATH)
                    time.sleep(RETRY_DELAY)  # Attendre que la suppression soit effective
                except:
                    pass

            # Sauvegarder
            game_map.save_map(TEMP_SAVE_PATH)
            
            # Vérifier que le fichier est bien écrit
            if wait_for_file(TEMP_SAVE_PATH):
                success = True
                break
                
        except Exception as e:
            print(f"Attempt {attempt+1}/{MAX_RETRIES} - Error saving sync state: {e}")
            time.sleep(RETRY_DELAY)
            
    return success

def check_and_load_sync(game_map):
    """Vérifie et charge si une synchro est disponible"""
    if os.path.exists(TEMP_SAVE_PATH):
        # Attendre que le fichier soit complètement écrit
        if not wait_for_file(TEMP_SAVE_PATH):
            print("Timeout waiting for sync file to be ready")
            return False

        for attempt in range(MAX_RETRIES):
            try:
                # Garder quelques paramètres GUI
                old_gui_settings = {
                    'screen': game_map.game_state.get('screen'),
                    'screen_width': game_map.game_state.get('screen_width'),
                    'screen_height': game_map.game_state.get('screen_height'),
                    'camera': game_map.game_state.get('camera')
                } if game_map.game_state else {}

                # Chargement
                game_map.load_map(TEMP_SAVE_PATH)

                # Réinitialiser complètement old_resources avec les nouveaux joueurs
                if game_map.game_state:
                    game_map.game_state['old_resources'] = {
                        p.teamID: p.resources.copy() for p in game_map.players
                    }
                
                # Restaurer les paramètres GUI
                if old_gui_settings and game_map.game_state:
                    for key, value in old_gui_settings.items():
                        if value is not None:
                            game_map.game_state[key] = value
                
                time.sleep(RETRY_DELAY)
                
                try:
                    os.remove(TEMP_SAVE_PATH)
                except PermissionError:
                    print("Could not delete sync file - will retry next cycle")
                return True
                
            except PermissionError:
                print(f"Attempt {attempt+1}/{MAX_RETRIES} - File busy, retrying...")
                time.sleep(RETRY_DELAY)
            except Exception as e:
                print(f"Error loading sync state: {e}")
                try:
                    os.remove(TEMP_SAVE_PATH)
                except:
                    pass
                break
    return False
