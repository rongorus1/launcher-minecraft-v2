from helpers.robust_network import activar_red_robusta

# Aplicar timeout y reintentos a todas las descargas ANTES de importar las vistas
activar_red_robusta()

from views.main_window import MainWindow

# Entry point
if __name__ == "__main__":
    root_window = MainWindow()
    root_window.run()
