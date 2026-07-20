import os
import sys
import time
import json as _json

from PySide6.QtWidgets import QMainWindow, QLabel, QMessageBox, QFileDialog
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings, QWebEngineDownloadRequest
from PySide6.QtCore import QUrl, QSettings, QSize, QTimer
from PySide6.QtGui import QIcon

from ui.splash import draw_icon_badge
from PySide6.QtGui import QPixmap, QPainter, QColor


def _html_path() -> str:
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(base, "GeoCim.html")


def _make_app_icon() -> QIcon:
    ico_path = os.path.join(
        getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(__file__))),
        "GeoCim.ico"
    )
    if os.path.exists(ico_path):
        return QIcon(ico_path)

    sizes = [16, 32, 48, 64, 128, 256]
    icon = QIcon()
    for s in sizes:
        pm = QPixmap(s, s)
        pm.fill(QColor(0, 0, 0, 0))
        p = QPainter(pm)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        draw_icon_badge(p, cx=s // 2, cy=s // 2, size=s)
        p.end()
        icon.addPixmap(pm)
    return icon


class VentanaPrincipal(QMainWindow):
    def __init__(self, splash=None, open_path=None):
        super().__init__()
        self._splash = splash
        self._open_path = open_path
        self._load_done = False
        self._close_confirmed = False   # True cuando ya se resolvió el diálogo de cierre
        self._current_path = open_path  # ruta del .gcm en disco (None si nunca se ha guardado)

        self.setWindowTitle("GeoCim · Suite de Cimentaciones")
        self.setWindowIcon(_make_app_icon())
        self.setMinimumSize(1180, 680)
        self._restore_geometry()
        self._setup_webview()
        self._setup_statusbar()
        self._setup_autosave()

        QTimer.singleShot(10_000, self._open_window)

    # ------------------------------------------------------------------
    def _setup_webview(self):
        self.browser = QWebEngineView(self)

        s = self.browser.settings()
        s.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        s.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        s.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, False)

        # Interceptar descargas (Guardar proyecto desde JS)
        self.browser.page().profile().downloadRequested.connect(
            self._on_download_requested
        )

        self.browser.loadFinished.connect(self._on_load_finished)

        path = _html_path()
        if os.path.exists(path):
            self.browser.load(QUrl.fromLocalFile(path))
        else:
            self.browser.setHtml(
                f"<h2 style='font-family:monospace;color:#d4453b'>"
                f"No se encontró GeoCim.html en:<br>{path}</h2>"
            )
            self._open_window()

        self.setCentralWidget(self.browser)

    def _on_load_finished(self, _ok: bool):
        if self._open_path:
            self._load_project_file()
        QTimer.singleShot(350, self._open_window)

    def _load_project_file(self):
        """Carga un .gcm/.json pasado por línea de comandos (doble clic en Explorer)."""
        try:
            with open(self._open_path, "r", encoding="utf-8") as f:
                data = f.read()
        except OSError:
            return
        self.browser.page().runJavaScript(f"loadJsonString({_json.dumps(data)})")

    def _open_window(self):
        if self._load_done:
            return
        self._load_done = True
        if self._splash:
            self._splash.finish(self)
            self._splash = None
        self.show()
        self.raise_()
        self.activateWindow()

    # ------------------------------------------------------------------
    # Descarga de archivos (Guardar proyecto — JS crea blob URL)
    # ------------------------------------------------------------------
    def _on_download_requested(self, download: QWebEngineDownloadRequest):
        suggested = download.suggestedFileName() or "proyecto.gcm"
        # Aseguramos extensión .gcm
        if not suggested.endswith((".gcm", ".json")):
            suggested += ".gcm"

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar proyecto GeoCim",
            suggested,
            "Proyectos GeoCim (*.gcm);;JSON (*.json)",
        )
        if path:
            download.setDownloadDirectory(os.path.dirname(path) or ".")
            download.setDownloadFileName(os.path.basename(path))
            download.accept()
            self._current_path = path
        else:
            download.cancel()

    # ------------------------------------------------------------------
    # Autoguardado — pregunta a la página cada cierto tiempo si toca guardar
    # (el intervalo y el on/off los decide el JS según state.config.autosave)
    # ------------------------------------------------------------------
    def _setup_autosave(self):
        self._autosave_timer = QTimer(self)
        self._autosave_timer.timeout.connect(self._autosave_tick)
        self._autosave_timer.start(30_000)  # sondeo cada 30s; el JS decide si ya toca

    def _autosave_tick(self):
        if not self._load_done:
            return
        self.browser.page().runJavaScript("_autosaveCheck()", self._on_autosave_result)

    def _on_autosave_result(self, json_data):
        if not json_data or not self._current_path:
            return
        try:
            with open(self._current_path, "w", encoding="utf-8") as f:
                f.write(json_data)
        except OSError:
            return
        self.statusBar().showMessage(
            f"Autoguardado · {time.strftime('%H:%M:%S')}", 4000
        )

    # ------------------------------------------------------------------
    # Cierre de ventana — preguntar si guardar
    # ------------------------------------------------------------------
    def closeEvent(self, event):
        # Guardar geometría siempre
        cfg = QSettings("GeoCim", "Ventana")
        cfg.setValue("size", self.size())
        cfg.setValue("pos", self.pos())

        if self._close_confirmed:
            super().closeEvent(event)
            return

        mb = QMessageBox(self)
        mb.setWindowTitle("GeoCim — Cerrar aplicación")
        mb.setText("¿Deseas guardar el proyecto antes de salir?")
        mb.setInformativeText(
            "Los datos del proyecto se perderán si cierras sin guardar."
        )
        mb.setIcon(QMessageBox.Icon.Question)
        btn_save   = mb.addButton("Guardar",     QMessageBox.ButtonRole.AcceptRole)
        btn_no     = mb.addButton("No guardar",  QMessageBox.ButtonRole.DestructiveRole)
        btn_cancel = mb.addButton("Cancelar",    QMessageBox.ButtonRole.RejectRole)
        mb.setDefaultButton(btn_save)
        mb.exec()

        clicked = mb.clickedButton()

        if clicked == btn_cancel:
            event.ignore()

        elif clicked == btn_no:
            self._close_confirmed = True
            event.accept()

        else:  # Guardar
            event.ignore()
            # Pedimos los datos al JS y luego abrimos el diálogo nativo
            self.browser.page().runJavaScript(
                "menuGuardarData()",
                self._save_then_close,
            )

    def _save_then_close(self, json_data: str):
        """Callback de runJavaScript('menuGuardarData()'). Guarda y cierra."""
        saved = False
        if json_data:
            nombre = "proyecto"
            try:
                d = _json.loads(json_data)
                proyecto = d.get("state", {}).get("proyecto", {})
                nombre = proyecto.get("assetNumber") or proyecto.get("assetName") or "proyecto"
            except Exception:
                pass
            nombre = nombre.replace(" ", "_").replace("/", "-") + ".gcm"

            path, _ = QFileDialog.getSaveFileName(
                self,
                "Guardar proyecto GeoCim",
                nombre,
                "Proyectos GeoCim (*.gcm);;JSON (*.json)",
            )
            if path:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(json_data)
                self._current_path = path
                saved = True

        if saved:
            self._close_confirmed = True
            self.close()  # vuelve a llamar closeEvent con _close_confirmed=True
        # Si canceló el diálogo de archivo, la ventana permanece abierta

    # ------------------------------------------------------------------
    def _setup_statusbar(self):
        sb = self.statusBar()
        sb.addPermanentWidget(
            QLabel("GeoCim V1.0  ·  Ing. Juan C. Espinosa López  ·  Motor: Python + Claude")
        )

    # ------------------------------------------------------------------
    def _restore_geometry(self):
        cfg = QSettings("GeoCim", "Ventana")
        self.resize(cfg.value("size", QSize(1440, 900)))
        pos = cfg.value("pos", None)
        if pos is not None:
            self.move(pos)
