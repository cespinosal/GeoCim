"""
GeoCim — Suite de Cimentaciones
Entrada principal de la aplicación.
"""
import sys
import traceback

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt

from ui.splash import SplashGeoCim
from ui.ventana_principal import VentanaPrincipal
from ui.tema import get_stylesheet


def _exception_hook(exc_type, exc_value, exc_tb):
    msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    box = QMessageBox()
    box.setWindowTitle("Error inesperado — GeoCim")
    box.setIcon(QMessageBox.Icon.Critical)
    box.setText(f"<pre style='font-family:monospace;font-size:11px'>{msg}</pre>")
    box.exec()
    sys.__excepthook__(exc_type, exc_value, exc_tb)


def main():
    sys.excepthook = _exception_hook

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("GeoCim")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Ing. Juan C. Espinosa López")
    app.setStyleSheet(get_stylesheet())

    # Mostrar splash solo, la ventana principal NO se muestra aquí.
    # VentanaPrincipal se muestra a sí misma cuando el HTML termina de cargar.
    splash = SplashGeoCim()
    splash.show()
    app.processEvents()

    ventana = VentanaPrincipal(splash=splash)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
