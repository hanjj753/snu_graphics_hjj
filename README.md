# Computer Graphics

## utils

### Blender에서 json export하기

```bash
'D:\Program Files\Blender Foundation\Blender 5.2\blender.exe' .\model\pigeon_blockout.blend --background --python ..\utils\export_blender_scene.py
```

### json 을 코드로 바꾸기

```bash
python ..\utils\generate_default_scene.py ..\HW1\model\pigeon_blockout.scene.json | Set-Clipboard
```