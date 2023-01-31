import setup_python_blender

IS_TEST = False
SCALE = 1/2.5
if not IS_TEST:
    import bpy
    setup_python_blender.install_packages(["pandas", "math", "random", "numpy", "datetime"])


if not IS_TEST:
    # Update text labels:
    scene = bpy.context.scene
    text_t1 = scene.objects['Text Trimester 1']
    text_t2 = scene.objects['Text Trimester 2']
    text_t3 = scene.objects['Text Trimester 3']
    bar_t1 = scene.objects['Bar Trimester 1']
    bar_t2 = scene.objects['Bar Trimester 2']
    bar_t3 = scene.objects['Bar Trimester 3']

    def recalculate_text(scene):
        if scene.frame_current >= 500:
            # text_t2.data.body = '0.972'
            text_t1.data.body = str(round(bar_t1.scale[1]*SCALE, 3))
            text_t2.data.body = str(round(bar_t2.scale[1]*SCALE, 3))
            text_t3.data.body = str(round(bar_t3.scale[1]*SCALE, 3))
        else:
            text_t1.data.body = ''
            text_t2.data.body = ''
            text_t3.data.body = ''
    bpy.app.handlers.frame_change_pre.append(recalculate_text)
print("END")