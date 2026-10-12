# src/controller/update_mods_controller.py
"""Controlador para actualización e instalación de modpacks."""
import os
import threading
from tkinter import messagebox

from components.progress_bar_generic import ProgressBarGeneric
from config import MINECRAFT_DIRECTORY
from helpers.archive_tools import extract_modpack
from helpers.file_dialog_tools import select_file_archive


def run_update_mods_controller(progress_bar: 'ProgressBarGeneric' = None):
    """Pide un .rar/.zip y lo instala en .minecraft (manifest + overrides)."""
    archive_path = select_file_archive()
    if not archive_path:
        return

    def instalar():
        def reportar_progreso(ratio: float):
            if progress_bar is not None:
                progress_bar.show_element_thread_safe()
                progress_bar.set_thread_safe(ratio)

        def reportar_estado(texto: str):
            if progress_bar is not None:
                progress_bar.show_element_thread_safe()
                progress_bar.set_status_thread_safe(texto)

        def _error(mensaje: str):
            import logging
            logging.getLogger().error(f"Actualizar mods: {mensaje}")
            master = progress_bar.master if progress_bar else None
            if master:
                master.after(0, lambda: messagebox.showerror("Actualizar mods", mensaje))

        # 1. Extraer modpack base (manifest.json + overrides/ fusionado en .minecraft)
        top_folders, error = extract_modpack(
            archive_path, MINECRAFT_DIRECTORY,
            progress_callback=reportar_progreso,
            status_callback=reportar_estado
        )

        if error:
            _error(error)
            return

        # 2. Si hay manifest.json, descargar dependencias externas (CurseForge)
        manifest_path = os.path.join(MINECRAFT_DIRECTORY, "manifest.json")
        if os.path.exists(manifest_path):
            def descargar_dependencias():
                try:
                    from helpers.config_curseforge import get_api_key
                    from helpers.curseforge_downloader import CurseForgeDownloader
                    
                    api_key = get_api_key()
                    if not api_key:
                        # Intentar variable de entorno
                        api_key = os.getenv("CURSEFORGE_API_KEY", "")
                    
                    if not api_key:
                        master = progress_bar.master if progress_bar else None
                        if master:
                            master.after(0, lambda: messagebox.showwarning(
                                "API Key faltante",
                                "Se requiere API Key de CurseForge para descargar dependencias externas.\n"
                                "Configura CURSEFORGE_API_KEY en variables de entorno o en curseforge_config.json\n\n"
                                "El modpack base ya se instaló, pero faltan dependencias externas."
                            ))
                        else:
                            # Sin UI, solo log
                            import logging
                            logging.getLogger().warning("API Key faltante, no se descargaron dependencias externas")
                        
                        # Avisar que el base se instaló aunque falten deps
                        master2 = progress_bar.master if progress_bar else None
                        if master2:
                            master.after(0, lambda: messagebox.showinfo(
                                "Modpack base instalado",
                                f"Se instalaron: {', '.join(top_folders) if top_folders else 'archivos'}\n"
                                "Faltan dependencias externas (requiere API Key)."
                            ))
                        return

                    # Validar la key contra la API antes de descargar cientos
                    # de mods: una key inválida daría un fallo por mod.
                    # (Si GitHub funcionó hace segundos, un fallo aquí es la key.)
                    reportar_estado("Verificando API key de CurseForge...")
                    try:
                        from helpers.curseforge_api import CurseForgeAPI
                        key_ok = CurseForgeAPI(api_key).validate_key()
                    except Exception as e:
                        import logging
                        logging.getLogger().warning(f"No se pudo validar la API key ({e}); se intenta descargar igual.")
                        key_ok = True
                    if not key_ok:
                        master = progress_bar.master if progress_bar else None
                        if master:
                            master.after(0, lambda: messagebox.showwarning(
                                "API Key inválida",
                                "La API Key de CurseForge fue rechazada (inválida, revocada o sin conexión).\n"
                                "Genera una nueva en console.curseforge.com y actualiza\n"
                                "CURSEFORGE_API_KEY o curseforge_config.json.\n\n"
                                "El modpack base ya se instaló, pero faltan dependencias externas."
                            ))
                        else:
                            import logging
                            logging.getLogger().warning("API Key inválida, no se descargaron dependencias externas")
                        return

                    downloader = CurseForgeDownloader(
                        api_key=api_key,
                        minecraft_dir=MINECRAFT_DIRECTORY
                    )

                    def progress_cb(actual, total):
                        if progress_bar:
                            # Progreso de dependencias: 0.5 a 1.0 (mitad superior)
                            ratio = 0.5 + (actual / total) * 0.5
                            progress_bar.set_thread_safe(ratio)

                    def status_cb(texto):
                        if progress_bar:
                            progress_bar.set_status_thread_safe(texto)

                    result = downloader.install_from_manifest(
                        manifest_path=manifest_path,
                        api_key=api_key,
                        progress_callback=progress_cb,
                        status_callback=status_cb
                    )

                    master = progress_bar.master if progress_bar else None
                    if not master:
                        return
                    
                    import logging
                    logging.getLogger().warning(
                        "Deps CurseForge: success=%s installed=%s skipped=%s failed=%s error=%s",
                        result.get("success"), result.get("installed", 0),
                        result.get("skipped", 0), len(result.get("failed", [])),
                        result.get("error", ""),
                    )
                    for f in result.get("failed", [])[:3]:
                        logging.getLogger().warning(
                            "Dep fallida: %s/%s: %s",
                            f.get("project_id"), f.get("file_id"), f.get("error"))

                    if not result.get("success"):
                        err = result.get("error", "Error desconocido")
                        master.after(0, lambda: messagebox.showerror("Error dependencias", err))
                    elif result.get("failed"):
                        msg = f"Instalados: {result.get('installed',0)}, Fallaron: {len(result['failed'])}\n" + "\n".join(
                            f"- {f['project_id']}/{f['file_id']}: {f['error']}"
                            for f in result['failed'][:5]
                        )
                        master.after(0, lambda: messagebox.showwarning("Algunos mods fallaron", msg))
                    else:
                        installed = result.get("installed", 0)
                        skipped = result.get("skipped", 0)
                        if installed > 0:
                            master.after(0, lambda: messagebox.showinfo(
                                "Modpack completo",
                                f"Instalado correctamente.\nDependencias: {installed} nuevas, {skipped} ya existían."
                            ))
                        else:
                            master.after(0, lambda: messagebox.showinfo(
                                "Modpack instalado",
                                f"Se instalaron: {', '.join(top_folders) if top_folders else 'archivos'}\nDependencias ya estaban instaladas."
                            ))
                except Exception as e:
                    import logging
                    import traceback
                    logging.getLogger().error(f"Error descargando dependencias: {e}\n{traceback.format_exc()}")
                    master = progress_bar.master if progress_bar else None
                    if master:
                        master.after(0, lambda: messagebox.showerror("Error", f"Error descargando dependencias: {e}"))

            threading.Thread(target=descargar_dependencias, daemon=True).start()
        else:
            # No hay manifest, solo avisar que terminó
            master = progress_bar.master if progress_bar else None
            if master:
                master.after(0, lambda: messagebox.showinfo(
                    "Modpack instalado", f"Se instalaron: {', '.join(top_folders) if top_folders else 'archivos'} correctamente."
                ))

    threading.Thread(target=instalar, daemon=True).start()
