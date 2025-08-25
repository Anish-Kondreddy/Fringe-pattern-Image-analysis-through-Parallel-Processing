from moviepy.editor import VideoFileClip # type: ignore
import os

def extract_frames(movie, times, imgdir):
    if not os.path.exists(imgdir):
        os.makedirs(imgdir)

    clip = VideoFileClip(movie)
    for t in times:
        imgpath = os.path.join(imgdir, '{}.png'.format(int(t*clip.fps)))
        clip.save_frame(imgpath, t)

movie = 'movie.mov'
imgdir = './pngs'
clip = VideoFileClip(movie)
times = [i/clip.fps for i in range(int(clip.fps * clip.duration))]

extract_frames(movie, times, imgdir)