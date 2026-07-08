import os
import sys
import hashlib
import requests
import json


class Updater:
    def __init__(self, server_url):
        self.server_url = f"{server_url}/api/update"
        # Directorio raíz: al correr como exe congelado, es la carpeta del exe;
        # en modo fuente, es la raíz del proyecto.
        if getattr(sys, 'frozen', False):
            self.root_dir = os.path.dirname(sys.executable)
        else:
            self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # ─────────────────────────────────────────────────────────
    # PUNTO DE ENTRADA PRINCIPAL
    # ─────────────────────────────────────────────────────────

    def check_and_update(self, status_callback=None):
        """Compara versión y archivos con el servidor y aplica parches.

        Retorna (success: bool, message: str) donde message puede ser:
          ALREADY_UP_TO_DATE|<version>
          MINOR_UPDATE_APPLIED|<version>   ← sólo en modo fuente
          EXE_UPDATE_PENDING|<version>     ← sólo en modo exe congelado
          MAJOR_UPDATE_REQUIRED|<version>
          Error …
        """
        if status_callback:
            status_callback("Buscando actualizaciones...")

        try:
            from settings import GAME_VERSION
            r = requests.get(f"{self.server_url}/check", timeout=3)
            if r.status_code != 200:
                return False, "Error al conectar con el servidor de actualizaciones."

            try:
                data = r.json()
            except (ValueError, Exception):
                return False, "Respuesta inválida del servidor de actualizaciones."

            manifest        = data.get("manifest", {})
            srv_version     = data.get("version", GAME_VERSION)
            update_type     = data.get("update_type", "minor")

            # ── Actualización mayor obligatoria ──────────────────────
            if srv_version != GAME_VERSION and update_type == "major":
                return False, f"MAJOR_UPDATE_REQUIRED|{srv_version}"

            # ── Modo exe congelado: actualizar el binario completo ────
            if getattr(sys, 'frozen', False):
                return self._check_exe_update(status_callback, srv_version)

            # ── Modo fuente: actualizar archivos individuales ─────────
            return self._check_files_update(manifest, srv_version, status_callback)

        except Exception as e:
            return False, f"Error en auto-update: {e}"

    # ─────────────────────────────────────────────────────────
    # ACTUALIZACIÓN DE ARCHIVOS (modo fuente)
    # ─────────────────────────────────────────────────────────

    def _check_files_update(self, manifest, srv_version, status_callback):
        updated_count = 0
        for rel_path, srv_hash in manifest.items():
            local_path = os.path.join(self.root_dir, rel_path)
            needs_update = False

            if not os.path.exists(local_path):
                needs_update = True
            else:
                with open(local_path, "rb") as f:
                    local_hash = hashlib.md5(f.read()).hexdigest()
                if local_hash != srv_hash:
                    needs_update = True

            if needs_update:
                if status_callback:
                    status_callback(f"Descargando parche: {rel_path}...")
                self._download_file(rel_path)
                updated_count += 1

        if updated_count > 0:
            return True, f"MINOR_UPDATE_APPLIED|{srv_version}"
        return True, f"ALREADY_UP_TO_DATE|{srv_version}"

    def _download_file(self, rel_path):
        """Descarga un archivo del servidor y lo guarda localmente."""
        url = f"{self.server_url}/download/{rel_path}"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            local_path = os.path.join(self.root_dir, rel_path)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, "wb") as f:
                f.write(r.content)
            return True
        return False

    # ─────────────────────────────────────────────────────────
    # ACTUALIZACIÓN DEL EJECUTABLE (modo congelado)
    # ─────────────────────────────────────────────────────────

    def _check_exe_update(self, status_callback, srv_version):
        """Compara el hash MD5 del exe actual con el del servidor.
        Si son distintos, descarga el nuevo exe como '_update.exe'
        y devuelve EXE_UPDATE_PENDING para que loading.py salga con código 99.
        """
        try:
            # Obtener info del exe en el servidor
            r = requests.get(f"{self.server_url}/exe_info", timeout=5)
            if r.status_code != 200:
                # Sin endpoint de exe → ya estamos al día desde la perspectiva del servidor
                return True, f"ALREADY_UP_TO_DATE|{srv_version}"

            srv_data     = r.json()
            srv_exe_hash = srv_data.get("md5", "")

            if not srv_exe_hash:
                return True, f"ALREADY_UP_TO_DATE|{srv_version}"

            # Hash del exe actual
            exe_path = sys.executable
            if status_callback:
                status_callback("Verificando versión del ejecutable...")
            with open(exe_path, "rb") as f:
                local_hash = hashlib.md5(f.read()).hexdigest()

            if local_hash == srv_exe_hash:
                return True, f"ALREADY_UP_TO_DATE|{srv_version}"

            # ── Hay una versión nueva: descargar ──────────────────────
            exe_dir     = os.path.dirname(exe_path)
            update_path = os.path.join(exe_dir, "_NeoFutbolArcade_update.exe")

            if status_callback:
                status_callback("Descargando nueva versión del juego (0%)...")

            resp = requests.get(
                f"{self.server_url}/download_exe",
                timeout=300,
                stream=True
            )
            if resp.status_code != 200:
                return False, f"Error al descargar actualización: HTTP {resp.status_code}"

            total      = int(resp.headers.get("content-length", 0))
            downloaded = 0

            with open(update_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total and status_callback:
                            pct = int(downloaded * 100 / total)
                            status_callback(f"Descargando nueva versión... {pct}%")

            # Verificar integridad del archivo descargado
            with open(update_path, "rb") as f:
                dl_hash = hashlib.md5(f.read()).hexdigest()

            if dl_hash != srv_exe_hash:
                os.remove(update_path)
                return False, "Error de integridad en la descarga. Intentar de nuevo."

            # Escribir bat de actualización automática (se ejecuta DESPUÉS de que el exe cierre)
            self._write_update_bat(exe_path, update_path)

            return True, f"EXE_UPDATE_PENDING|{srv_version}"

        except Exception as e:
            return False, f"Error al verificar exe: {e}"

    def _write_update_bat(self, exe_path, update_path):
        """Escribe un script .bat que espera a que el juego cierre y luego lo reemplaza."""
        exe_dir  = os.path.dirname(exe_path)
        exe_name = os.path.basename(exe_path)
        bat_path = os.path.join(exe_dir, "_apply_update.bat")

        # El bat espera 2 s, reemplaza el exe y se borra a sí mismo
        bat_content = (
            "@echo off\n"
            "timeout /t 2 /nobreak >nul\n"
            f"del /f \"{exe_path}\"\n"
            f"rename \"{update_path}\" \"{exe_name}\"\n"
            f"start \"\" \"{exe_path}\"\n"
            f"del /f \"{bat_path}\"\n"
        )
        with open(bat_path, "w", encoding="utf-8") as f:
            f.write(bat_content)
