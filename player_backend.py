"""
High-Performance GPU Video Backend using libmpv
Configured specifically for 8K 60fps hardware-accelerated decoding via NVIDIA RTX / D3D11VA / NVDEC.
"""

import os
import sys
import ctypes
from PySide6.QtCore import QObject, Signal, QTimer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if hasattr(os, 'add_dll_directory') and os.path.isdir(BASE_DIR):
    try:
        os.add_dll_directory(BASE_DIR)
    except Exception:
        pass
os.environ['PATH'] = BASE_DIR + os.pathsep + os.environ.get('PATH', '')

import mpv



class VRVideoBackend(QObject):
    file_loaded = Signal(dict)
    time_changed = Signal(float)
    duration_changed = Signal(float)
    playback_state_changed = Signal(bool)
    stats_updated = Signal(dict)
    frame_ready = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mpv_player = None
        self.render_ctx = None
        self.current_file = None
        self.is_paused = True
        self.duration = 0.0
        self.current_time = 0.0
        self.video_width = 0
        self.video_height = 0
        
        # Telemetry timer for smooth stats reporting
        self.telemetry_timer = QTimer(self)
        self.telemetry_timer.setInterval(250)
        self.telemetry_timer.timeout.connect(self._report_telemetry)

    def init_mpv(self, get_proc_address_cb):
        """Initializes MPV with the OpenGL render context."""
        try:
            self.mpv_player = mpv.MPV(
                hwdec='auto-safe',
                hwdec_codecs='all',
                vo='libmpv',
                gpu_api='opengl',
                video_sync='display-resample',
                interpolation=False,
                vd_lavc_threads=16,
                terminal=False,
                ytdl=False,
                keep_open='yes'
            )
            
            # Setup render context
            get_proc_addr_fn = mpv.MpvGlGetProcAddressFn(
                lambda ctx, name: get_proc_address_cb(name)
            )
            
            self.render_ctx = mpv.MpvRenderContext(
                self.mpv_player,
                'opengl',
                opengl_init_params={'get_proc_address': get_proc_addr_fn}
            )
            
            # Callback when a new video frame is ready to be presented
            self.render_ctx.update_cb = self._on_mpv_update
            
            # Property observers
            @self.mpv_player.property_observer('time-pos')
            def on_time_pos(_name, value):
                if value is not None:
                    self.current_time = value
                    self.time_changed.emit(value)

            @self.mpv_player.property_observer('duration')
            def on_duration(_name, value):
                if value is not None:
                    self.duration = value
                    self.duration_changed.emit(value)

            @self.mpv_player.property_observer('pause')
            def on_pause(_name, value):
                if value is not None:
                    self.is_paused = bool(value)
                    self.playback_state_changed.emit(not self.is_paused)

            @self.mpv_player.property_observer('width')
            def on_width(_name, value):
                if value:
                    self.video_width = value
                    self._check_file_info()

            @self.mpv_player.property_observer('height')
            def on_height(_name, value):
                if value:
                    self.video_height = value
                    self._check_file_info()

            self.telemetry_timer.start()
            return True
        except Exception as e:
            print("Failed to initialize MPV:", e)
            return False

    def _on_mpv_update(self):
        # Notify Qt main thread that a frame is ready
        self.frame_ready.emit()

    def _check_file_info(self):
        if self.video_width > 0 and self.video_height > 0:
            codec = getattr(self.mpv_player, 'video_codec', 'Unknown')
            hwdec = getattr(self.mpv_player, 'hwdec_current', 'none')
            fps = getattr(self.mpv_player, 'estimated_vf_fps', 60.0) or 60.0
            info = {
                'width': self.video_width,
                'height': self.video_height,
                'codec': codec,
                'hwdec': hwdec,
                'fps': fps,
                'duration': self.duration,
                'filename': os.path.basename(self.current_file) if self.current_file else "Unknown"
            }
            self.file_loaded.emit(info)

    def _report_telemetry(self):
        if not self.mpv_player:
            return
        try:
            hwdec = getattr(self.mpv_player, 'hwdec_current', 'none')
            codec = getattr(self.mpv_player, 'video_codec', '')
            fps = getattr(self.mpv_player, 'estimated_vf_fps', 0.0) or 0.0
            drops = getattr(self.mpv_player, 'frame_drop_count', 0) or 0
            bitrate = getattr(self.mpv_player, 'video_bitrate', 0) or 0
            
            stats = {
                'hwdec': hwdec,
                'codec': codec,
                'fps': fps,
                'drops': drops,
                'bitrate': bitrate,
                'width': self.video_width,
                'height': self.video_height
            }
            self.stats_updated.emit(stats)
        except Exception:
            pass

    def load_file(self, filepath):
        if not os.path.exists(filepath):
            print("File not found:", filepath)
            return False
        self.current_file = filepath
        self.mpv_player.play(filepath)
        self.mpv_player.pause = False
        return True

    def play(self):
        if self.mpv_player:
            self.mpv_player.pause = False

    def pause(self):
        if self.mpv_player:
            self.mpv_player.pause = True

    def toggle_play(self):
        if self.mpv_player:
            self.mpv_player.pause = not self.mpv_player.pause

    def seek(self, seconds, absolute=True):
        if self.mpv_player:
            mode = 'absolute' if absolute else 'relative'
            try:
                self.mpv_player.seek(seconds, mode)
            except Exception:
                pass

    def set_speed(self, speed):
        if self.mpv_player:
            self.mpv_player.speed = float(speed)

    def set_volume(self, vol):
        if self.mpv_player:
            self.mpv_player.volume = max(0, min(100, int(vol)))

    def set_loop(self, enabled):
        if self.mpv_player:
            self.mpv_player.loop = 'inf' if enabled else 'no'

    def render_frame_to_fbo(self, fbo_id, width, height, flip_y=False):
        if self.render_ctx:
            try:
                self.render_ctx.render(
                    opengl_fbo={'w': int(width), 'h': int(height), 'fbo': int(fbo_id)},
                    flip_y=flip_y
                )
                return True
            except Exception as e:
                # Can happen during resize or shutdown
                return False
        return False

    def cleanup(self):
        self.telemetry_timer.stop()
        if self.render_ctx:
            try:
                self.render_ctx.free()
            except Exception:
                pass
            self.render_ctx = None
        if self.mpv_player:
            try:
                self.mpv_player.terminate()
            except Exception:
                pass
            self.mpv_player = None
