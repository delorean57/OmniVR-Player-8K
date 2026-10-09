"""
VR Projection Shaders for OmniVR Player (GoPro VR Player Modern 8K)
Provides mathematically exact GLSL shaders for:
- Rectilinear (standard perspective)
- Panini (cylindrical wide-angle with vertical line preservation)
- Fisheye (equidistant hemispherical)
- Little Planet (stereographic downward projection)
- Spherical 360 (equirectangular panorama map)
- Stereoscopic 3D:
  - VR180 Side-by-Side (Left, Right, Dual Split, Anaglyph Red-Cyan)
  - 360 Side-by-Side (Left, Right, Dual Split, Anaglyph Red-Cyan)
  - 360 Over-Under (Top, Bottom, Dual Split, Anaglyph Red-Cyan)
"""

VERTEX_SHADER = """
#version 330 core
layout(location = 0) in vec2 a_pos;
layout(location = 1) in vec2 a_texcoord;

out vec2 v_texcoord;

void main() {
    v_texcoord = a_texcoord;
    gl_Position = vec4(a_pos, 0.0, 1.0);
}
"""

FRAGMENT_SHADER = """
#version 330 core
in vec2 v_texcoord;
out vec4 fragColor;

uniform sampler2D u_video_texture;
uniform vec2 u_resolution;
uniform float u_fov;            // Field of view in radians
uniform vec3 u_rotation;       // pitch, yaw, roll in radians
uniform int u_projection;      // 0: Rectilinear, 1: Panini, 2: Fisheye, 3: Little Planet, 4: Spherical 360
uniform int u_stereo_mode;     // 0: Mono 2D,
                               // 1: VR180 SBS Left, 2: VR180 SBS Right, 3: VR180 SBS Dual, 4: VR180 SBS Anaglyph,
                               // 5: 360 SBS Left, 6: 360 SBS Right, 7: 360 SBS Dual, 8: 360 SBS Anaglyph,
                               // 9: 360 OU Top, 10: 360 OU Bottom, 11: 360 OU Dual, 12: 360 OU Anaglyph
uniform int u_flip_x;          // 0 or 1
uniform int u_flip_y;          // 0 or 1
uniform float u_dome_fov;      // Dome coverage angle in radians (180°, 190°, 200°, 220°, 240°, or custom)
uniform int u_lens_model;      // 0: Equirectangular Dome, 1: Circular Fisheye (Canon RF 5.2mm / Dual Fisheye)

const float PI = 3.14159265358979323846;
const float TWO_PI = 6.28318530717958647692;

mat3 getRotationMatrix(vec3 r) {
    // r.x = pitch, r.y = yaw, r.z = roll
    float cp = cos(r.x); float sp = sin(r.x);
    float cy = cos(r.y); float sy = sin(r.y);
    float cr = cos(r.z); float sr = sin(r.z);

    mat3 Rx = mat3(
        1.0, 0.0, 0.0,
        0.0, cp, -sp,
        0.0, sp, cp
    );
    mat3 Ry = mat3(
        cy, 0.0, sy,
        0.0, 1.0, 0.0,
        -sy, 0.0, cy
    );
    mat3 Rz = mat3(
        cr, -sr, 0.0,
        sr, cr, 0.0,
        0.0, 0.0, 1.0
    );
    return Ry * Rx * Rz;
}

vec2 rayToEquirectangular(vec3 dir) {
    float lon = atan(dir.x, dir.z);
    float lat = asin(clamp(dir.y, -1.0, 1.0));
    float u = lon / TWO_PI + 0.5;
    float v = 0.5 - lat / PI;
    return vec2(fract(u), clamp(v, 0.0, 1.0));
}

vec2 rayToDome(vec3 dir, float dome_fov) {
    float half_fov = dome_fov * 0.5;
    float theta = acos(clamp(dir.z, -1.0, 1.0));

    if (u_lens_model == 1) {
        // Modelo Ojo de Pez Circular (Canon RF 5.2mm Dual Fisheye / equidistant circular fisheye)
        if (theta > half_fov) {
            return vec2(-1.0, -1.0); // Fuera de cobertura óptica
        }
        float sin_t = sin(theta);
        float r = (half_fov > 0.0001) ? (theta / half_fov) : 0.0;
        vec2 xy_dir = (sin_t > 0.0001) ? (dir.xy / sin_t) : vec2(0.0);
        vec2 circle_uv = xy_dir * r;
        float u = 0.5 + 0.5 * circle_uv.x;
        float v = 0.5 - 0.5 * circle_uv.y;
        if (u < 0.0 || u > 1.0 || v < 0.0 || v > 1.0) {
            return vec2(-1.0, -1.0);
        }
        return vec2(u, v);
    } else {
        // Modelo Equirrectangular Domo (VR180 / VR190 Equirectangular)
        if (theta > half_fov + 0.005) {
            return vec2(-1.0, -1.0); // Fuera de cobertura del domo frontal
        }
        float safe_z = max(dir.z, 0.0001);
        float lon = atan(dir.x, safe_z);
        float lat = asin(clamp(dir.y, -1.0, 1.0));
        float u = lon / dome_fov + 0.5;
        float v = 0.5 - lat / dome_fov;
        if (u < 0.0 || u > 1.0 || v < 0.0 || v > 1.0) {
            return vec2(-1.0, -1.0);
        }
        return vec2(u, v);
    }
}

vec3 computeRayDir(vec2 ndc, int proj, float fov) {
    vec3 ray = vec3(0.0, 0.0, 1.0);
    if (proj == 0) {
        // Rectilinear (Perspective)
        float tanFov = tan(fov * 0.5);
        ray = normalize(vec3(ndc.x * tanFov, ndc.y * tanFov, 1.0));
    } else if (proj == 1) {
        // Panini (Vedutismo / Cylindrical straight verticals)
        float d = 1.0;
        float tanFov = tan(fov * 0.5);
        float s = ndc.x * tanFov;
        float phi = 2.0 * atan(s / (d + 1.0));
        float y = ndc.y * tanFov * (d + cos(phi)) / (d + 1.0);
        ray = normalize(vec3(sin(phi), y, cos(phi)));
    } else if (proj == 2) {
        // Fisheye (Hemispherical / Equidistant)
        float r = length(ndc);
        float theta = r * (fov * 0.5);
        vec2 n = (r > 0.0001) ? (ndc / r) : vec2(0.0);
        ray = normalize(vec3(n.x * sin(theta), n.y * sin(theta), cos(theta)));
    } else if (proj == 3) {
        // Little Planet (Stereographic projection looking at Nadir)
        float r = length(ndc);
        float theta = 2.0 * atan(r * tan(fov * 0.25));
        vec2 n = (r > 0.0001) ? (ndc / r) : vec2(0.0);
        ray = normalize(vec3(n.x * sin(theta), -cos(theta), n.y * sin(theta)));
    } else {
        // Default flat
        ray = vec3(ndc.x, ndc.y, 1.0);
    }
    return ray;
}

vec4 sampleVideo(vec2 sphere_uv, int eye_channel, bool is_180) {
    if (sphere_uv.x < 0.0) {
        // Dark background outside 180° dome
        return vec4(0.04, 0.06, 0.09, 1.0);
    }
    vec2 tex_uv = sphere_uv;
    
    if (u_flip_x == 1) {
        tex_uv.x = 1.0 - tex_uv.x;
    }
    if (u_flip_y == 1) {
        tex_uv.y = 1.0 - tex_uv.y;
    }
    
    if (is_180) {
        // VR180 Side by Side
        if (eye_channel == 0) {
            tex_uv.x = tex_uv.x * 0.5;
        } else {
            tex_uv.x = 0.5 + tex_uv.x * 0.5;
        }
    } else if (u_stereo_mode >= 5 && u_stereo_mode <= 8) {
        // 360 Side by Side
        if (eye_channel == 0) {
            tex_uv.x = tex_uv.x * 0.5;
        } else {
            tex_uv.x = 0.5 + tex_uv.x * 0.5;
        }
    } else if (u_stereo_mode >= 9 && u_stereo_mode <= 12) {
        // 360 Over Under
        if (eye_channel == 0) {
            tex_uv.y = tex_uv.y * 0.5;
        } else {
            tex_uv.y = 0.5 + tex_uv.y * 0.5;
        }
    }
    
    return texture(u_video_texture, tex_uv);
}

void main() {
    float aspect = u_resolution.x / u_resolution.y;
    mat3 R = getRotationMatrix(u_rotation);
    bool is_180 = (u_stereo_mode >= 1 && u_stereo_mode <= 4);
    
    bool is_dual = (u_stereo_mode == 3 || u_stereo_mode == 7 || u_stereo_mode == 11);
    bool is_dual_inv = (u_stereo_mode == 4 || u_stereo_mode == 8 || u_stereo_mode == 12);
    
    if (is_dual || is_dual_inv) {
        // Dual view: Left eye on left half of screen, Right eye on right half
        int eye = (v_texcoord.x < 0.5) ? 0 : 1;
        if (is_dual_inv) {
            eye = 1 - eye; // Inverted eye stereo (swapped)
        }
        float sub_x = (v_texcoord.x < 0.5) ? (v_texcoord.x * 2.0) : ((v_texcoord.x - 0.5) * 2.0);
        vec2 sub_ndc = vec2(sub_x * 2.0 - 1.0, v_texcoord.y * 2.0 - 1.0);
        sub_ndc.x *= (aspect * 0.5);
        
        vec3 ray = computeRayDir(sub_ndc, u_projection, u_fov);
        vec3 world_dir = R * ray;
        vec2 sphere_uv = is_180 ? rayToDome(world_dir, u_dome_fov) : rayToEquirectangular(world_dir);
        fragColor = sampleVideo(sphere_uv, eye, is_180);
        
        // Draw subtle separator line between views
        if (abs(v_texcoord.x - 0.5) < 0.0015) {
            fragColor = vec4(0.2, 0.7, 1.0, 1.0);
        }
        return;
    }
    
    vec2 ndc = vec2(v_texcoord.x * 2.0 - 1.0, v_texcoord.y * 2.0 - 1.0);
    ndc.x *= aspect;
    
    if (u_projection == 4) {
        // Spherical 360 direct panorama view
        float u = fract(-ndc.x * 0.25 * (u_fov / PI) - u_rotation.y / TWO_PI + 0.5);
        float v = clamp(-ndc.y * 0.5 * (u_fov / PI) + 0.5 - u_rotation.x / PI, 0.0, 1.0);
        int eye = (u_stereo_mode == 2 || u_stereo_mode == 6 || u_stereo_mode == 10) ? 1 : 0;
        fragColor = sampleVideo(vec2(u, v), eye, is_180);
        return;
    }
    
    vec3 ray = computeRayDir(ndc, u_projection, u_fov);
    vec3 world_dir = R * ray;
    vec2 sphere_uv = is_180 ? rayToDome(world_dir, u_dome_fov) : rayToEquirectangular(world_dir);
    
    int eye = (u_stereo_mode == 2 || u_stereo_mode == 6 || u_stereo_mode == 10) ? 1 : 0;
    fragColor = sampleVideo(sphere_uv, eye, is_180);
}
"""
