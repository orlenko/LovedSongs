import Image
import ImageEnhance
import os


SIZE = (1280, 720) # High-def YouTube size


def zoom(image, factor):
    size = image.size
    size = (int(round(size[0] * factor)), int(round(size[1] * factor)))
    return image.resize(size, Image.ANTIALIAS)


def crop(image, box):
    cropped = image.transform((box[2] - box[0], box[3] - box[1]), Image.EXTENT, box)
    return cropped


def normalize_size(image, view_size):
    print 'Normalizing %s to %s' % (image.size, view_size)
    x_factor = float(view_size[0]) / image.size[0]
    y_factor = float(view_size[1]) / image.size[1]
    print 'X factor: %s, Y factor: %s' % (x_factor, y_factor)
    min_factor = min(x_factor, y_factor)

    # Make the image fit the view size
    norm_image = zoom(image, min_factor)

    # Do I need to pad the image so that it has the right aspect ratio?
    if x_factor != y_factor:
        new_norm = Image.new('RGBA', (view_size[0], view_size[1]),
            (0,0,0,1))
        if x_factor < y_factor:
            print 'Adding padding at top and bottom'
            new_norm.paste(norm_image, (0, (view_size[1] - norm_image.size[1]) /2))
        elif y_factor < x_factor:
            print 'Adding padding at left and right'
            new_norm.paste(norm_image, ((view_size[0] - norm_image.size[0]) /2, 0))
        norm_image = new_norm
    return norm_image


def pan_zoom(image, view_size, out_dir, pan_vector, start_small):
    assert pan_vector in ((0,0), (0,1), (0,-1), (1,0), (1,1), (1,-1), (-1,0), (-1,1),
            (-1,-1))
    assert os.path.isdir(out_dir)

    normalized = normalize_size(image, (int(round(view_size[0] * 2)), 
        int(round(view_size[1] * 2))))
    normalized.save('normalized.png')
    
    steps = 300
    pan_speed = 0.8
    max_pan = ((view_size[0] / 2.0 + view_size[0] / 2.0 * pan_vector[0] * pan_speed), 
                (view_size[1] / 2.0 + view_size[1] / 2.0 * pan_vector[1] * pan_speed))
    if start_small:
        initial_zoom = 0.5
        final_zoom = 1
        initial_pan = (0, 0)
        final_pan = max_pan
    else:
        initial_zoom = 1
        final_zoom = 0.5
        initial_pan = max_pan
        final_pan = (0, 0)
    zoom_step = (final_zoom - initial_zoom) / steps
    pan_step = ((final_pan[0] - initial_pan[0]) / steps, 
            (final_pan[1] - initial_pan[1]) / steps)
    zoom_factor = initial_zoom
    pan_offset = initial_pan
    ir = lambda x: int(round(x))
    for i in range(steps):
        pan_rect = (ir(pan_offset[0]), ir(pan_offset[1]),
            ir(view_size[0] + pan_offset[0]), ir(view_size[1] + pan_offset[1]))
        zoomed = zoom(normalized, zoom_factor)
        zoomed.save('zoomed%03d.png' % i)
        print 'Step %s: zoom %s, pan %s, from image %s' % (i, zoom_factor, pan_rect,
                zoomed.size)
        img = crop(zoomed, pan_rect)
        img.save('cropped%03d.png' % i)
        fname = os.path.join(out_dir, 'step%03d.png' % i)
        img.save(fname)
        zoom_factor += zoom_step
        pan_offset = (pan_offset[0] + pan_step[0], pan_offset[1] + pan_step[1])


''' ffmpeg command:
ffmpeg.exe -r 10 -f image2 -i C:\dev\lovedsongs\images\pz\step%03d.png -qscale 2 -g 1000 -r 25 -vframes 6000 -y C:\dev\lovedsongs\images\pz\clip.mpg
'''


