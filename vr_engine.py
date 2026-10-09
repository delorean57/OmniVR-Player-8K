"""
VR OpenGL Rendering Engine & Interactive 360/180 Viewport
Handles GPU offscreen FBO allocation, GLSL shader compilation,
and smooth mouse/gyro camera navigation with damping and inertia.
"""

import math
import numpy as np
import ctypes
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtCore import Qt, QPointF, QTimer, Signal, QByteArray
from PySide6.QtGui import QOpenGLContext, QCursor
from OpenGL import GL

from vr_shader import VERTEX_SHADER, FRAGMENT_SHADER


class VRGLWidget(QOpenGLWidget):
    camera_changed = Signal(float, float, float, float)  # yaw, pitch, roll, fov (degrees)
    fps_rendered = Signal(float)

    # Projections
    PROJ_RECTILINEAR = 0
    PROJ_PANINI = 1
    PROJ_FISHEYE = 2
    PROJ_LITTLE_PLANET = 3
    PROJ_SPHERICAL_360 = 4

    # Stereo Modes
    STEREO_MONO = 0
    STEREO_VR180_SBS_LEFT = 1
    STEREO_VR180_SBS_RIGHT = 2
    STEREO_VR180_SBS_DUAL = 3
    STEREO_VR180_SBS_INVERTED = 4
    STEREO_360_SBS_LEFT = 5
    STEREO_360_SBS_RIGHT = 6
    STEREO_360_SBS_DUAL = 7
    STEREO_360_SBS_INVERTED = 8
    STEREO_360_OU_TOP = 9
    STEREO_360_OU_BOTTOM = 10
    STEREO_360_OU_DUAL = 11
    STEREO_360_OU_INVERTED = 12

    # Quality modes
    QUALITY_NATIVE_8K = 0
    QUALITY_ULTRA_4K = 1
    QUALITY_ADAPTIVE = 2

    def __init__(self, backend, parent=None):
        super().__init__(parent)
        self.backend = backend
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)

        # Camera state (in radians)
        self.yaw = 0.0
        self.pitch = 0.0
        self.roll = 0.0
        self.fov = math.radians(90.0)

        # Smooth inertia / velocity
        self.vel_yaw = 0.0
        self.vel_pitch = 0.0
        self.vel_roll = 0.0
        self.target_yaw = 0.0
        self.target_pitch = 0.0
        self.target_roll = 0.0
        self.target_fov = math.radians(90.0)
        self.is_recentering = False

        # Settings
        self.projection_mode = self.PROJ_RECTILINEAR
        self.stereo_mode = self.STEREO_MONO
        self.quality_mode = self.QUALITY_NATIVE_8K
        self.auto_orbit = False
        self.flip_x = 0
        self.flip_y = 0
        self.invert_x = False
        self.invert_y = False
        self.dome_fov = math.radians(180.0)
        self.lens_model = 0  # 0: Equirrectangular Domo, 1: Ojo de Pez Circular (Canon RF 5.2mm / Dual Fisheye)

        # Mouse interaction
        self.last_mouse_pos = QPointF()
        self.is_dragging_left = False
        self.is_dragging_right = False

        # OpenGL objects
        self.shader_prog = None
        self.fbo = 0
        self.fbo_texture = 0
        self.fbo_width = 7680
        self.fbo_height = 3840
        self.vao = 0
        self.vbo = 0

        # Animation timer for inertia and auto-orbit (60-120 FPS refresh)
        self.anim_timer = QTimer(self)
        self.anim_timer.setInterval(16)
        self.anim_timer.timeout.connect(self._on_anim_tick)
        self.anim_timer.start()

        # Connect backend frame update
        self.backend.frame_ready.connect(self.update)
        self.backend.file_loaded.connect(self._on_file_loaded)

        # Render performance tracking
        self.frame_count = 0
        self.last_fps_time = 0
        self.measured_fps = 60.0

    def initializeGL(self):
        ctx = QOpenGLContext.currentContext()
        print("Initializing VRGLWidget with OpenGL context:", ctx.isValid())

        # Compile Shader Program
        vs = GL.glCreateShader(GL.GL_VERTEX_SHADER)
        GL.glShaderSource(vs, VERTEX_SHADER)
        GL.glCompileShader(vs)
        if not GL.glGetShaderiv(vs, GL.GL_COMPILE_STATUS):
            print("VS Error:", GL.glGetShaderInfoLog(vs))

        fs = GL.glCreateShader(GL.GL_FRAGMENT_SHADER)
        GL.glShaderSource(fs, FRAGMENT_SHADER)
        GL.glCompileShader(fs)
        if not GL.glGetShaderiv(fs, GL.GL_COMPILE_STATUS):
            print("FS Error:", GL.glGetShaderInfoLog(fs))

        self.shader_prog = GL.glCreateProgram()
        GL.glAttachShader(self.shader_prog, vs)
        GL.glAttachShader(self.shader_prog, fs)
        GL.glLinkProgram(self.shader_prog)
        if not GL.glGetProgramiv(self.shader_prog, GL.GL_LINK_STATUS):
            print("Program Link Error:", GL.glGetProgramInfoLog(self.shader_prog))

        GL.glDeleteShader(vs)
        GL.glDeleteShader(fs)

        # Screen-aligned full Quad geometry (NDC coords + UV)
        quad_vertices = np.array([
            # pos(x,y)   uv(u,v)
            -1.0, -1.0,  0.0, 0.0,
             1.0, -1.0,  1.0, 0.0,
             1.0,  1.0,  1.0, 1.0,
            -1.0, -1.0,  0.0, 0.0,
             1.0,  1.0,  1.0, 1.0,
            -1.0,  1.0,  0.0, 1.0
        ], dtype=np.float32)

        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)

        self.vbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, quad_vertices.nbytes, quad_vertices, GL.GL_STATIC_DRAW)

        # a_pos (location 0)
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, 2, GL.GL_FLOAT, GL.GL_FALSE, 4 * 4, ctypes.c_void_p(0))

        # a_texcoord (location 1)
        GL.glEnableVertexAttribArray(1)
        GL.glVertexAttribPointer(1, 2, GL.GL_FLOAT, GL.GL_FALSE, 4 * 4, ctypes.c_void_p(2 * 4))

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

        # Initialize MPV render context with proc address loader
        def get_proc_address(name):
            res = ctx.getProcAddress(QByteArray(name))
            return ctypes.cast(res, ctypes.c_void_p).value if res else None

        self.backend.init_mpv(get_proc_address)

        # Allocate initial FBO
        self._reallocate_fbo(self.fbo_width, self.fbo_height)

    def _reallocate_fbo(self, width, height):
        self.makeCurrent()
        if self.fbo:
            GL.glDeleteFramebuffers(1, [self.fbo])
            self.fbo = 0
        if self.fbo_texture:
            GL.glDeleteTextures([self.fbo_texture])
            self.fbo_texture = 0

        self.fbo_width = max(640, int(width))
        self.fbo_height = max(360, int(height))

        # Create texture
        self.fbo_texture = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.fbo_texture)
        GL.glTexImage2D(
            GL.GL_TEXTURE_2D, 0, GL.GL_RGBA8,
            self.fbo_width, self.fbo_height, 0,
            GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, None
        )
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_REPEAT)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)

        # Create FBO
        self.fbo = GL.glGenFramebuffers(1)
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.fbo)
        GL.glFramebufferTexture2D(
            GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0,
            GL.GL_TEXTURE_2D, self.fbo_texture, 0
        )
        status = GL.glCheckFramebufferStatus(GL.GL_FRAMEBUFFER)
        if status != GL.GL_FRAMEBUFFER_COMPLETE:
            print("Warning: FBO is not complete, status:", status)

        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.defaultFramebufferObject())

    def _on_file_loaded(self, info):
        vid_w = info.get('width', 7680)
        vid_h = info.get('height', 3840)
        
        # Decide FBO dimensions based on quality mode
        if self.quality_mode == self.QUALITY_NATIVE_8K:
            self._reallocate_fbo(vid_w, vid_h)
        elif self.quality_mode == self.QUALITY_ULTRA_4K:
            self._reallocate_fbo(min(vid_w, 3840), min(vid_h, 1920))
        else: # Adaptive
            self._reallocate_fbo(self.width() * 2, self.height() * 2)

    def set_quality_mode(self, mode):
        self.quality_mode = mode
        if self.backend.video_width > 0:
            self._on_file_loaded({
                'width': self.backend.video_width,
                'height': self.backend.video_height
            })
        self.update()

    def set_projection(self, proj):
        self.projection_mode = proj
        # Default FOVs tuned for each projection
        if proj == self.PROJ_LITTLE_PLANET:
            self.target_fov = math.radians(220.0)
            self.fov = self.target_fov
        elif proj == self.PROJ_FISHEYE:
            self.target_fov = math.radians(140.0)
            self.fov = self.target_fov
        elif proj == self.PROJ_PANINI:
            self.target_fov = math.radians(110.0)
            self.fov = self.target_fov
        else:
            self.target_fov = math.radians(90.0)
            self.fov = self.target_fov
        self.update()
        self._emit_camera_changed()

    def set_stereo_mode(self, mode):
        self.stereo_mode = mode
        self.update()

    def toggle_auto_orbit(self):
        self.auto_orbit = not self.auto_orbit
        return self.auto_orbit

    def set_invert_x(self, inverted):
        self.invert_x = bool(inverted)

    def set_invert_y(self, inverted):
        self.invert_y = bool(inverted)

    def toggle_invert_x(self):
        self.invert_x = not self.invert_x
        return self.invert_x

    def toggle_invert_y(self):
        self.invert_y = not self.invert_y
        return self.invert_y

    def set_invert_axes(self, inverted):
        self.invert_x = bool(inverted)
        self.invert_y = bool(inverted)

    def toggle_invert_axes(self):
        new_val = not (self.invert_x and self.invert_y)
        self.invert_x = new_val
        self.invert_y = new_val
        return new_val

    def recenter_view(self):
        self.target_yaw = 0.0
        self.target_pitch = 0.0
        self.target_roll = 0.0
        _, _, def_deg = self.get_fov_limits()
        self.target_fov = math.radians(def_deg)
        self.vel_yaw = 0.0
        self.vel_pitch = 0.0
        self.vel_roll = 0.0
        self.is_recentering = True

    def get_fov_degrees(self):
        return math.degrees(self.fov)

    def get_fov_limits(self):
        """Returns (min_deg, max_deg, default_deg) for current projection."""
        if self.projection_mode == self.PROJ_LITTLE_PLANET:
            return 45.0, 280.0, 220.0
        elif self.projection_mode == self.PROJ_FISHEYE:
            return 30.0, 260.0, 180.0
        elif self.projection_mode == self.PROJ_PANINI:
            return 25.0, 180.0, 100.0
        elif self.projection_mode == self.PROJ_SPHERICAL_360:
            return 25.0, 260.0, 90.0
        else: # Rectilinear
            return 20.0, 160.0, 90.0

    def set_fov_degrees(self, deg):
        min_deg, max_deg, _ = self.get_fov_limits()
        deg = max(min_deg, min(max_deg, float(deg)))
        self.fov = math.radians(deg)
        self.target_fov = self.fov
        self.is_recentering = False
        self.update()
        self._emit_camera_changed()

    def zoom_in(self, step=5.0):
        """Zooms in (decreases FOV angle)."""
        current_deg = math.degrees(self.fov)
        self.set_fov_degrees(current_deg - step)

    def zoom_out(self, step=5.0):
        """Zooms out (increases FOV angle)."""
        current_deg = math.degrees(self.fov)
        self.set_fov_degrees(current_deg + step)

    def reset_fov(self):
        """Resets FOV to default for current projection."""
        _, _, def_deg = self.get_fov_limits()
        self.set_fov_degrees(def_deg)

    def get_dome_fov_degrees(self):
        """Returns dome coverage angle in degrees (default 180.0°)."""
        return math.degrees(self.dome_fov)

    def set_dome_fov_degrees(self, deg):
        """Sets dome coverage angle (e.g. 180°, 190°, 200°, 220°, 240°, or custom)."""
        deg = max(90.0, min(360.0, float(deg)))
        self.dome_fov = math.radians(deg)
        self.update()

    def get_lens_model(self) -> int:
        """Returns lens projection model (0: Equirectangular Dome, 1: Circular Fisheye)."""
        return self.lens_model

    def set_lens_model(self, model: int):
        """Sets lens projection model (0: Equirectangular Dome, 1: Circular Fisheye / Canon RF 5.2mm)."""
        self.lens_model = 1 if int(model) == 1 else 0
        self.update()

    def _emit_camera_changed(self):
        self.camera_changed.emit(
            math.degrees(self.yaw),
            math.degrees(self.pitch),
            math.degrees(self.roll),
            math.degrees(self.fov)
        )

    def _on_anim_tick(self):
        needs_update = False

        if self.is_recentering:
            # Smooth exponential interpolation back to center
            lerp_speed = 0.15
            self.yaw += (self.target_yaw - self.yaw) * lerp_speed
            self.pitch += (self.target_pitch - self.pitch) * lerp_speed
            self.roll += (self.target_roll - self.roll) * lerp_speed
            self.fov += (self.target_fov - self.fov) * lerp_speed

            if (abs(self.yaw - self.target_yaw) < 0.001 and
                abs(self.pitch - self.target_pitch) < 0.001 and
                abs(self.roll - self.target_roll) < 0.001 and
                abs(self.fov - self.target_fov) < 0.001):
                self.yaw = self.target_yaw
                self.pitch = self.target_pitch
                self.roll = self.target_roll
                self.fov = self.target_fov
                self.is_recentering = False

            needs_update = True
            self._emit_camera_changed()

        elif not self.is_dragging_left and not self.is_dragging_right:
            # Inertia decay
            if abs(self.vel_yaw) > 0.0001 or abs(self.vel_pitch) > 0.0001 or abs(self.vel_roll) > 0.0001:
                self.yaw += self.vel_yaw
                self.pitch += self.vel_pitch
                self.roll += self.vel_roll
                
                # Pitch clamp to avoid pole flipping
                max_pitch = math.pi * 0.49
                self.pitch = max(-max_pitch, min(max_pitch, self.pitch))

                self.vel_yaw *= 0.90
                self.vel_pitch *= 0.90
                self.vel_roll *= 0.90
                needs_update = True
                self._emit_camera_changed()

        if self.auto_orbit and not self.is_dragging_left:
            self.yaw += 0.0035
            needs_update = True
            self._emit_camera_changed()

        if needs_update:
            self.update()

    def mousePressEvent(self, event):
        win = self.window()
        # Si el menú contextual u overlay está visible y el clic fue fuera, cerrarlo
        if hasattr(win, 'overlay_menu') and win.overlay_menu.isVisible():
            click_pt = event.position().toPoint()
            if not win.overlay_menu.geometry().contains(click_pt):
                win.overlay_menu.hide()
                event.accept()
                return

        if event.button() == Qt.LeftButton:
            self.is_dragging_left = True
            self.last_mouse_pos = event.position()
            self.vel_yaw = 0.0
            self.vel_pitch = 0.0
            self.is_recentering = False
            self.setCursor(Qt.ClosedHandCursor)
        elif event.button() == Qt.RightButton:
            self.is_dragging_right = True
            self.right_dragged = False
            self.right_menu_opened = False
            self.last_mouse_pos = event.position()
            self.right_press_pos = event.position()
            self.vel_roll = 0.0
            self.is_recentering = False
            self.setCursor(Qt.SizeHorCursor)

    def mouseMoveEvent(self, event):
        pos = event.position()
        delta = pos - self.last_mouse_pos
        self.last_mouse_pos = pos

        # Control inteligente de la barra inferior: solo mostrar si el mouse está en la parte de abajo
        win = self.window()
        if hasattr(win, '_handle_mouse_move_hover'):
            win._handle_mouse_move_hover(pos.y())

        if self.is_dragging_left:
            # Sensitivity scaled by FOV
            fov_scale = math.tan(self.fov * 0.5)
            sens = 0.0035 * fov_scale

            # GoPro VR Player Inverted Axes navigation (Separated X and Y)
            sign_x = 1.0 if self.invert_x else -1.0
            sign_y = -1.0 if self.invert_y else 1.0

            d_yaw = sign_x * delta.x() * sens
            d_pitch = sign_y * delta.y() * sens

            self.yaw += d_yaw
            self.pitch += d_pitch

            # Clamp pitch
            max_pitch = math.pi * 0.49
            self.pitch = max(-max_pitch, min(max_pitch, self.pitch))

            # Store velocity for inertia
            self.vel_yaw = d_yaw * 0.7
            self.vel_pitch = d_pitch * 0.7

            self.update()
            self._emit_camera_changed()

        elif self.is_dragging_right:
            if hasattr(self, 'right_press_pos') and (pos - self.right_press_pos).manhattanLength() > 12:
                self.right_dragged = True
            # Right drag rotates roll angle
            sens_roll = 0.005
            d_roll = delta.x() * sens_roll
            self.roll += d_roll
            self.vel_roll = d_roll * 0.7
            self.update()
            self._emit_camera_changed()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging_left = False
            self.setCursor(Qt.ArrowCursor)
        elif event.button() == Qt.RightButton:
            self.is_dragging_right = False
            self.setCursor(Qt.ArrowCursor)
            if not getattr(self, 'right_dragged', False):
                self.right_menu_opened = True
                win = self.window()
                if not hasattr(win, 'show_context_menu') and hasattr(self.parent(), 'show_context_menu'):
                    win = self.parent()
                if hasattr(win, 'show_context_menu'):
                    win.show_context_menu(event.position().toPoint())
            self.right_dragged = False

    def contextMenuEvent(self, event):
        if not getattr(self, 'right_menu_opened', False) and not getattr(self, 'right_dragged', False):
            self.right_menu_opened = True
            win = self.window()
            if not hasattr(win, 'show_context_menu') and hasattr(self.parent(), 'show_context_menu'):
                win = self.parent()
            if hasattr(win, 'show_context_menu'):
                pt = event.position().toPoint() if hasattr(event, 'position') else event.pos()
                win.show_context_menu(pt)
        event.accept()

    def wheelEvent(self, event):
        # Zoom / FOV adjustment
        num_degrees = event.angleDelta().y() / 8.0
        num_steps = num_degrees / 15.0

        min_deg, max_deg, _ = self.get_fov_limits()
        min_fov = math.radians(min_deg)
        max_fov = math.radians(max_deg)

        zoom_factor = 0.93 if num_steps > 0 else 1.07
        self.fov = max(min_fov, min(max_fov, self.fov * zoom_factor))
        self.target_fov = self.fov
        self.is_recentering = False
        self.update()
        self._emit_camera_changed()

    def mouseDoubleClickEvent(self, event):
        # Double click toggles fullscreen on parent window
        if event.button() == Qt.LeftButton:
            win = self.window()
            if hasattr(win, '_toggle_fullscreen'):
                win._toggle_fullscreen()
            elif win.isFullScreen():
                win.showNormal()
            else:
                win.showFullScreen()

    def resizeGL(self, w, h):
        GL.glViewport(0, 0, w, h)
        if self.quality_mode == self.QUALITY_ADAPTIVE:
            self._reallocate_fbo(w * 2, h * 2)

    def paintGL(self):
        # 1. Ask MPV to render the current video frame into our offscreen FBO
        if self.fbo:
            self.backend.render_frame_to_fbo(self.fbo, self.fbo_width, self.fbo_height, flip_y=False)

        # 2. Bind default framebuffer (the screen widget)
        target_fbo = self.defaultFramebufferObject()
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, target_fbo)
        GL.glViewport(0, 0, self.width(), self.height())
        GL.glClearColor(0.04, 0.05, 0.08, 1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        if not self.shader_prog or not self.fbo_texture:
            return

        # 3. Render screen quad with our VR multi-projection shader
        GL.glUseProgram(self.shader_prog)

        # Bind decoded video texture to texture unit 0
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.fbo_texture)
        GL.glUniform1i(GL.glGetUniformLocation(self.shader_prog, "u_video_texture"), 0)

        # Set uniforms
        GL.glUniform2f(
            GL.glGetUniformLocation(self.shader_prog, "u_resolution"),
            float(self.width()), float(self.height())
        )
        GL.glUniform1f(GL.glGetUniformLocation(self.shader_prog, "u_fov"), float(self.fov))
        GL.glUniform3f(
            GL.glGetUniformLocation(self.shader_prog, "u_rotation"),
            float(self.pitch), float(self.yaw), float(self.roll)
        )
        GL.glUniform1i(GL.glGetUniformLocation(self.shader_prog, "u_projection"), int(self.projection_mode))
        GL.glUniform1i(GL.glGetUniformLocation(self.shader_prog, "u_stereo_mode"), int(self.stereo_mode))
        GL.glUniform1i(GL.glGetUniformLocation(self.shader_prog, "u_flip_x"), int(self.flip_x))
        GL.glUniform1i(GL.glGetUniformLocation(self.shader_prog, "u_flip_y"), int(self.flip_y))
        GL.glUniform1f(GL.glGetUniformLocation(self.shader_prog, "u_dome_fov"), float(self.dome_fov))
        GL.glUniform1i(GL.glGetUniformLocation(self.shader_prog, "u_lens_model"), int(self.lens_model))

        # Draw full screen quad
        GL.glBindVertexArray(self.vao)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 6)
        GL.glBindVertexArray(0)
        GL.glUseProgram(0)

    def cleanup(self):
        self.makeCurrent()
        self.anim_timer.stop()
        if self.fbo:
            GL.glDeleteFramebuffers(1, [self.fbo])
            self.fbo = 0
        if self.fbo_texture:
            GL.glDeleteTextures([self.fbo_texture])
            self.fbo_texture = 0
        if self.vbo:
            GL.glDeleteBuffers(1, [self.vbo])
            self.vbo = 0
        if self.vao:
            GL.glDeleteVertexArrays(1, [self.vao])
            self.vao = 0
        if self.shader_prog:
            GL.glDeleteProgram(self.shader_prog)
            self.shader_prog = 0
