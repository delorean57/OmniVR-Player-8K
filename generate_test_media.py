import os
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FFMPEG_BIN = os.path.join(BASE_DIR, 'ffmpeg.exe') if os.path.exists(os.path.join(BASE_DIR, 'ffmpeg.exe')) else 'ffmpeg'


def create_vr360_8k_pattern(output_path="test_vr360_8k.mp4", duration_sec=5, fps=60):
    print(f"Generating 8K 360 test video: {output_path} ({duration_sec}s @ {fps}fps)...")
    width, height = 7680, 3840
    
    # Pre-render base background image
    base_img = Image.new('RGB', (width, height), color=(15, 20, 30))
    draw = ImageDraw.Draw(base_img)
    
    # Try loading a system font or default
    try:
        font_large = ImageFont.truetype("arial.ttf", 160)
        font_med = ImageFont.truetype("arial.ttf", 90)
        font_small = ImageFont.truetype("arial.ttf", 55)
    except:
        font_large = ImageFont.load_default()
        font_med = font_large
        font_small = font_large
        
    # Draw sky gradient (top half) and ground gradient (bottom half)
    for y in range(0, height // 2, 40):
        intensity = int(30 + 120 * (1.0 - y / (height / 2)))
        draw.rectangle([0, y, width, y + 40], fill=(20, int(intensity * 0.7), intensity))
        
    for y in range(height // 2, height, 40):
        intensity = int(30 + 70 * ((y - height / 2) / (height / 2)))
        draw.rectangle([0, y, width, y + 40], fill=(int(intensity * 0.8), int(intensity * 0.6), 30))
        
    # Horizon line (Equator / Lat 0)
    horizon_y = height // 2
    draw.line([0, horizon_y, width, horizon_y], fill=(0, 255, 200), width=10)
    draw.text((width // 2 - 300, horizon_y - 120), "EQUATOR / HORIZON (0°)", fill=(0, 255, 200), font=font_med)
    
    # Latitudes (+60°, +30°, -30°, -60°)
    for lat_deg in [60, 30, -30, -60]:
        y = int(height * (0.5 - lat_deg / 180.0))
        color = (100, 200, 255) if lat_deg > 0 else (255, 200, 100)
        draw.line([0, y, width, y], fill=color, width=4)
        draw.text((80, y - 60), f"LATITUDE {lat_deg:+d}°", fill=color, font=font_small)
        draw.text((width - 600, y - 60), f"LATITUDE {lat_deg:+d}°", fill=color, font=font_small)
        
    # Cardinal directions (Longitudes: North=Center (0.5), East (0.75), South (0.0 & 1.0), West (0.25))
    directions = [
        (0.5, "NORTH (FRONT 0°)", (0, 255, 128)),
        (0.75, "EAST (RIGHT +90°)", (255, 180, 0)),
        (0.25, "WEST (LEFT -90°)", (255, 80, 80)),
        (0.0, "SOUTH (BACK -180°)", (180, 100, 255)),
        (1.0, "SOUTH (BACK +180°)", (180, 100, 255)),
    ]
    for norm_x, label, col in directions:
        x = int(norm_x * width)
        draw.line([x, 0, x, height], fill=col, width=6)
        draw.text((x - 300, horizon_y + 40), label, fill=col, font=font_med)
        
    # Zenith & Nadir
    draw.text((width // 2 - 350, 200), "ZENITH (SKY +90°)", fill=(255, 255, 255), font=font_large)
    draw.text((width // 2 - 400, height - 350), "NADIR (GROUND -90°)", fill=(200, 200, 200), font=font_large)
    
    # Specifications banner
    banner_text = "OMNIVR 8K GPU PLAYER - TEST PATTERN (7680x3840 @ 60 FPS)"
    draw.text((width // 2 - 1800, horizon_y + 250), banner_text, fill=(255, 255, 255), font=font_large)
    
    base_np = np.array(base_img)
    
    # Encode with ffmpeg hevc_nvenc
    cmd = [
        FFMPEG_BIN, '-y',
        '-f', 'rawvideo',
        '-vcodec', 'rawvideo',
        '-s', f'{width}x{height}',
        '-pix_fmt', 'rgb24',
        '-r', str(fps),
        '-i', '-',
        '-c:v', 'hevc_nvenc',
        '-preset', 'p4',
        '-pix_fmt', 'yuv420p',
        '-b:v', '40M',
        output_path
    ]
    
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    total_frames = duration_sec * fps
    
    for frame_idx in range(total_frames):
        # Add animated moving indicator along equator
        frame = base_np.copy()
        t = frame_idx / total_frames
        cx = int((t * width) % width)
        cy = horizon_y
        
        # Draw dynamic moving tracker
        # Draw directly in numpy: a green circle
        y_min = max(0, cy - 60)
        y_max = min(height, cy + 60)
        x_min = max(0, cx - 60)
        x_max = min(width, cx + 60)
        frame[y_min:y_max, x_min:x_max] = [0, 255, 255]
        
        proc.stdin.write(frame.tobytes())
        
    proc.stdin.close()
    proc.wait()
    print(f"Generated {output_path} successfully!")


def create_vr180_sbs_pattern(output_path="test_vr180_sbs.mp4", duration_sec=5, fps=60):
    print(f"Generating VR180 SBS test video: {output_path}...")
    width, height = 3840, 1920
    half_w = width // 2
    
    img = Image.new('RGB', (width, height), color=(20, 25, 35))
    draw = ImageDraw.Draw(img)
    
    try:
        font_large = ImageFont.truetype("arial.ttf", 90)
        font_med = ImageFont.truetype("arial.ttf", 55)
    except:
        font_large = ImageFont.load_default()
        font_med = font_large
        
    # Left Eye half (0 to half_w)
    draw.rectangle([0, 0, half_w, height], outline=(0, 200, 255), width=6)
    draw.text((half_w // 2 - 350, 150), "VR180 - LEFT EYE", fill=(0, 255, 255), font=font_large)
    draw.line([half_w // 2, 0, half_w // 2, height], fill=(0, 150, 255), width=3)
    draw.line([0, height // 2, half_w, height // 2], fill=(0, 150, 255), width=3)
    draw.ellipse([half_w // 2 - 350, height // 2 - 350, half_w // 2 + 350, height // 2 + 350], outline=(0, 255, 255), width=6)
    draw.text((half_w // 2 - 150, height // 2 - 30), "CENTER 0°", fill=(0, 255, 255), font=font_med)
    # 3D target with horizontal parallax (-40px for left eye)
    draw.ellipse([half_w // 2 - 40 - 80, height // 2 + 150 - 80, half_w // 2 - 40 + 80, height // 2 + 150 + 80], fill=(255, 50, 50))
    
    # Right Eye half (half_w to width)
    draw.rectangle([half_w, 0, width, height], outline=(255, 100, 200), width=6)
    draw.text((half_w + half_w // 2 - 380, 150), "VR180 - RIGHT EYE", fill=(255, 100, 200), font=font_large)
    draw.line([half_w + half_w // 2, 0, half_w + half_w // 2, height], fill=(255, 80, 150), width=3)
    draw.line([half_w, height // 2, width, height // 2], fill=(255, 80, 150), width=3)
    draw.ellipse([half_w + half_w // 2 - 350, height // 2 - 350, half_w + half_w // 2 + 350, height // 2 + 350], outline=(255, 100, 200), width=6)
    draw.text((half_w + half_w // 2 - 150, height // 2 - 30), "CENTER 0°", fill=(255, 100, 200), font=font_med)
    # 3D target with horizontal parallax (+40px for right eye)
    draw.ellipse([half_w + half_w // 2 + 40 - 80, height // 2 + 150 - 80, half_w + half_w // 2 + 40 + 80, height // 2 + 150 + 80], fill=(50, 100, 255))
    
    base_np = np.array(img)
    
    cmd = [
        FFMPEG_BIN, '-y',
        '-f', 'rawvideo',
        '-vcodec', 'rawvideo',
        '-s', f'{width}x{height}',
        '-pix_fmt', 'rgb24',
        '-r', str(fps),
        '-i', '-',
        '-c:v', 'hevc_nvenc',
        '-preset', 'p4',
        '-pix_fmt', 'yuv420p',
        '-b:v', '20M',
        output_path
    ]
    
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    total_frames = duration_sec * fps
    
    for frame_idx in range(total_frames):
        proc.stdin.write(base_np.tobytes())
        
    proc.stdin.close()
    proc.wait()
    print(f"Generated {output_path} successfully!")


def create_vr190_sbs_pattern(output_path="test_vr190_sbs.mp4", duration_sec=4, fps=60):
    print(f"Generating VR190 SBS test video: {output_path}...")
    width, height = 3840, 1920
    half_w = width // 2
    
    img = Image.new('RGB', (width, height), color=(18, 22, 32))
    draw = ImageDraw.Draw(img)
    
    try:
        font_large = ImageFont.truetype("arial.ttf", 80)
        font_med = ImageFont.truetype("arial.ttf", 50)
        font_small = ImageFont.truetype("arial.ttf", 36)
    except:
        font_large = ImageFont.load_default()
        font_med = font_large
        font_small = font_large
        
    for side, offset, col_primary, col_accent, eye_label, parallax in [
        ("left", 0, (0, 210, 255), (0, 140, 255), "VR 190° SBS — LEFT EYE", -40),
        ("right", half_w, (255, 90, 190), (255, 60, 140), "VR 190° SBS — RIGHT EYE", +40)
    ]:
        cx = offset + half_w // 2
        cy = height // 2
        
        # Border
        draw.rectangle([offset, 0, offset + half_w, height], outline=col_primary, width=6)
        
        # Header banner
        draw.text((cx - 400, 120), eye_label, fill=col_primary, font=font_large)
        draw.text((cx - 360, 210), "CANON RF 5.2mm / 190° WIDE DOME SBS", fill=(200, 220, 240), font=font_small)
        
        # Center crosshair
        draw.line([cx, 0, cx, height], fill=col_accent, width=2)
        draw.line([offset, cy, offset + half_w, cy], fill=col_accent, width=2)
        
        # 190° Dome concentric rings: 30°, 60°, 90°, 95° (Outer Edge)
        for deg, r_px, label, col_ring in [
            (30, int(half_w * 0.16), "30°", (100, 140, 180)),
            (60, int(half_w * 0.32), "60°", (130, 180, 220)),
            (90, int(half_w * 0.47), "90° (180° Limit)", (255, 200, 80)),
            (95, int(half_w * 0.495), "95° (190° Canon Limit)", col_primary)
        ]:
            draw.ellipse([cx - r_px, cy - r_px, cx + r_px, cy + r_px], outline=col_ring, width=3 if deg < 90 else 5)
            draw.text((cx + r_px - 80, cy - 30), label, fill=col_ring, font=font_small)
            
        draw.text((cx - 150, cy - 25), "CENTER 0°", fill=col_primary, font=font_med)
        
        # 3D stereoscopic target object with horizontal parallax
        draw.ellipse([cx + parallax - 70, cy + 180 - 70, cx + parallax + 70, cy + 180 + 70], fill=(255, 230, 0) if side == 'left' else (0, 255, 180))
        draw.text((cx + parallax - 55, cy + 180 - 15), "3D OBJ", fill=(0, 0, 0), font=font_small)

    base_np = np.array(img)
    
    cmd = [
        FFMPEG_BIN, '-y',
        '-f', 'rawvideo',
        '-vcodec', 'rawvideo',
        '-s', f'{width}x{height}',
        '-pix_fmt', 'rgb24',
        '-r', str(fps),
        '-i', '-',
        '-c:v', 'hevc_nvenc',
        '-preset', 'p4',
        '-pix_fmt', 'yuv420p',
        '-b:v', '20M',
        output_path
    ]
    
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    total_frames = duration_sec * fps
    
    for _ in range(total_frames):
        proc.stdin.write(base_np.tobytes())
        
    proc.stdin.close()
    proc.wait()
    print(f"Generated {output_path} successfully!")


if __name__ == '__main__':
    create_vr180_sbs_pattern()
    create_vr190_sbs_pattern()
    create_vr360_8k_pattern(duration_sec=3)
